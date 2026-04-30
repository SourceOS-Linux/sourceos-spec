#!/usr/bin/env python3
"""Validate NLBoot schema/example pairs."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "NLBootPlan.json", ROOT / "examples" / "nlboot_plan.json"),
    (ROOT / "schemas" / "ArtifactCacheRecord.json", ROOT / "examples" / "artifact_cache_record.json"),
    (ROOT / "schemas" / "BootProofRecord.json", ROOT / "examples" / "boot_proof_record.json"),
    (ROOT / "schemas" / "AppleSiliconAdapterEvidence.json", ROOT / "examples" / "apple_silicon_adapter_evidence.json"),
]


def validate_pair(schema_path: Path, example_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema).check_schema(schema)
    example = json.loads(example_path.read_text(encoding="utf-8"))
    jsonschema.validate(example, schema)


def main() -> int:
    checks: dict[str, bool] = {}
    for schema_path, example_path in PAIRS:
        validate_pair(schema_path, example_path)
        checks[example_path.name] = True
    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
