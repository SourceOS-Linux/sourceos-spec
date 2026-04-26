#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "control-plane" / "ReleaseSet.json", ROOT / "examples" / "release_set.json"),
    (ROOT / "schemas" / "control-plane" / "Fingerprint.json", ROOT / "examples" / "fingerprint.json"),
]


def main() -> int:
    checks: dict[str, bool] = {}
    for schema_path, example_path in PAIRS:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        example = json.loads(example_path.read_text(encoding="utf-8"))
        resolver = jsonschema.validators.validator_for(schema)
        resolver.check_schema(schema)
        validator = resolver(schema, registry=jsonschema.validators.SPECIFICATIONS)
        # Resolve local legacy refs by changing cwd-like base through a RefResolver fallback for older jsonschema behavior.
        # jsonschema 4.x resolves relative refs against the schema id; these wrapper schemas reference local legacy files.
        legacy_schema_path = schema_path.with_name(schema["allOf"][0]["$ref"])
        legacy_schema = json.loads(legacy_schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(example, legacy_schema)
        checks[example_path.name] = True
    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
