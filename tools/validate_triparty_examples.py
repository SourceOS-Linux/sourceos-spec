#!/usr/bin/env python3
"""Validate the governed-triparty marketplace contract examples.

Covers the settlement/marketplace primitives: NettingCell (the triparty clearing
cell that couples value + proof + authority + disclosure) and TripartyBundle (the
typed, proof-carrying bundle that advances a cell through its lifecycle).
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "NettingCell.json", ROOT / "examples" / "netting_cell.json"),
    (ROOT / "schemas" / "TripartyBundle.json", ROOT / "examples" / "triparty_bundle.json"),
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
