#!/usr/bin/env python3
"""Validate immutable-node contract examples against their schemas."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    ("schemas/HostCapabilityPlacement.json", "examples/hostcapabilityplacement.json"),
    ("schemas/NodeStateSchema.json", "examples/nodestateschema.json"),
    ("schemas/ImmutableNodeProfile.json", "examples/immutablenodeprofile.json"),
]


def load_json(path: str) -> object:
    with (ROOT / path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    for schema_path, example_path in PAIRS:
        schema = load_json(schema_path)
        example = load_json(example_path)
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(instance=example, schema=schema)
        print(f"OK: {example_path} validates against {schema_path}")


if __name__ == "__main__":
    main()
