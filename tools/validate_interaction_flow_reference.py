#!/usr/bin/env python3
"""Validate the SourceOS interaction reference-flow packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FLOW = ROOT / "examples" / "interaction-flow" / "noetica-superconscious-agentplane-agentterm.flow.json"

REQUIRED_REPOS = {
    "SourceOS-Linux/sourceos-spec": "canonical schema and generated artifact authority",
    "SocioProphet/Noetica": "browser-chat-surface",
    "SocioProphet/superconscious": "task-cognition-coordinator",
    "SocioProphet/agentplane": "execution-evidence-replay-authority",
    "SourceOS-Linux/agent-term": "terminal-operator-surface",
}

REQUIRED_AUTHORITY_KEYS = {
    "sourceosSpec",
    "noetica",
    "superconscious",
    "agentplane",
    "agentTerm",
    "policyFabric",
    "agentRegistry",
    "memoryMesh",
}

REQUIRED_FORBIDDEN_PAYLOADS = {
    "raw secrets",
    "credentials",
    "unrestricted browser history",
    "unrestricted shell output",
    "unrestricted transcripts",
    "private chain-of-thought",
    "private reasoning",
    "raw execution logs",
}

REQUIRED_VALIDATION_REF_FRAGMENTS = {
    "validate_sourceos_interaction_examples.py",
    "validate_interaction_flow_reference.py",
    "sourceos-contract-sync.yml",
    "check_sourceos_interaction_boundary.py",
    "validate_sourceos_interaction_evidence_binding.py",
}

INTERACTION_EVENT_PREFIX = "urn:srcos:interaction-event:"


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("flow reference root must be a JSON object")
    return data


def main() -> int:
    flow = load(FLOW)

    require_equal(flow.get("schemaVersion"), "sourceos.interaction-flow-reference.v0.1", "schemaVersion")
    require_prefix(flow.get("flowId"), "urn:srcos:interaction-flow:", "flowId")
    require_equal(flow.get("specVersion"), "2.0.0", "specVersion")

    sourceos_spec = require_object(flow, "sourceosSpec")
    require_equal(sourceos_spec.get("repo"), "SourceOS-Linux/sourceos-spec", "sourceosSpec.repo")
    require_nonempty(sourceos_spec.get("pinnedCommit"), "sourceosSpec.pinnedCommit")
    require_equal(sourceos_spec.get("schemaRef"), "schemas/SourceOSInteractionEvent.json", "sourceosSpec.schemaRef")

    interaction_events = require_object(flow, "interactionEvents")
    for key, value in interaction_events.items():
        require_prefix(value, INTERACTION_EVENT_PREFIX, f"interactionEvents.{key}")

    repositories = flow.get("repositories")
    if not isinstance(repositories, list):
        raise ValueError("repositories must be a list")
    by_repo = {entry.get("repo"): entry for entry in repositories if isinstance(entry, dict)}

    for repo, role in REQUIRED_REPOS.items():
        if repo not in by_repo:
            raise ValueError(f"missing repository binding: {repo}")
        entry = by_repo[repo]
        require_equal(entry.get("role"), role, f"repositories[{repo}].role")
        require_nonempty(entry.get("pinnedCommit"), f"repositories[{repo}].pinnedCommit")
        require_nonempty_list(entry.get("obligations"), f"repositories[{repo}].obligations")
        require_nonempty_list(entry.get("sourceRefs"), f"repositories[{repo}].sourceRefs")
        require_nonempty_list(entry.get("ownsAuthority"), f"repositories[{repo}].ownsAuthority")
        require_nonempty_list(entry.get("doesNotOwnAuthority"), f"repositories[{repo}].doesNotOwnAuthority")

    authority_boundaries = require_object(flow, "authorityBoundaries")
    missing_authorities = REQUIRED_AUTHORITY_KEYS - set(authority_boundaries)
    if missing_authorities:
        raise ValueError("missing authority boundaries: " + ", ".join(sorted(missing_authorities)))

    forbidden_payloads = set(flow.get("forbiddenPayloads") or [])
    missing_forbidden = REQUIRED_FORBIDDEN_PAYLOADS - forbidden_payloads
    if missing_forbidden:
        raise ValueError("missing forbidden payload classes: " + ", ".join(sorted(missing_forbidden)))

    validation_refs = flow.get("validationRefs")
    if not isinstance(validation_refs, list) or not validation_refs:
        raise ValueError("validationRefs must be a non-empty list")
    validation_text = "\n".join(str(item) for item in validation_refs)
    for fragment in REQUIRED_VALIDATION_REF_FRAGMENTS:
        if fragment not in validation_text:
            raise ValueError(f"validationRefs missing fragment: {fragment}")

    print("OK: SourceOS interaction reference flow validated")
    return 0


def require_object(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, got {actual!r}")


def require_prefix(value: Any, prefix: str, label: str) -> None:
    if not isinstance(value, str) or not value.startswith(prefix):
        raise ValueError(f"{label} must be a string starting with {prefix!r}")


def require_nonempty(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")


def require_nonempty_list(value: Any, label: str) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")


if __name__ == "__main__":
    raise SystemExit(main())
