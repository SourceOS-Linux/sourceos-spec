#!/usr/bin/env python3
"""Validate MultiversealTwin family examples + the invariants that make the twin safe.

Beyond JSON Schema:
  * URN prefix per contract;
  * reference-at-ingest: a TwinAttestation stores only a boundVector (never a bare object)
    and carries an authorization (declaredPurpose + proof) — the purpose bit is bound at
    capture, not inferred later;
  * unlinkability budget: epsilon > 0 and flagged as the reversibility-distance ledger;
  * sharing threshold sane: 1 <= d <= n;
  * impersonation wall: fixed rule + phase-retrieval hardened;
  * mint asymmetry: VRF anchored to a ProofOfSelfToken;
  * interferometric read: authorized watcher, sub-threshold + global-tamper asserted.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ("schemas/TwinAttestation.json", "examples/twin_attestation.json"),
    ("schemas/MultiversealTwin.json", "examples/multiverseal_twin.json"),
    ("schemas/InterferometricDiff.json", "examples/interferometric_diff.json"),
]
EXPECTED_IDS = {
    "TwinAttestation": "urn:srcos:twin-attestation:",
    "MultiversealTwin": "urn:srcos:multiverseal-twin:",
    "InterferometricDiff": "urn:srcos:interferometric-diff:",
}


def main() -> int:
    errors: list[str] = []
    for schema_rel, ex_rel in PAIRS:
        schema = json.loads((ROOT / schema_rel).read_text())
        doc = json.loads((ROOT / ex_rel).read_text())
        try:
            jsonschema.validate(doc, schema, cls=jsonschema.Draft202012Validator)
        except jsonschema.ValidationError as e:
            errors.append(f"{ex_rel}: schema invalid: {e.message} @ {list(e.absolute_path)}")
            continue

        t = doc.get("type")
        pfx = EXPECTED_IDS.get(t)
        if pfx and not str(doc.get("id", "")).startswith(pfx):
            errors.append(f"{ex_rel}: id must start with '{pfx}'")

        if t == "TwinAttestation":
            bv = doc.get("boundVector", {})
            if "object" in bv or "bareObject" in bv or "intensity" in bv:
                errors.append(f"{ex_rel}: reference-at-ingest violation: a bare object was stored")
            auth = doc.get("envelope", {}).get("authorization", {})
            if not auth.get("declaredPurpose") or not auth.get("authorizationProof"):
                errors.append(f"{ex_rel}: attestation missing bound authorization (purpose+proof)")
            if doc.get("grounding", {}).get("state") not in ("coherent", "decohered"):
                errors.append(f"{ex_rel}: grounding.state must be coherent|decohered")

        if t == "MultiversealTwin":
            u = doc.get("unlinkability", {})
            if not (u.get("epsilon", 0) > 0) or u.get("isReversibilityBudget") is not True:
                errors.append(f"{ex_rel}: unlinkability epsilon must be >0 and flagged as reversibility budget")
            s = doc.get("sharing", {})
            if not (1 <= s.get("d", 0) <= s.get("n", 0)):
                errors.append(f"{ex_rel}: sharing must satisfy 1 <= d <= n")
            w = doc.get("impersonationWall", {})
            if w.get("rule") != "mint-only-under-subject-key-or-subject-signed-capability" or w.get("phaseRetrievalHardened") is not True:
                errors.append(f"{ex_rel}: impersonation wall not enforced")
            m = doc.get("mintAnchor", {})
            if m.get("scheme") != "vrf" or not str(m.get("proofOfSelfRef", "")).startswith("urn:srcos:proof-of-self:"):
                errors.append(f"{ex_rel}: mint anchor must be VRF anchored to a ProofOfSelfToken")

        if t == "InterferometricDiff":
            if doc.get("watcher", {}).get("authorized") is not True:
                errors.append(f"{ex_rel}: watcher must be authorized (rainbow angle-bounding)")
            f = doc.get("fringe", {})
            if f.get("subThreshold") is not True or f.get("tamperGlobalPerturbation") is not True:
                errors.append(f"{ex_rel}: fringe must assert sub-threshold + global tamper properties")

        if not any(e.startswith(ex_rel) for e in errors):
            print(f"OK   {ex_rel}")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nAll MultiversealTwin examples valid (schema + invariants).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
