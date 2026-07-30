#!/usr/bin/env python3
"""Validate Measurement: a value carries how it was obtained, and gate-eligibility is derived.

The invariant worth having is that `gateEligible` cannot be chosen by the producer. It is
false unless an instrument produced the value AND nothing was refused. Everything else here
exists to prove that rule fires, in both directions, on documents rather than on fixtures.

  INVARIANT 1  source != measured, or unobserved > 0, forces gateEligible: false. It is a
               CEILING: claiming false is always allowed, claiming true needs a clean
               reading. Asserted over all 4 sources x {0,1} unobserved x {true,false}
               claimed — 16 exhaustive combinations, each fed to the schema as a document.

  INVARIANT 2  source == measured requires `instrument`. A measured value with no named
               instrument is the same unfalsifiable assertion the enum exists to prevent,
               and the name alone is not enough: on the machine that motivated this schema
               `find` is bfs and `stat -f` is GNU coreutils, so 'find(1)' hides a semantic
               difference that changed a result.

  INVARIANT 3  unobserved > 0 requires `sampling`. Ten refused members with no stated
               population is a fact about nothing.

  INVARIANT 4  (validator-only, not expressible in JSON Schema)
               sampling.observed + unobserved <= sampling.population. A walk cannot read
               more members than exist, and one that claims to has miscounted its own
               population — which is the failure mode that produced 617-of-627.

  INVARIANT 5  LawfulDispatchReceipt's inlined `source` enum must remain a SUBSET of this
               one. That schema had `measured | declared` on `law` and `evidence` before this
               file existed; extracting the concept here is only worth doing if the two
               cannot drift. Divergence is a failing test, not a silent fork.
"""

from __future__ import annotations

import copy
import json
import sys
from itertools import product
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "Measurement.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "measurement.example.json"
LDR_PATH = REPO_ROOT / "schemas" / "LawfulDispatchReceipt.json"

#: The CEILING on eligibility, not its value. Only a clean instrumented reading MAY claim
#: gateEligible=true; every reading may claim false. Written as a predicate so the test and the
#: schema state the same rule in different languages — and the exhaustive sweep below caught
#: this file asserting equality instead of a bound on its first run, which is what the sweep
#: is for. Producers must be able to downgrade their own measurement voluntarily: the same
#: reason the truth-product is a MEET, where a caller can never claim more than its weakest
#: factor but is always free to claim less.
def may_claim_eligible(source: str, unobserved: int) -> bool:
    return source == "measured" and unobserved == 0


