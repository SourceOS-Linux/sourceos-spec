#!/usr/bin/env python3
"""Validate the request-centric labor-market contract examples.

Labor is modeled as request + response + evidence + fulfillment + trust — NOT
identity + feed + attention. Covers LaborRequest (the structured ask),
LaborResponse (the proposal), FitScore (request<->response fit; never a global
human-worth score), LaborAward (the accepted arrangement + work ledger), and
TrustEvent (reputation from evidenced fulfillment).
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "LaborRequest.json", ROOT / "examples" / "labor_request.json"),
    (ROOT / "schemas" / "LaborResponse.json", ROOT / "examples" / "labor_response.json"),
    (ROOT / "schemas" / "FitScore.json", ROOT / "examples" / "fit_score.json"),
    (ROOT / "schemas" / "LaborAward.json", ROOT / "examples" / "labor_award.json"),
    (ROOT / "schemas" / "TrustEvent.json", ROOT / "examples" / "trust_event.json"),
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
