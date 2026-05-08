#!/usr/bin/env python3
"""Validate runtime-causality schema/example pairs."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "RetryLoopFingerprint.json", ROOT / "examples" / "retry_loop_fingerprint.json"),
    (ROOT / "schemas" / "SecurityVerdictState.json", ROOT / "examples" / "security_verdict_state.json"),
    (ROOT / "schemas" / "NetworkTruthState.json", ROOT / "examples" / "network_truth_state.json"),
    (ROOT / "schemas" / "BrowserLaunchTransaction.json", ROOT / "examples" / "browser_launch_transaction.json"),
    (ROOT / "schemas" / "RuntimeIdentityGraph.json", ROOT / "examples" / "runtime_identity_graph.json"),
    (ROOT / "schemas" / "DesktopServiceBrokerState.json", ROOT / "examples" / "desktop_service_broker_state.json"),
    (ROOT / "schemas" / "MaintenanceEpoch.json", ROOT / "examples" / "maintenance_epoch.json"),
    (ROOT / "schemas" / "RuntimeRegistryIntegrityRecord.json", ROOT / "examples" / "runtime_registry_integrity_record.json"),
    (ROOT / "schemas" / "BootSessionPhaseState.json", ROOT / "examples" / "boot_session_phase_state.json"),
    (ROOT / "schemas" / "DiagnosticStormRecord.json", ROOT / "examples" / "diagnostic_storm_record.json"),
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
