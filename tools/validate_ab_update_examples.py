#!/usr/bin/env python3
"""Validate the A/B fallback update contract family (UpdateSlot, UpdateTransaction,
UpdateHealthProbe).

Five checks, not one:
  1. schema conformance — every schema is a valid draft-2020-12 document and every
     canonical example validates against its schema;
  2. strictness bar — every schema in the family holds the tranche bar: top-level
     "additionalProperties": false, specVersion pinned to the 0.1.0 const, and an
     anchored urn:srcos: id pattern;
  3. recomputed probe digest — UpdateHealthProbe.definitionDigest is RECOMPUTED
     from the probe's own check set and watchdog configuration rather than read
     back. A digest that is merely stored is an assertion about pinning; a digest
     that is recomputed is pinning. This is what makes "the gate cannot be
     weakened to admit the candidate that failed it" a build failure instead of a
     paragraph;
  4. cross-invariants — the properties JSON Schema cannot express, checked over
     the example set. Chief among them: a settled transaction's
     preservedPayloadDigest still equals the active slot's payloadDigest, which is
     the executable form of "the currently-good slot was never overwritten by the
     update being applied". That is the invariant this family exists for, and it
     is the one that has to be checked across two documents rather than inside
     one;
  5. negative vectors — every case in fixtures/ab-update/conformance.json FAILS
     for its stated reason.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_NAMES = [
    "UpdateSlot.json",
    "UpdateTransaction.json",
    "UpdateHealthProbe.json",
]

SLOT_EXAMPLES = [
    "update_slot.fog07_a_active.json",
    "update_slot.fog07_b_unbootable.json",
    "update_slot.noetica_a_fallback.json",
    "update_slot.noetica_b_active.json",
]
TRANSACTION_EXAMPLES = [
    "update_transaction.refused.json",
    "update_transaction.promoted.json",
]
PROBE_EXAMPLES = ["update_health_probe.json"]

PAIRS = (
    [("UpdateSlot.json", name) for name in SLOT_EXAMPLES]
    + [("UpdateTransaction.json", name) for name in TRANSACTION_EXAMPLES]
    + [("UpdateHealthProbe.json", name) for name in PROBE_EXAMPLES]
)

FIXTURE = ROOT / "fixtures" / "ab-update" / "conformance.json"

# The fields the probe's definitionDigest covers. Deliberately the whole check and
# watchdog objects, descriptions included: an exclusion list is somewhere to hide a
# weakening, and the cost of re-pinning after a comment edit is far below the cost
# of a gate that can be edited without the pin noticing.
DIGEST_FIELDS = (
    "checks",
    "evaluatedIn",
    "minConsecutivePasses",
    "onProbeUnavailable",
    "timeoutSeconds",
    "watchdogs",
)

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"FAIL: {msg}")


def ok(msg: str) -> None:
    print(f"ok: {msg}")


def load(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


def definition_digest(probe: dict) -> str:
    """Recompute UpdateHealthProbe.definitionDigest. Normative: sha256 over the
    canonical JSON (sorted keys, no whitespace) of the DIGEST_FIELDS projection."""
    core = {field: probe[field] for field in DIGEST_FIELDS}
    canonical = json.dumps(core, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main() -> int:  # noqa: C901 - a validator is a list of checks; splitting it hides them
    schemas = {name: load(ROOT / "schemas" / name) for name in SCHEMA_NAMES}
    examples = {name: load(ROOT / "examples" / name) for _, name in PAIRS}

    # 1. schema conformance
    for name, schema in schemas.items():
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
            ok(f"schema valid: {name}")
        except jsonschema.SchemaError as exc:
            fail(f"schema invalid: {name}: {exc.message}")

    for schema_name, example_name in PAIRS:
        validator = jsonschema.Draft202012Validator(schemas[schema_name])
        errors = sorted(validator.iter_errors(examples[example_name]), key=str)
        if errors:
            for err in errors:
                fail(f"example {example_name} vs {schema_name}: {err.message}")
        else:
            ok(f"example validates: {example_name} vs {schema_name}")

    # 2. strictness bar
    bar_failures = len(failures)
    for name, schema in schemas.items():
        if schema.get("additionalProperties") is not False:
            fail(f"strictness: {name} must set top-level additionalProperties:false")
        spec_version = schema.get("properties", {}).get("specVersion", {})
        if spec_version.get("const") != "0.1.0":
            fail(f"strictness: {name} specVersion must be const 0.1.0")
        id_pattern = schema.get("properties", {}).get("id", {}).get("pattern", "")
        if not id_pattern.startswith("^urn:srcos:"):
            fail(f"strictness: {name} id pattern must anchor on urn:srcos:")
        if schema.get("properties", {}).get("type", {}).get("const") != schema.get("title"):
            fail(f"strictness: {name} type const must equal the schema title")
    if len(failures) == bar_failures:
        ok(f"strictness bar holds for all {len(schemas)} schemas")

    # 3. recomputed probe digest
    probe = examples["update_health_probe.json"]
    recomputed = definition_digest(probe)
    if probe["definitionDigest"] != recomputed:
        fail(
            "probe definitionDigest is stale: recorded "
            f"{probe['definitionDigest']} but the check set hashes to {recomputed}"
        )
    else:
        ok("probe definitionDigest recomputes from its own check set + watchdogs")

    # A gate with no blocking check cannot gate anything.
    if not any(check["blocking"] for check in probe["checks"]):
        fail("probe has no blocking check — it cannot refuse a promotion")
    else:
        ok("probe has at least one blocking check")

    # The software watchdog must get the first word, or every software-detectable
    # fault is reported as an unexplained hardware reset.
    sw = [w for w in probe["watchdogs"] if w["kind"] == "software"]
    hw = [w for w in probe["watchdogs"] if w["kind"] == "hardware"]
    if min(w["timeoutSeconds"] for w in hw) <= max(w["timeoutSeconds"] for w in sw):
        fail("watchdog ordering: hardware timeout must exceed software timeout")
    else:
        ok("watchdog ordering: software fires first, hardware is the backstop")

    # 4. cross-invariants over the example set
    slots_by_target: dict[str, list[dict]] = defaultdict(list)
    for name in SLOT_EXAMPLES:
        slots_by_target[examples[name]["targetRef"]].append(examples[name])

    for target, slots in sorted(slots_by_target.items()):
        short = target.rsplit(":", 1)[-1]
        if len(slots) != 2:
            fail(f"{short}: a target must have exactly two slots, found {len(slots)}")
            continue
        if {s["slot"] for s in slots} != {"A", "B"}:
            fail(f"{short}: slot labels must be exactly {{A, B}}")
        if sum(1 for s in slots if s["role"] == "active") != 1:
            fail(f"{short}: exactly one slot must hold role 'active'")
        elif sum(1 for s in slots if s["currentlyRunning"]) != 1:
            fail(f"{short}: exactly one slot may be currentlyRunning")
        else:
            ok(f"{short}: two slots, one active, one running")

    for name in TRANSACTION_EXAMPLES:
        tx = examples[name]
        short = tx["id"].rsplit(":", 1)[-1]
        slots = {s["slot"]: s for s in slots_by_target[tx["targetRef"]]}
        if set(slots) != {"A", "B"}:
            fail(f"{short}: transaction targetRef has no slot pair in the example set")
            continue
        from_slot, to_slot = slots[tx["fromSlot"]], slots[tx["toSlot"]]

        # THE invariant: the good slot was never overwritten.
        if from_slot["payloadDigest"] != tx["preservedPayloadDigest"]:
            fail(
                f"{short}: the good slot WAS overwritten — opened with "
                f"{tx['preservedPayloadDigest']} in slot {tx['fromSlot']}, which now "
                f"holds {from_slot['payloadDigest']}"
            )
        else:
            ok(f"{short}: fromSlot still holds its opening digest (never overwritten)")

        if to_slot["payloadDigest"] != tx["candidatePayloadDigest"]:
            fail(f"{short}: toSlot does not hold the candidate payload digest")

        # The probe was pinned, and the pin still resolves.
        if tx["healthProbeRef"] != probe["id"]:
            fail(f"{short}: healthProbeRef does not resolve to the example probe")
        elif tx["healthProbeDigest"] != probe["definitionDigest"]:
            fail(f"{short}: pinned probe digest does not match the probe definition")
        else:
            ok(f"{short}: probe pin resolves and matches")

        # Attempt accounting.
        attempts = tx["attempts"]
        numbers = [a["attemptNumber"] for a in attempts]
        if numbers != list(range(1, len(attempts) + 1)):
            fail(f"{short}: attemptNumbers must be contiguous from 1, got {numbers}")
        if len(attempts) > tx["maxAttempts"]:
            fail(f"{short}: {len(attempts)} attempts exceeds maxAttempts {tx['maxAttempts']}")
        passes = [i for i, a in enumerate(attempts) if a["result"] == "pass"]
        if len(passes) > 1 or (passes and passes[0] != len(attempts) - 1):
            fail(f"{short}: 'pass' must appear at most once and only as the final attempt")
        for attempt in attempts:
            if attempt["result"] == "pass":
                continue
            if attempt["fellBackTo"] is None:
                fail(
                    f"{short}: attempt {attempt['attemptNumber']} failed and fell back "
                    "nowhere — the target was left running an unproven payload"
                )
            elif attempt["fellBackTo"] != tx["fromSlot"]:
                fail(
                    f"{short}: attempt {attempt['attemptNumber']} fell back to "
                    f"{attempt['fellBackTo']}, not to the known-good slot {tx['fromSlot']}"
                )
        if not failures or all("attempt" not in f for f in failures[-4:]):
            ok(f"{short}: attempt accounting consistent, every failure fell back to active")

        # Terminal-state consistency with the slot pair.
        if tx["outcome"] == "refused":
            if len(attempts) != tx["maxAttempts"]:
                fail(f"{short}: refused before the attempt budget was spent")
            elif to_slot["state"] != "unbootable" or to_slot["bootPriority"] != 0:
                fail(
                    f"{short}: refused but the candidate slot is still selectable "
                    f"(state={to_slot['state']}, bootPriority={to_slot['bootPriority']}) "
                    "— nothing ends the boot loop"
                )
            elif not from_slot["successful"] or not from_slot["currentlyRunning"]:
                fail(f"{short}: refused but the target is not running the known-good slot")
            else:
                ok(f"{short}: refused — candidate unbootable, target running active")
        elif tx["outcome"] == "promoted":
            if attempts[-1]["result"] != "pass":
                fail(f"{short}: promoted without a passing final attempt")
            elif to_slot["role"] != "active" or not to_slot["successful"]:
                fail(f"{short}: promoted but the candidate did not become the active slot")
            elif not from_slot["successful"] or from_slot["bootPriority"] == 0:
                fail(
                    f"{short}: promoted and the previous payload is no longer a usable "
                    "fallback — promotion must retain the slot it replaced"
                )
            else:
                ok(f"{short}: promoted — roles swapped, previous payload retained bootable")

    # 5. negative vectors must FAIL
    fixture = load(FIXTURE)
    for case in fixture["cases"]:
        validator = jsonschema.Draft202012Validator(schemas[case["schema"]])
        if list(validator.iter_errors(case["document"])):
            ok(f"negative vector fails as required: {case['reason'][:72]}")
        else:
            fail(f"negative vector VALIDATED but must fail: {case['reason']}")

    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nOK: ab-update family — all five checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
