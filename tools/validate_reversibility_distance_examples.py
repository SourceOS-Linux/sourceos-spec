#!/usr/bin/env python3
"""Validate ReversibilityDistance examples + the invariants that make the meter honest.

Beyond JSON Schema:
  * URN prefix per contract;
  * the distance is a distance: dBits >= 0;
  * the reidentified flag is not free-floating — reidentified iff dBits == 0;
  * the unicity curve is well-formed: p are positive integers, epsilon_p in [0, 1];
  * the budget is the singling-out budget: budgetBits ~= log2(populationN) (within 0.01)
    whenever both are present — so D is measured against the right ceiling.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ("schemas/ReversibilityDistance.json", "examples/reversibility_distance.json"),
]
EXPECTED_IDS = {
    "ReversibilityDistance": "urn:srcos:reversibility-distance:",
}


def main() -> int:
    errors: list[str] = []
    for schema_rel, ex_rel in PAIRS:
        schema = json.loads((ROOT / schema_rel).read_text())
        doc = json.loads((ROOT / ex_rel).read_text())
        try:
            jsonschema.validate(
                doc,
                schema,
                cls=jsonschema.Draft202012Validator,
                format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
            )
        except jsonschema.ValidationError as e:
            errors.append(f"{ex_rel}: schema invalid: {e.message} @ {list(e.absolute_path)}")
            continue

        t = doc.get("type")
        pfx = EXPECTED_IDS.get(t)
        if pfx and not str(doc.get("id", "")).startswith(pfx):
            errors.append(f"{ex_rel}: id must start with '{pfx}'")

        d = doc.get("dBits")
        if d is None or d < 0:
            errors.append(f"{ex_rel}: dBits must be present and >= 0 (it is a distance)")
        else:
            reid = doc.get("reidentified")
            if reid is not None and reid != (d == 0):
                errors.append(f"{ex_rel}: reidentified must equal (dBits == 0)")

        curve = doc.get("unicityCurve")
        if curve is not None:
            for i, pt in enumerate(curve):
                p = pt.get("p")
                ep = pt.get("epsilonP")
                if not isinstance(p, int) or p < 1:
                    errors.append(f"{ex_rel}: unicityCurve[{i}].p must be a positive integer")
                if ep is None or not (0.0 <= ep <= 1.0):
                    errors.append(f"{ex_rel}: unicityCurve[{i}].epsilonP must be in [0, 1]")

        n = doc.get("populationN")
        b = doc.get("budgetBits")
        if n is not None and b is not None:
            if n <= 0:
                errors.append(f"{ex_rel}: populationN must be > 0")
            elif abs(b - math.log2(n)) > 0.01:
                errors.append(
                    f"{ex_rel}: budgetBits ({b}) must equal log2(populationN) "
                    f"({math.log2(n):.6f}) within 0.01"
                )

        if not any(e.startswith(ex_rel) for e in errors):
            print(f"OK   {ex_rel}")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nAll ReversibilityDistance examples valid (schema + invariants).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
