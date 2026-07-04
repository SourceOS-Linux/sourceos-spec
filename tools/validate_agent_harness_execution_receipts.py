#!/usr/bin/env python3
"""Validate SourceOS Agent Harness execution receipt examples.

Uses only the Python standard library and implements the small JSON Schema subset
used by schemas/AgentHarnessExecutionReceipts.json: required, properties,
additionalProperties=false, const, enum, primitive type checks, arrays, and
nested object properties.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "AgentHarnessExecutionReceipts.json"
EXAMPLE = ROOT / "examples" / "agent-harness-execution-receipts.example.json"


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid json in {path}: {exc}") from exc


def json_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def type_matches(value: Any, expected: str) -> bool:
    actual = json_type_name(value)
    if expected == "number":
        return actual in {"integer", "number"}
    return actual == expected


def validate(schema: dict[str, Any], value: Any, path: str = "$") -> None:
    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{path}: expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{path}: {value!r} not in enum {schema['enum']!r}")

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(type_matches(value, item) for item in expected_types):
            raise ValidationError(
                f"{path}: expected type {expected_types!r}, got {json_type_name(value)!r}"
            )

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ValidationError(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                raise ValidationError(f"{path}: unexpected properties {extra!r}")

        additional = schema.get("additionalProperties")
        for key, item in value.items():
            child_schema = properties.get(key)
            if child_schema is None and isinstance(additional, dict):
                child_schema = additional
            if child_schema is not None:
                validate(child_schema, item, f"{path}.{key}")

    if isinstance(value, list):
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                validate(item_schema, item, f"{path}[{index}]")


def semantic_checks(example: dict[str, Any]) -> None:
    runtime = example["localAgentRuntimeReceipt"]
    if runtime["networkProfile"] not in {"local-only", "offline", "corporate-firewall", "approved-internet"}:
        raise ValidationError("localAgentRuntimeReceipt.networkProfile must be an allowed SourceOS posture")
    if runtime["hostMutationPolicy"] == "preapproved" and not runtime.get("policyAdmissionRef"):
        raise ValidationError("preapproved host mutation requires policy admission ref")

    shell = example["shellReceiptEvent"]
    if shell["exitCode"] != 0 and shell["replayEligible"]:
        raise ValidationError("failed shell command should not be marked replayEligible in the baseline example")

    browser = example["browserActionReceipt"]
    if browser["credentialUse"] and browser["sideEffectClass"] != "credential":
        raise ValidationError("credentialUse=true requires sideEffectClass=credential")

    mutation = example["hostMutationBoundaryReceipt"]
    if mutation["mutatedHost"] and mutation["mode"] != "live":
        raise ValidationError("mutatedHost=true requires mode=live")
    if mutation["mode"] == "live" and not mutation.get("approvalRef"):
        raise ValidationError("live host mutation requires approvalRef")

    artifact = example["downloadArtifactReceipt"]
    if not artifact["artifactRef"].startswith("artifact://sha256/"):
        raise ValidationError("downloadArtifactReceipt.artifactRef must use artifact://sha256/<digest>")
    if artifact["sha256"] not in artifact["artifactRef"]:
        raise ValidationError("downloadArtifactReceipt.artifactRef must contain the declared sha256 digest")


def main() -> int:
    try:
        schema = load_json(SCHEMA)
        example = load_json(EXAMPLE)
        validate(schema, example)
        semantic_checks(example)
    except ValidationError as exc:
        print(f"Agent Harness execution receipts validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"ok: {EXAMPLE.relative_to(ROOT)} validates against {SCHEMA.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
