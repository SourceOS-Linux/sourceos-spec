#!/usr/bin/env python3
"""Validate SourceOS interaction substrate examples."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "SourceOSInteractionEvent.json"
EXAMPLE = ROOT / "examples" / "sourceos-interaction-event.json"


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    schema = load_json(SCHEMA)
    example = load_json(EXAMPLE)

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(example, schema)


if __name__ == "__main__":
    main()
