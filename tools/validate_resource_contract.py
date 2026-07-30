#!/usr/bin/env python3
"""Validate ResourceContract: a limit must carry evidence it can refuse.

One string this schema exists to make unwritable: `Action taken: none`.

  INVARIANT 1  enforcement != observe requires `negativeControl`. A contract that claims it
               will act, with nothing demonstrating it can, is the never-fired-control defect.
               'It has never needed to' is the shape of every control that turns out not to
               work.

  INVARIANT 2  enforcement == observe requires `observeOnlyReason`, so an unenforced limit
               reads as a position someone took rather than an oversight. Both motivating
               macOS reports were effectively observe-only while presenting a `limit`.

  INVARIANT 3  scope == process requires `scopeRationale`. Per-process limits are defeated by
               fan-out: in the nsurlsessiond report the flagged process was 141 of 8,357
               samples (2%) while node/app/VM/git were 66% between them, all under one
               coalition, none tripping anything.

  INVARIANT 4  firedCount > 0 requires `lastFiredAt` — a count with no timestamp cannot be
               reconciled against a log.

  INVARIANT 5  (validator-only) `negativeControl` must RESOLVE. `format: uri-reference` is a
               syntax check that resolves nothing; a pointer to a procedure that is not there
               reads as proof to anyone who does not go looking. Same defect this repo shipped
               on ArchitecturalBuildingBlock.conformanceTest.

  INVARIANT 6  (validator-only) `observedPeak`, when present, must be a gate-eligible
               Measurement. A peak that was declared rather than instrumented, or came from a
               walk that refused part of its population, cannot calibrate a limit.

  INVARIANT 7  the $ref target must exist. A cross-schema reference to a missing file is the
               same dangling pointer as INVARIANT 5, one level up.

NOT CHECKED, deliberately: whether `observedPeak.value` exceeds `limit.value`. Measurement has
no unit on `value` — `sampling.unit` describes what was counted ('hourly samples'), not what
the value measures ('bytes'). Comparing two numbers whose units cannot be verified is the exact
error class this repo has spent the day closing, so the comparison is omitted rather than
bodged. The real fix is a `unit` field on Measurement; recorded as follow-up, not smuggled in.
"""

from __future__ import annotations

import copy
import json
import sys
from itertools import product
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "ResourceContract.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "resource-contract.example.json"
MEASUREMENT_PATH = REPO_ROOT / "schemas" / "Measurement.json"


def resolve_refs(schema: dict, measurement: dict) -> dict:
    """Inline the Measurement $ref.

    Done by substitution rather than a resolver registry so this validator has no dependency
    beyond jsonschema, and so the inlining is visible here instead of happening inside a
    library. The schema file keeps its `$ref` for consumers.
    """
    out = copy.deepcopy(schema)
    node = out["properties"]["observedPeak"]
    assert node.get("$ref") == "Measurement.json", f"unexpected $ref: {node.get('$ref')}"
    desc = node.get("description")
    embedded = {k: v for k, v in copy.deepcopy(measurement).items() if k not in ("$schema", "$id")}
    if desc:
        embedded["description"] = desc
    out["properties"]["observedPeak"] = embedded
    return out


