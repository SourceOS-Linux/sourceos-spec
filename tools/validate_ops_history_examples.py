#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "OpsHistoryEvent.json", ROOT / "examples" / "ops-history-event.json"),
    (ROOT / "schemas" / "OpsHistorySyncPolicy.json", ROOT / "examples" / "ops-history-sync-policy.json"),
    (ROOT / "schemas" / "LocalFirstServiceManifest.json", ROOT / "examples" / "local-first-service-manifest.json"),
    (ROOT / "schemas" / "RedactionTombstone.json", ROOT / "examples" / "redaction-tombstone.json"),
    (ROOT / "schemas" / "OpsHistoryContextPackRef.json", ROOT / "examples" / "ops-history-context-pack-ref.json"),
    (ROOT / "schemas" / "BearHistoryEvent.json", ROOT / "examples" / "bearhistory-event.json"),
    (ROOT / "schemas" / "BearHistorySyncPolicy.json", ROOT / "examples" / "bearhistory-sync-policy.json"),
    (ROOT / "schemas" / "ShellReceiptEvent.json", ROOT / "examples" / "shell-receipt-event.json"),
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
