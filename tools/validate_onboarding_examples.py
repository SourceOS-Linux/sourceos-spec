#!/usr/bin/env python3
"""Validate SourceOS/SociOS onboarding control-plane schema/example pairs."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "WorkspaceScope.json", ROOT / "examples" / "workspacescope.json"),
    (ROOT / "schemas" / "TrustMode.json", ROOT / "examples" / "trustmode.read_only_analyst.json"),
    (ROOT / "schemas" / "CapabilityPack.json", ROOT / "examples" / "capabilitypack.repo_release_prep.json"),
    (ROOT / "schemas" / "ConnectorActionScope.json", ROOT / "examples" / "connectoractionscope.github_read_only.json"),
    (ROOT / "schemas" / "AutomationTemplate.json", ROOT / "examples" / "automationtemplate.yesterday_git_activity.json"),
    (ROOT / "schemas" / "OnboardingReceipt.json", ROOT / "examples" / "onboardingreceipt.first_run_read_only.json"),
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