def main() -> int:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("Missing dependency: jsonschema", file=sys.stderr)
        return 1

    failures: list[str] = []
    checks = 0

    # INVARIANT 7 first — everything below depends on the referenced schema existing.
    print("  INVARIANT 7 — the $ref target exists")
    checks += 1
    if not MEASUREMENT_PATH.is_file():
        print(f"    FAIL {MEASUREMENT_PATH.name} missing — observedPeak $ref dangles")
        print(f"\n1 failure of {checks} checks:", file=sys.stderr)
        print(f"  observedPeak $ref points at {MEASUREMENT_PATH.name}, which does not exist",
              file=sys.stderr)
        return 1
    print(f"    OK   {MEASUREMENT_PATH.name} resolves")

    raw = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    measurement = json.loads(MEASUREMENT_PATH.read_text(encoding="utf-8"))
    schema = resolve_refs(raw, measurement)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    def case(label: str, instance: Any, should_pass: bool) -> None:
        nonlocal checks
        checks += 1
        errs = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        accepted = not errs
        if accepted != should_pass:
            want = "accepted" if should_pass else "rejected"
            got = "accepted" if accepted else f"rejected ({errs[0].message[:110]})"
            failures.append(f"{label}: expected {want}, was {got}")

    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def broken(mutation) -> dict:
        b = copy.deepcopy(example)
        mutation(b)
        return b

    print("  shape")
    case("shipped example (tenant-scoped disk-writes, throttle)", example, True)
    for label, mut in [
        ("kind wrong", lambda b: b.__setitem__("kind", "Quota")),
        ("resource outside the closed set", lambda b: b.__setitem__("resource", "gpu")),
        ("limit without a unit", lambda b: b["limit"].pop("unit")),
        ("limit value zero", lambda b: b["limit"].__setitem__("value", 0)),
        ("limit value negative", lambda b: b["limit"].__setitem__("value", -1)),
        ("window absent (a rate without a window is not a rate)", lambda b: b.pop("window")),
        ("window not an ISO 8601 duration", lambda b: b.__setitem__("window", "1 day")),
        ("scope outside the enum", lambda b: b.__setitem__("scope", "container")),
        ("enforcement outside the enum", lambda b: b.__setitem__("enforcement", "warn")),
        ("contractId not lowercase-kebab", lambda b: b.__setitem__("contractId", "Runner_Disk")),
        ("undeclared field at root (schema is closed)", lambda b: b.__setitem__("zz", 1)),
        ("undeclared field in limit", lambda b: b["limit"].__setitem__("zz", 1)),
        ("observedPeak not gate-eligible but claims to be",
         lambda b: b["observedPeak"].__setitem__("source", "declared")),
    ]:
        case(label, broken(mut), False)
    print(f"    {'OK  ' if not failures else 'FAIL'} 13 shape controls rejected, 1 accepted")

    # INVARIANT 1 + 2 — exhaustive over enforcement x presence of each witness.
    print("  INVARIANT 1 & 2 — acting requires a demonstration; observing requires a reason")
    before = len(failures)
    for enf, has_nc, has_reason in product(
        ["observe", "throttle", "refuse", "terminate"], [True, False], [True, False]
    ):
        doc = {
            "schemaVersion": "0.1.0", "kind": "ResourceContract",
            "resource": "cpu", "limit": {"value": 0.5, "unit": "ratio-of-one-cpu"},
            "window": "PT180S", "scope": "tenant", "enforcement": enf,
        }
        if has_nc:
            doc["negativeControl"] = "conformance/resource-contract-throttle-fires.md"
        if has_reason:
            doc["observeOnlyReason"] = "characterising before choosing a threshold"
        ok = has_nc if enf != "observe" else has_reason
        case(f"enforcement={enf} negativeControl={has_nc} observeOnlyReason={has_reason}",
             doc, ok)
    print(f"    {'OK  ' if len(failures) == before else 'FAIL'} 16 combinations: the 3 acting "
          "enforcements require negativeControl, observe requires observeOnlyReason")

    print("  INVARIANT 1a — the allOf is what does the work (mutation test)")
    checks += 1
    loose = copy.deepcopy(schema)
    loose["allOf"] = [c for c in loose["allOf"] if "INVARIANT 1" not in c.get("$comment", "")]
    toothless = {
        "schemaVersion": "0.1.0", "kind": "ResourceContract", "resource": "cpu",
        "limit": {"value": 0.5, "unit": "ratio-of-one-cpu"}, "window": "PT180S",
        "scope": "tenant", "enforcement": "throttle",
    }
    if list(Draft202012Validator(loose).iter_errors(toothless)):
        failures.append(
            "mutation test inconclusive: with INVARIANT 1 removed, a throttle contract with no "
            "negativeControl was STILL rejected — the allOf is not the constraint doing the "
            "work, so the 16 combinations prove nothing about it"
        )
        print("    FAIL invariant removed but document still rejected")
    else:
        print("    OK   invariant removed ⇒ evidence-free throttle accepted; restored ⇒ "
              "rejected. The allOf is load-bearing.")

    print("  INVARIANT 3 — per-process scope must justify itself against fan-out")
    before = len(failures)
    case("scope=process with no rationale",
         broken(lambda b: b.__setitem__("scope", "process")), False)
    case("scope=process with a rationale",
         broken(lambda b: (b.__setitem__("scope", "process"),
                           b.__setitem__("scopeRationale",
                                         "single-tenant host; fan-out is not possible here"))),
         True)
    print(f"    {'OK  ' if len(failures) == before else 'FAIL'} rationale required, and "
          "sufficient")

    print("  INVARIANT 4 — a non-zero fired count needs a timestamp")
    before = len(failures)
    case("firedCount=3 with no lastFiredAt",
         broken(lambda b: b.__setitem__("firedCount", 3)), False)
    case("firedCount=3 with lastFiredAt",
         broken(lambda b: (b.__setitem__("firedCount", 3),
                           b.__setitem__("lastFiredAt", "2026-07-30T04:00:00Z"))), True)
    print(f"    {'OK  ' if len(failures) == before else 'FAIL'} count and timestamp move "
          "together")

    print("  INVARIANT 5 — negativeControl resolves")
    checks += 1
    nc = example.get("negativeControl")
    if nc and (REPO_ROOT / nc).is_file():
        print(f"    OK   {nc} resolves")
    else:
        failures.append(
            f"negativeControl {nc!r} does not resolve under {REPO_ROOT}. A pointer to a "
            "procedure that is not there reads as proof to anyone who does not go looking."
        )
    checks += 1
    probe = "conformance/does-not-exist-negative-control.md"
    if not (REPO_ROOT / probe).is_file():
        print("    OK   negative control: a dangling pointer IS detected as unresolvable")
    else:
        failures.append("negative control for INVARIANT 5 is not negative: probe path exists")

    print("  INVARIANT 6 — observedPeak must be gate-eligible")
    before = len(failures)
    checks += 1
    peak = example.get("observedPeak")
    if peak is not None and peak.get("gateEligible") is not True:
        failures.append(
            "example observedPeak is not gate-eligible — a peak that was declared, or came "
            "from a walk that refused members, cannot calibrate a limit"
        )
    else:
        print("    OK   example peak is measured, nothing unobserved, gateEligible")
    # Rejected above in the shape sweep via source=declared; assert the reason is the peak.
    checks += 1
    forged = broken(lambda b: (b["observedPeak"].__setitem__("source", "assumed"),
                               b["observedPeak"].__setitem__("gateEligible", True)))
    errs = list(validator.iter_errors(forged))
    if errs and any("observedPeak" in list(map(str, e.path)) for e in errs):
        print("    OK   negative control: an assumed peak claiming eligibility is rejected, "
              "and the error is located on observedPeak")
    else:
        failures.append(
            "an assumed observedPeak claiming gateEligible=true was not rejected at that path "
            "— the Measurement $ref is not being applied to the nested object"
        )

    if failures:
        print(f"\n{len(failures)} failure(s) of {checks} checks:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print(f"\nOK ResourceContract: {checks} checks. Acting enforcement requires a resolvable "
          "negativeControl (mutation-tested), observe-only requires a stated reason, "
          "per-process scope must justify itself against fan-out, and observedPeak must be a "
          "gate-eligible Measurement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
