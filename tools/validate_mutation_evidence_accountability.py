#!/usr/bin/env python3
"""Validate SourceOS Mutation and Evidence Accountability examples.

The validator checks two schema surfaces:

1. The initial event-family bundle in MutationEvidenceAccountability.schema.json.
2. The umbrella primitive bundle in MutationEvidenceUmbrellaPrimitives.schema.json.

It also enforces semantic guardrails that JSON Schema alone should not carry:

- degraded/blind/missing sensors cannot clear compromise;
- browser write pressure cannot be blamed on extensions when the visible
  extension inventory is empty, unless hidden/system/policy add-on evidence
  explicitly allows it;
- delegated I/O requires a meaningful multi-actor chain;
- diagnostic observer-effect writes cannot grant clearance when evidence is
  redacted/partial;
- archive extraction requires path-boundary and cleanup accounting.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover
    raise SystemExit("jsonschema is required: python -m pip install jsonschema") from exc

ROOT = Path(__file__).resolve().parents[1]
BASE_SCHEMA_PATH = ROOT / "schemas" / "MutationEvidenceAccountability.schema.json"
BASE_EXAMPLES_PATH = ROOT / "examples" / "mutation-evidence-accountability.examples.json"
BASE_ANTI_PATH = ROOT / "fixtures" / "anti-patterns" / "mutation-evidence-accountability.invalid.json"

UMBRELLA_SCHEMA_PATH = ROOT / "schemas" / "MutationEvidenceUmbrellaPrimitives.schema.json"
UMBRELLA_EXAMPLES_PATH = ROOT / "examples" / "mutation-evidence-umbrella.examples.json"
UMBRELLA_ANTI_PATH = ROOT / "fixtures" / "anti-patterns" / "mutation-evidence-umbrella.invalid.json"

base_validator = jsonschema.Draft202012Validator(json.loads(BASE_SCHEMA_PATH.read_text()))
umbrella_validator = jsonschema.Draft202012Validator(json.loads(UMBRELLA_SCHEMA_PATH.read_text()))


def _schema_errors(validator: jsonschema.Draft202012Validator, event: dict[str, Any]) -> list[str]:
    return [err.message for err in sorted(validator.iter_errors(event), key=lambda e: list(e.path))]


def _actor_roles(event: dict[str, Any]) -> set[str]:
    return {actor.get("role", "") for actor in event.get("actor_chain", [])}


def semantic_errors_base(event: dict[str, Any]) -> list[str]:
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


def semantic_errors_umbrella(event: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if event.get("schema") != "sourceos.mutation_evidence.umbrella.v0.1":
        return errors

    primitive = event.get("primitive")
    subtype = event.get("subtype")
    evidence = event.get("evidence_quality", {})
    evidence_status = evidence.get("status")
    missing_fields = set(evidence.get("missing_fields", []))
    roles = _actor_roles(event)

    if subtype == "browser_write":
        browser = event.get("browser", {})
        if (
            browser.get("extension_inventory_state") == "none_visible"
            and browser.get("browser_actor_class") == "browser_extension_storage"
            and browser.get("primary_extension_cause_allowed") is True
        ):
            errors.append("browser write cannot be extension-primary when extension_inventory_state=none_visible")

    if subtype == "delegated_io":
        required_roles = {"origin_actor", "requesting_actor", "execution_actor", "storage_actor"}
        missing_roles = sorted(required_roles - roles)
        if missing_roles:
            errors.append(f"delegated_io missing required actor roles: {', '.join(missing_roles)}")
        if not event.get("causal_parents"):
            errors.append("delegated_io requires at least one causal parent")

    if subtype == "diagnostic_self_noise":
        pipeline = event.get("evidence_pipeline", {})
        if pipeline.get("clearance_allowed") is True and (
            evidence_status != "complete" or missing_fields or pipeline.get("redacted", 0) > 0
        ):
            errors.append("diagnostic self-noise with partial/redacted evidence cannot allow clearance")

    if subtype == "archive_extraction":
        obj = event.get("object", {})
        archive = event.get("archive", {})
        if obj.get("path_class") == "unknown":
            errors.append("archive_extraction requires a known path_class")
        if "cleanup_policy" not in archive:
            errors.append("archive_extraction requires cleanup_policy accounting")
        if evidence_status == "complete" and (archive.get("quarantine_state") == "unknown" or not event.get("causal_parents")):
            errors.append("archive_extraction cannot be complete without quarantine state and causal parent")

    if primitive == "EvidencePipelineReceipt" and subtype == "compromise_assessment":
        pipeline = event.get("evidence_pipeline", {})
        if pipeline.get("clearance_allowed") is True and evidence.get("sensor_state") in {"degraded", "blind", "missing"}:
            errors.append("evidence pipeline cannot clear compromise with degraded/blind/missing sensors")

    return errors


def validate_base_event(event: dict[str, Any]) -> list[str]:
    return _schema_errors(base_validator, event) + semantic_errors_base(event)


def validate_umbrella_event(event: dict[str, Any]) -> list[str]:
    return _schema_errors(umbrella_validator, event) + semantic_errors_umbrella(event)


def _validate_examples(label: str, path: Path, validator_fn) -> bool:
    failed = False
    examples = json.loads(path.read_text())["examples"]
    for idx, event in enumerate(examples):
        errors = validator_fn(event)
        if errors:
            failed = True
            print(f"FAIL {label} example[{idx}] {event.get('schema')} {event.get('subtype', '')}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"PASS {label} example[{idx}] {event.get('schema')} {event.get('subtype', '')}")
    return failed


def _validate_anti_patterns(label: str, path: Path, validator_fn) -> bool:
    failed = False
    anti_patterns = json.loads(path.read_text())["anti_patterns"]
    for idx, item in enumerate(anti_patterns):
        event = item["event"]
        errors = validator_fn(event)
        if errors:
            print(f"PASS {label} anti-pattern rejected[{idx}] {item['name']}")
        else:
            failed = True
            print(f"FAIL {label} anti-pattern unexpectedly valid[{idx}] {item['name']}")
    return failed


def main() -> int:
    failed = False
    failed |= _validate_examples("base", BASE_EXAMPLES_PATH, validate_base_event)
    failed |= _validate_anti_patterns("base", BASE_ANTI_PATH, validate_base_event)
    failed |= _validate_examples("umbrella", UMBRELLA_EXAMPLES_PATH, validate_umbrella_event)
    failed |= _validate_anti_patterns("umbrella", UMBRELLA_ANTI_PATH, validate_umbrella_event)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
