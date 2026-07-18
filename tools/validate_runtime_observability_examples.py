#!/usr/bin/env python3
"""Validate runtime observability and capability governance examples.

This validator intentionally goes beyond simple JSON Schema validation. It also
checks the properties that matter for evidence discipline: unique IDs, required
cross-reference shapes, non-empty evidence references, timestamp parseability,
and no raw workspace path storage for GitWorkspaceState examples.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    ("schemas/CapabilityLedger.json", "examples/capabilityledger.json"),
    ("schemas/BrowserAutomationReceipt.json", "examples/browserautomationreceipt.json"),
    ("schemas/GitWorkspaceState.json", "examples/gitworkspacestate.json"),
    ("schemas/OrphanEventReceipt.json", "examples/orphaneventreceipt.json"),
    ("schemas/RuntimeInstallReceipt.json", "examples/runtimeinstallreceipt.json"),
]

EXPECTED_IDS = {
    "CapabilityLedger": "urn:srcos:capability-ledger:",
    "BrowserAutomationReceipt": "urn:srcos:receipt:browser-automation:",
    "GitWorkspaceState": "urn:srcos:git-workspace-state:",
    "OrphanEventReceipt": "urn:srcos:receipt:orphan-event:",
    "RuntimeInstallReceipt": "urn:srcos:receipt:runtime-install:",
}

TIMESTAMP_KEYS = {
    "capturedAt",
    "startedAt",
    "finishedAt",
    "revokedAt",
    "observedAt",
    "reconciledAt",
    "quarantinedAt",
    "expiresAt",
    "resolvedAt",
}


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def parse_timestamp(value: str, *, where: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AssertionError(f"Invalid timestamp at {where}: {value}") from exc


def validate_timestamps(doc: dict[str, Any], example_path: str) -> None:
    def visit(value: Any, path: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}"
                if key in TIMESTAMP_KEYS and child is not None:
                    if not isinstance(child, str):
                        raise AssertionError(f"Timestamp field is not string at {example_path}:{child_path}")
                    parse_timestamp(child, where=f"{example_path}:{child_path}")
                visit(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")

    visit(doc)


def validate_common(doc: dict[str, Any], example_path: str, seen_ids: set[str]) -> None:
    doc_type = doc.get("type")
    doc_id = doc.get("id")
    if doc_type not in EXPECTED_IDS:
        raise AssertionError(f"Unexpected type in {example_path}: {doc_type}")
    if not isinstance(doc_id, str) or not doc_id.startswith(EXPECTED_IDS[doc_type]):
        raise AssertionError(f"Invalid id prefix in {example_path}: {doc_id}")
    if doc_id in seen_ids:
        raise AssertionError(f"Duplicate id in examples: {doc_id}")
    seen_ids.add(doc_id)

    evidence = doc.get("evidenceRefs")
    if not isinstance(evidence, list) or not evidence:
        raise AssertionError(f"Missing non-empty evidenceRefs in {example_path}")

    policy = doc.get("policyDecisionRef")
    if not isinstance(policy, str) or not policy.startswith("urn:srcos:decision:"):
        raise AssertionError(f"Invalid policyDecisionRef in {example_path}: {policy}")

    validate_timestamps(doc, example_path)


def validate_specific(doc: dict[str, Any], example_path: str) -> None:
    doc_type = doc["type"]

    if doc_type in {"BrowserAutomationReceipt", "GitWorkspaceState", "RuntimeInstallReceipt"}:
        session_ref = doc.get("sessionRef")
        if not isinstance(session_ref, str) or not session_ref.startswith("urn:srcos:session:"):
            raise AssertionError(f"Invalid sessionRef in {example_path}: {session_ref}")
        ledger_ref = doc.get("capabilityLedgerRef")
        if not isinstance(ledger_ref, str) or not ledger_ref.startswith("urn:srcos:capability-ledger:"):
            raise AssertionError(f"Invalid capabilityLedgerRef in {example_path}: {ledger_ref}")

    if doc_type == "GitWorkspaceState":
        path_evidence = doc.get("pathEvidence", {})
        if path_evidence.get("rawPathStored") is not False:
            raise AssertionError("GitWorkspaceState must not store raw paths")

    if doc_type == "BrowserAutomationReceipt":
        started_at = doc.get("startedAt")
        captured_at = doc.get("capturedAt")
        revoked_at = doc.get("revokedAt")
        if started_at and captured_at:
            start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            captured = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
            if captured < start:
                raise AssertionError("BrowserAutomationReceipt capturedAt precedes startedAt")
        if revoked_at:
            revoked = datetime.fromisoformat(revoked_at.replace("Z", "+00:00"))
            start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            if revoked < start:
                raise AssertionError("BrowserAutomationReceipt revokedAt precedes startedAt")

    if doc_type == "OrphanEventReceipt":
        resolution = doc.get("sessionResolution", {})
        state = resolution.get("state")
        if state == "recovered" and not resolution.get("recoveredSessionRef"):
            raise AssertionError("Recovered orphan event requires recoveredSessionRef")
        if state == "quarantined" and not resolution.get("quarantinedAt"):
            raise AssertionError("Quarantined orphan event requires quarantinedAt")

    if doc_type == "RuntimeInstallReceipt":
        artifacts = doc.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise AssertionError("RuntimeInstallReceipt requires at least one artifact")
        if doc.get("logMode") != "compact_receipt_ref":
            raise AssertionError("RuntimeInstallReceipt canonical example must use compact_receipt_ref")


def main() -> None:
    seen_ids: set[str] = set()
    for schema_path, example_path in PAIRS:
        schema = load_json(schema_path)
        example = load_json(example_path)
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(instance=example, schema=schema)
        validate_common(example, example_path, seen_ids)
        validate_specific(example, example_path)
        print(f"OK: {example_path} -> {schema_path}")

    print("OK: runtime observability examples")


if __name__ == "__main__":
    main()
