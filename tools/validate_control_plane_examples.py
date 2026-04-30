#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "control-plane" / "BootReleaseSet.json", ROOT / "examples" / "boot_release_set.json"),
    (ROOT / "schemas" / "control-plane" / "EnrollmentToken.json", ROOT / "examples" / "enrollment_token.json"),
]


def validate_pair(schema_path: Path, example_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema).check_schema(schema)
    legacy_ref = schema.get("allOf", [{}])[0].get("$ref")
    validation_schema_path = (schema_path.parent / legacy_ref).resolve() if legacy_ref else schema_path
    validation_schema = json.loads(validation_schema_path.read_text(encoding="utf-8"))
    example = json.loads(example_path.read_text(encoding="utf-8"))
    jsonschema.validate(example, validation_schema)


def main() -> int:
    checks: dict[str, bool] = {}
    for schema_path, example_path in PAIRS:
        validate_pair(schema_path, example_path)
        checks[example_path.name] = True
    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
