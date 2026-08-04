#!/usr/bin/env python3
"""Validate CaptureReceipt examples + the invariants that make the receipt safe.

CaptureReceipt (Epoch E13 / WS-B) is the universal bind-purpose-before-f() primitive:
it seals a declared purpose + authorization onto a datum BEFORE the transform that would
consume it runs. It generalizes TwinAttestation.envelope.authorization. The reason it must
exist at capture — not later — is the reidentification-economy result that purpose is
provably unrecoverable from the signal (I(purpose; Q) = 0).

Beyond JSON Schema:
  * URN prefix per contract (urn:srcos:capture-receipt:);
  * boundBeforeTransform is exactly true (the whole point — sealed before f());
  * fail-closed: missing/empty declaredPurpose OR authorizationProof ⇒ disposition
    MUST be 'refused' or 'inert' (you cannot be 'admitted' without a bound purpose+proof);
  * disposition ∈ {admitted, refused, inert}.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ("schemas/CaptureReceipt.json", "examples/capture_receipt.json"),
    ("schemas/CaptureReceipt.json", "examples/capture_receipt_refused.json"),
]
EXPECTED_ID_PREFIX = "urn:srcos:capture-receipt:"
VALID_DISPOSITIONS = {"admitted", "refused", "inert"}


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

        # 1. URN prefix.
        if not str(doc.get("id", "")).startswith(EXPECTED_ID_PREFIX):
            errors.append(f"{ex_rel}: id must start with '{EXPECTED_ID_PREFIX}'")

        # 2. boundBeforeTransform is exactly true.
        if doc.get("boundBeforeTransform") is not True:
            errors.append(f"{ex_rel}: boundBeforeTransform must be exactly true (sealed before f())")

        # 4. disposition in the closed set.
        disp = doc.get("disposition")
        if disp not in VALID_DISPOSITIONS:
            errors.append(f"{ex_rel}: disposition must be one of {sorted(VALID_DISPOSITIONS)}")

        # 3. Fail-closed: no bound purpose+proof ⇒ cannot be admitted.
        purpose = str(doc.get("declaredPurpose", "")).strip()
        proof = str(doc.get("authorizationProof", "")).strip()
        if (not purpose or not proof) and disp == "admitted":
            errors.append(
                f"{ex_rel}: fail-closed violation: disposition 'admitted' requires a "
                f"non-empty declaredPurpose AND authorizationProof"
            )

        if not any(e.startswith(ex_rel) for e in errors):
            print(f"OK   {ex_rel}")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nAll CaptureReceipt examples valid (schema + invariants).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
