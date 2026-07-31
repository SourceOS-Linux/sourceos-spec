#!/usr/bin/env python3
"""Validate the agent-system JSON-LD vocabulary seed (T0-3).

Asserts the vocabulary is well-formed JSON-LD and that every required term is
present AND complete (@type + rdfs:label + rdfs:comment). A term declared
without a label or comment is a silent gap, so it is rejected here rather than
shipped.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = REPO_ROOT / "semantic" / "agent-system-vocabulary.jsonld"
BASE_NS = "https://spec.sourceos.dev/vocab/agent-system#"
REQUIRED_TERMS = {
    "AgentClass",
    "PermissionFlag",
    "ManagedSpace",
    "SeamDefinition",
    "CapabilityException",
    "BundleIdentity",
}
REQUIRED_FIELDS = {"@type", "rdfs:label", "rdfs:comment"}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> int:
    try:
        doc = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{VOCAB_PATH.name} is not valid JSON: {exc}")

    ctx = doc.get("@context")
    if not isinstance(ctx, dict) or ctx.get("agentsys") != BASE_NS:
        fail(f"@context must map agentsys -> {BASE_NS}")

    graph = doc.get("@graph")
    if not isinstance(graph, list) or not graph:
        fail("@graph must be a non-empty array of term definitions")

    seen = {}
    for node in graph:
        if not isinstance(node, dict):
            fail("each @graph entry must be an object")
        node_id = str(node.get("@id", ""))
        if not node_id.startswith("agentsys:"):
            fail(f"term @id must be in the agentsys namespace, got {node_id!r}")
        term = node_id.split(":", 1)[1]
        missing = REQUIRED_FIELDS - set(node)
        if missing:
            fail(f"term {term} is missing required field(s): {sorted(missing)}")
        for field in ("rdfs:label", "rdfs:comment"):
            if not str(node.get(field, "")).strip():
                fail(f"term {term} has an empty {field}")
        seen[term] = node

    missing_terms = REQUIRED_TERMS - set(seen)
    if missing_terms:
        fail(f"missing required terms: {sorted(missing_terms)}")

    print(
        f"OK: agent-system vocabulary valid; {len(REQUIRED_TERMS)} terms defined "
        f"with @type + rdfs:label + rdfs:comment ({', '.join(sorted(REQUIRED_TERMS))})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
