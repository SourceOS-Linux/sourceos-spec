#!/usr/bin/env python3
"""Validate the agentic operating-system contract examples against their schemas.

Covers the objects the agentic OS coordinates: Opportunity (objective), AgentPod
(the staffing unit whose URN is also referenced by AgentMachineReceipt.agentPodRef),
SharedLibrary, ReadinessScore, CaptureCadence, and CaptureDelta.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "AgentPod.json", ROOT / "examples" / "agent_pod.json"),
    (ROOT / "schemas" / "SharedLibrary.json", ROOT / "examples" / "shared_library.json"),
    (ROOT / "schemas" / "ReadinessScore.json", ROOT / "examples" / "readiness_score.json"),
    (ROOT / "schemas" / "CaptureDelta.json", ROOT / "examples" / "capture_delta.json"),
    (ROOT / "schemas" / "CaptureCadence.json", ROOT / "examples" / "capture_cadence.json"),
    (ROOT / "schemas" / "Opportunity.json", ROOT / "examples" / "opportunity.json"),
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
