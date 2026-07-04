#!/usr/bin/env python3
"""Validate the supply-chain operational-risk contract examples.

A bank-style operational-risk framework applied to software/physical supply
chains (BIAN Operational Risk Models / FICO decisioning aligned): RiskNode
(inherent factors + control efficacy -> residual), RiskPath (accumulated node
residuals along a critical service), RiskCluster (common-mode / HHI concentration),
and RiskIndicator (KRI/KCI thresholds).
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "RiskNode.json", ROOT / "examples" / "risk_node.json"),
    (ROOT / "schemas" / "RiskPath.json", ROOT / "examples" / "risk_path.json"),
    (ROOT / "schemas" / "RiskCluster.json", ROOT / "examples" / "risk_cluster.json"),
    (ROOT / "schemas" / "RiskIndicator.json", ROOT / "examples" / "risk_indicator.json"),
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