def main() -> int:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("Missing dependency: jsonschema", file=sys.stderr)
        return 1

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    failures: list[str] = []
    checks = 0

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
    case("shipped example (the 617-of-627 container census)", example, True)
    for label, mut in [
        ("kind wrong", lambda b: b.__setitem__("kind", "Metric")),
        ("source outside the enum", lambda b: b.__setitem__("source", "estimated")),
        ("source absent", lambda b: b.pop("source")),
        ("value absent", lambda b: b.pop("value")),
        ("gateEligible absent (must be stated, never inferred)",
         lambda b: b.pop("gateEligible")),
        ("gateEligible as a string", lambda b: b.__setitem__("gateEligible", "false")),
        ("unobserved negative", lambda b: b.__setitem__("unobserved", -1)),
        ("sampling.unit missing", lambda b: b["sampling"].pop("unit")),
        ("sampling.population missing", lambda b: b["sampling"].pop("population")),
        ("schemaVersion bare number", lambda b: b.__setitem__("schemaVersion", "1")),
        ("undeclared field at root (schema is closed)",
         lambda b: b.__setitem__("zzUnknown", "leak")),
        ("undeclared field in sampling", lambda b: b["sampling"].__setitem__("zz", 1)),
    ]:
        case(label, broken(mut), False)
    print(f"    {'OK  ' if not failures else 'FAIL'} 12 shape controls rejected, 1 accepted")

    # INVARIANT 1 — exhaustive. instrument and sampling are always present so that
    # invariants 2 and 3 cannot be what does the rejecting.
    print("  INVARIANT 1 — gateEligible is derived, not chosen (16 combinations)")
    before = len(failures)
    for src, unobs, claimed in product(
        ["measured", "derived", "declared", "assumed"], [0, 1], [True, False]
    ):
        doc = {
            "schemaVersion": "0.1.0",
            "kind": "Measurement",
            "value": 1,
            "source": src,
            "instrument": "probe",
            "sampling": {"observed": 1, "population": 2, "unit": "entries"},
            "unobserved": unobs,
            "gateEligible": claimed,
        }
        # A claim of false is always permitted; only a claim of true needs a clean reading.
        ok = (not claimed) or may_claim_eligible(src, unobs)
        case(f"source={src} unobserved={unobs} claims gateEligible={claimed}", doc, ok)
    pairs = list(product(["measured", "derived", "declared", "assumed"], [0, 1]))
    n_eligible = sum(1 for s, u in pairs if may_claim_eligible(s, u))
    print(f"    {'OK  ' if len(failures) == before else 'FAIL'} of {len(pairs)} "
          f"source/unobserved pairs, exactly {n_eligible} may claim gateEligible=true "
          f"(measured + nothing refused); the other {len(pairs) - n_eligible} are rejected "
          "when they claim it. Claiming false is always accepted — eligibility is a ceiling, "
          "so a producer may downgrade its own reading but never upgrade it.")

    # The mutation test. Without it, INVARIANT 1's cases pass whenever the schema rejects for
    # ANY reason — and would keep passing if the allOf were deleted while some unrelated
    # constraint did the work.
    print("  INVARIANT 1a — the allOf is what does the work (mutation test)")
    checks += 1
    loose = copy.deepcopy(schema)
    loose["allOf"] = [c for c in loose["allOf"] if "INVARIANT 1" not in c.get("$comment", "")]
    forged = {
        "schemaVersion": "0.1.0", "kind": "Measurement", "value": 1,
        "source": "assumed", "gateEligible": True,
    }
    if list(Draft202012Validator(loose).iter_errors(forged)):
        failures.append(
            "mutation test inconclusive: with INVARIANT 1 removed, an assumed value claiming "
            "gateEligible=true was STILL rejected — so the allOf is not the constraint doing "
            "the work and the 16 combinations above prove nothing about it"
        )
        print("    FAIL invariant removed but document still rejected")
    else:
        print("    OK   invariant removed ⇒ assumed+gateEligible=true accepted; "
              "restored ⇒ rejected. The allOf is load-bearing.")

    print("  INVARIANT 2 — a measured value must name its instrument")
    before = len(failures)
    case("measured with no instrument",
         {"schemaVersion": "0.1.0", "kind": "Measurement", "value": 1,
          "source": "measured", "gateEligible": True}, False)
    case("declared with no instrument (permitted — nothing to name)",
         {"schemaVersion": "0.1.0", "kind": "Measurement", "value": 1,
          "source": "declared", "gateEligible": False}, True)
    print(f"    {'OK  ' if len(failures) == before else 'FAIL'} measured requires it, "
          "declared does not")

    print("  INVARIANT 3 — refused members require a stated population")
    before = len(failures)
    case("unobserved=10 with no sampling block",
         {"schemaVersion": "0.1.0", "kind": "Measurement", "value": 617,
          "source": "measured", "instrument": "bfs", "unobserved": 10,
          "gateEligible": False}, False)
    print(f"    {'OK  ' if len(failures) == before else 'FAIL'} "
          "'10 refused' with no population is a fact about nothing")

    # INVARIANT 4 — arithmetic JSON Schema cannot express.
    print("  INVARIANT 4 — observed + unobserved <= population (validator-enforced)")
    checks += 1
    s = example.get("sampling")
    if s and s["observed"] + example.get("unobserved", 0) > s["population"]:
        failures.append(
            f"example: observed {s['observed']} + unobserved {example.get('unobserved', 0)} "
            f"exceeds population {s['population']} — a walk cannot read more members than exist"
        )
    else:
        print(f"    OK   example: {s['observed']} + {example.get('unobserved', 0)} "
              f"<= {s['population']}")
    checks += 1
    bad = broken(lambda b: b["sampling"].__setitem__("population", 3))
    bs = bad["sampling"]
    if bs["observed"] + bad.get("unobserved", 0) > bs["population"]:
        print("    OK   negative control: population lowered to 3 IS caught as impossible")
    else:
        failures.append("negative control for INVARIANT 4 did not trigger")

    # INVARIANT 5 — the anti-drift guard. This is the reason extracting the concept is worth
    # doing at all; without it we would have two definitions of `source` instead of one.
    print("  INVARIANT 5 — LawfulDispatchReceipt's source enum stays a subset")
    checks += 1
    if not LDR_PATH.is_file():
        failures.append(f"{LDR_PATH.name} not found — cannot check enum drift")
    else:
        ldr = json.loads(LDR_PATH.read_text(encoding="utf-8"))
        found: list[list[str]] = []

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "source" and isinstance(v, dict) and isinstance(v.get("enum"), list):
                        found.append(v["enum"])
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(ldr)
        mine = set(schema["properties"]["source"]["enum"])
        if not found:
            failures.append(
                "LawfulDispatchReceipt no longer declares a `source` enum. Either it was "
                "refactored to $ref Measurement (good — delete this check) or the invariant "
                "was dropped (bad). Not something to pass silently."
            )
        else:
            for enum in found:
                if not set(enum) <= mine:
                    failures.append(
                        f"drift: LawfulDispatchReceipt source enum {sorted(enum)} is not a "
                        f"subset of Measurement's {sorted(mine)}. Two schemas defining the "
                        "same field differently is the failure this extraction exists to stop."
                    )
            if all(set(e) <= mine for e in found):
                print(f"    OK   {len(found)} LDR source enum(s) ⊆ Measurement's "
                      f"{sorted(mine)}; no drift")

    if failures:
        print(f"\n{len(failures)} failure(s) of {checks} checks:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print(f"\nOK Measurement: {checks} checks. gateEligible is derived from source and "
          "unobserved (mutation-tested), a measured value must name its instrument, refused "
          "members require a population, and LawfulDispatchReceipt's enum cannot drift from "
          "this one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
