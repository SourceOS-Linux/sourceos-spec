#!/usr/bin/env python3
"""Validate RLD LoaderFault / ResilientDiagnosticRecord examples + their invariants.

Beyond JSON Schema (with a $ref registry so RDR can embed LoaderFault):
  * URN prefix on the RDR;
  * kind <-> code consistency (the stable-code table);
  * severity is exactly what the binding class dictates (REQUIRED->fatal, FEATURE->degraded,
    WEAK->info, LAZY->handled|fatal) — the classifier is a table, not a heuristic (I5/severity map);
  * privacy by projection (I8): a telemetry-tier record contains NO filesystem-path-like value
    (no '/Library/…', '/Users/…', or leading '/…') — paths are symbolic (store names, hashes);
  * reproKey excludes the timestamp (does not equal capturedAt), so identical defects coalesce.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

FORMAT_CHECKER = FormatChecker()

ROOT = Path(__file__).resolve().parents[1]
LF = json.loads((ROOT / "schemas/LoaderFault.json").read_text())
RDR = json.loads((ROOT / "schemas/ResilientDiagnosticRecord.json").read_text())
REG = Registry().with_resource(LF["$id"], Resource.from_contents(LF))

KIND_CODE = {
    "MissingProvider": "LDR-DEP-MISSING", "VersionUnsatisfied": "LDR-DEP-VERSION",
    "InterfaceMismatch": "LDR-ABI-MISMATCH", "SignatureInvalid": "LDR-SIG-INVALID",
    "CorruptImage": "LDR-IMG-CORRUPT", "SandboxDenied": "LDR-SBX-DENY",
    "ResourceExhausted": "LDR-RES-EXHAUST",
}
BINDING_SEV = {"REQUIRED": {"fatal"}, "FEATURE": {"degraded"}, "WEAK": {"info"}, "LAZY": {"handled", "fatal"}}

PAIRS = [
    ("schemas/LoaderFault.json", "examples/loader_fault.json", LF, False),
    ("schemas/ResilientDiagnosticRecord.json", "examples/resilient_diagnostic_record.json", RDR, True),
    ("schemas/ResilientDiagnosticRecord.json", "examples/resilient_diagnostic_record_degraded.json", RDR, True),
]


def path_like(v) -> bool:
    if isinstance(v, str):
        return v.startswith("/") or "/Library/" in v or "/Users/" in v or v.startswith("file://")
    if isinstance(v, dict):
        return any(path_like(x) for x in v.values())
    if isinstance(v, list):
        return any(path_like(x) for x in v)
    return False


def check_fault(fault, ex_rel, errors):
    k, c, sev = fault.get("kind"), fault.get("code"), fault.get("severity")
    if KIND_CODE.get(k) != c:
        errors.append(f"{ex_rel}: kind '{k}' must pair with code '{KIND_CODE.get(k)}', got '{c}'")
    imp = fault.get("import") or {}
    b = imp.get("binding")
    if b and sev not in BINDING_SEV.get(b, set()):
        errors.append(f"{ex_rel}: binding {b} requires severity in {sorted(BINDING_SEV[b])}, got '{sev}'")


def main() -> int:
    errors: list[str] = []
    for schema_rel, ex_rel, schema, is_rdr in PAIRS:
        doc = json.loads((ROOT / ex_rel).read_text())
        try:
            Draft202012Validator(schema, registry=REG, format_checker=FORMAT_CHECKER).validate(doc)
        except Exception as e:
            errors.append(f"{ex_rel}: schema invalid: {str(e)[:140]}")
            continue
        if is_rdr:
            if not str(doc.get("id", "")).startswith("urn:srcos:rdr:"):
                errors.append(f"{ex_rel}: id must start with 'urn:srcos:rdr:'")
            check_fault(doc.get("fault", {}), ex_rel, errors)
            if doc.get("redaction", {}).get("tier") == "telemetry" and path_like(doc):
                errors.append(f"{ex_rel}: telemetry-tier record contains a filesystem-path-like value (I8 projection violation)")
            if doc.get("reproKey") and doc.get("reproKey") == doc.get("capturedAt"):
                errors.append(f"{ex_rel}: reproKey must exclude the timestamp")
        else:
            check_fault(doc, ex_rel, errors)
        if not any(e.startswith(ex_rel) for e in errors):
            print(f"OK   {ex_rel}")
    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nAll RLD examples valid (schema + invariants).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
