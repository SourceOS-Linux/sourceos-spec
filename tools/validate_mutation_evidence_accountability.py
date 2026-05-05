#!/usr/bin/env python3
"""Validate SourceOS Mutation and Evidence Accountability examples.

This validator intentionally includes one semantic guardrail that plain JSON Schema
cannot express cleanly yet: a compromise assessment with blind, degraded, or
missing sensors must not claim complete evidence quality or omit
cannot_exclude_compromise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover
    raise SystemExit("jsonschema is required: python -m pip install jsonschema") from exc

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "MutationEvidenceAccountability.schema.json"
EXAMPLES_PATH = ROOT / "examples" / "mutation-evidence-accountability.examples.json"
ANTI_PATH = ROOT / "fixtures" / "anti-patterns" / "mutation-evidence-accountability.invalid.json"

schema = json.loads(SCHEMA_PATH.read_text())
validator = jsonschema.Draft202012Validator(schema)


def semantic_errors(event: dict) -> list[str]:
    errors: list[str] = []
    if event.get("schema") != "sourceos.compromise_assessment.v0.1":
        return errors
    sensor_states = {sensor.get("state") for sensor in event.get("sensor_state", [])}
    status = set(event.get("status", []))
    evidence_status = event.get("evidence_quality", {}).get("status")
    if {"blind", "degraded", "missing"} & sensor_states:
        if "cannot_exclude_compromise" not in status:
            errors.append("degraded/blind/missing sensors require cannot_exclude_compromise")
        if evidence_status == "complete":
            errors.append("degraded/blind/missing sensors cannot produce complete evidence quality")
    return errors


def validate_event(event: dict) -> list[str]:
    errors: list[str] = []
    for err in sorted(validator.iter_errors(event), key=lambda e: list(e.path)):
        errors.append(err.message)
    errors.extend(semantic_errors(event))
    return errors


def main() -> int:
    failed = False
    examples = json.loads(EXAMPLES_PATH.read_text())["examples"]
    for idx, event in enumerate(examples):
        errors = validate_event(event)
        if errors:
            failed = True
            print(f"FAIL example[{idx}] {event.get('schema')}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"PASS example[{idx}] {event.get('schema')}")

    anti_patterns = json.loads(ANTI_PATH.read_text())["anti_patterns"]
    for idx, item in enumerate(anti_patterns):
        event = item["event"]
        errors = validate_event(event)
        if errors:
            print(f"PASS anti-pattern rejected[{idx}] {item['name']}")
        else:
            failed = True
            print(f"FAIL anti-pattern unexpectedly valid[{idx}] {item['name']}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
