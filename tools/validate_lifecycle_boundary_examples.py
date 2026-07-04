#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SCHEMA = ROOT / "schemas" / "runtime-effect-decision.v1.1.json"
GRANT_SCHEMA = ROOT / "schemas" / "grant-state-decision.v1.1.json"
RUNTIME_VALID = ROOT / "examples" / "runtime-effect-decision.valid.json"
RUNTIME_INVALID_AUTHORITY = ROOT / "examples" / "runtime-effect-decision.authority-mutated.invalid.json"
GRANT_VALID = ROOT / "examples" / "grant-state-decision.valid.json"
GRANT_INVALID_MISSING_AUTH = ROOT / "examples" / "grant-state-decision.missing-authorization.invalid.json"


class ValidationError(Exception):
    pass


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValidationError(f"{path}: expected JSON object")
    return payload


def validate_json_schema(schema_path: Path, instance_path: Path) -> dict[str, Any]:
    schema = load(schema_path)
    jsonschema.validators.validator_for(schema).check_schema(schema)
    instance = load(instance_path)
    jsonschema.validate(instance, schema)
    return instance


def validate_runtime_effect(instance: dict[str, Any]) -> None:
    if instance.get("decision_kind") != "runtime-effect-decision":
        raise ValidationError("runtime effect decision_kind mismatch")
    if instance.get("authority_mutation_performed") is not False:
        raise ValidationError("runtime effect decisions must not mutate authority")
    if instance.get("ledger_write_performed") is not False:
        raise ValidationError("runtime effect decisions must not write ledger records")
    effect = instance.get("runtime_effect")
    status = instance.get("effect_status")
    scope = instance.get("effect_scope", {})
    if effect in {"allow_dispatch", "export_ref_only"} and status not in {"admitted", "partial"}:
        raise ValidationError(f"{effect} requires admitted or partial status")
    if effect in {"block", "quarantine", "deny_dispatch"} and status == "admitted":
        raise ValidationError(f"{effect} cannot report admitted status")
    if scope.get("side_effecting") is True and effect in {"metadata_only", "export_ref_only", "noop"}:
        raise ValidationError("metadata/ref/noop runtime effects cannot be side-effecting")
    if instance.get("grant_state_decision_ref") and instance.get("authority_mutation_performed") is not False:
        raise ValidationError("grant_state_decision_ref is a reference, not inline authority mutation")


def validate_grant_state(instance: dict[str, Any]) -> None:
    if instance.get("decision_kind") != "grant-state-decision":
        raise ValidationError("grant state decision_kind mismatch")
    if not instance.get("authorization_policy_ref"):
        raise ValidationError("grant state decisions require authorization_policy_ref")
    if not instance.get("authorization_evidence_refs"):
        raise ValidationError("grant state decisions require authorization_evidence_refs")
    decision = instance.get("authority_decision")
    effects = instance.get("authority_effects", {})
    changed = any(value != "unchanged" for value in effects.values())
    if decision == "unchanged" and changed:
        raise ValidationError("unchanged grant state decision requires unchanged authority_effects")
    if decision != "unchanged" and not changed:
        raise ValidationError("changed grant state decision requires changed authority_effects")
    if decision == "revoked" and any(value != "revoked" for value in effects.values()):
        raise ValidationError("revoked grant state decision requires all authority_effects revoked")
    if decision == "restored" and instance.get("restoration_allowed") is not True:
        raise ValidationError("restored grant state decision requires restoration_allowed=true")


def expect_invalid(schema_path: Path, instance_path: Path, semantic_validator) -> None:
    try:
        instance = validate_json_schema(schema_path, instance_path)
        semantic_validator(instance)
    except Exception:
        return
    raise ValidationError(f"invalid fixture unexpectedly validated: {instance_path.relative_to(ROOT)}")


def main() -> int:
    runtime = validate_json_schema(RUNTIME_SCHEMA, RUNTIME_VALID)
    validate_runtime_effect(runtime)
    grant = validate_json_schema(GRANT_SCHEMA, GRANT_VALID)
    validate_grant_state(grant)
    expect_invalid(RUNTIME_SCHEMA, RUNTIME_INVALID_AUTHORITY, validate_runtime_effect)
    expect_invalid(GRANT_SCHEMA, GRANT_INVALID_MISSING_AUTH, validate_grant_state)
    print(json.dumps({"ok": True, "checks": [
        str(RUNTIME_VALID.relative_to(ROOT)),
        str(GRANT_VALID.relative_to(ROOT)),
        str(RUNTIME_INVALID_AUTHORITY.relative_to(ROOT)),
        str(GRANT_INVALID_MISSING_AUTH.relative_to(ROOT)),
    ]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
