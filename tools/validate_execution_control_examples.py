#!/usr/bin/env python3
"""Validate execution-control schema/example pairs."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "ExecutionFork.json", ROOT / "examples" / "execution_fork.json"),
    (ROOT / "schemas" / "RoutingContract.json", ROOT / "examples" / "routing_contract.json"),
    (ROOT / "schemas" / "ToolExposurePolicy.json", ROOT / "examples" / "tool_exposure_policy.json"),
    (ROOT / "schemas" / "QuotaPolicy.json", ROOT / "examples" / "quota_policy.json"),
    (ROOT / "schemas" / "RunnerGroup.json", ROOT / "examples" / "runner_group.json"),
    (ROOT / "schemas" / "ProtocolWorkbench.json", ROOT / "examples" / "protocol_workbench.json"),
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
