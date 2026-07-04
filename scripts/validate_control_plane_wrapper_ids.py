#!/usr/bin/env python3
"""Validate that control-plane canonical wrapper `$id` values resolve correctly.

This is a portability guardrail:

- Control-plane wrapper schemas live in `schemas/control-plane/*.json` and have
  canonical `$id` values under `https://schemas.srcos.ai/v2/control-plane/...`.
- The wrappers `allOf`-wrap legacy `*.schema.json` files.

We validate **two properties**:

1) Wrapper `$id` values resolve from the local schema registry.
2) Wrapper-internal `$ref` targets resolve (e.g., the legacy `*.schema.json` files).

Additionally, we run one end-to-end validation using IncidentEvent (minimal instance).

Exit:
- 0 on success
- 1 on failure
"""

from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect_refs(obj) -> set[str]:
    refs: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                refs.add(v)
            refs |= collect_refs(v)
    elif isinstance(obj, list):
        for it in obj:
            refs |= collect_refs(it)
    return refs


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    schema_dir = repo / "schemas"
    cp_dir = schema_dir / "control-plane"

    registry: dict[str, dict] = {}

    # Load top-level schemas
    for p in glob.glob(str(schema_dir / "*.json")):
        s = load_json(p)
        sid = s.get("$id")
        if sid:
            registry[sid] = s
        base = os.path.basename(p)
        registry[base] = s
        registry[f"./{base}"] = s

    # Load control-plane schemas (wrappers + legacy)
    for p in glob.glob(str(cp_dir / "*.json")) + glob.glob(str(cp_dir / "*.schema.json")):
        s = load_json(p)
        sid = s.get("$id")
        if sid:
            registry[sid] = s
        base = os.path.basename(p)
        registry[base] = s
        registry[f"./{base}"] = s

    from jsonschema import RefResolver, validate

    base_uri = f"file://{schema_dir.resolve()}/"

    class LocalRegistry(RefResolver):
        def resolve_remote(self, uri):
            clean = uri.split("#")[0]
            if clean in registry:
                return registry[clean]
            name = os.path.basename(clean)
            if name in registry:
                return registry[name]
            return super().resolve_remote(uri)

    resolver = LocalRegistry(base_uri=base_uri, referrer={}, store=registry)

    wrappers = [
        "https://schemas.srcos.ai/v2/control-plane/IncidentEvent.json",
        "https://schemas.srcos.ai/v2/control-plane/MeshSkill.json",
        "https://schemas.srcos.ai/v2/control-plane/EnrollmentToken.json",
        "https://schemas.srcos.ai/v2/control-plane/SkillExecutionEvent.json",
    ]

    # 1) Resolution checks (wrapper id + internal refs)
    for wid in wrappers:
        try:
            schema = resolver.resolve_remote(wid)
        except Exception as e:
            print(f"FAIL: cannot resolve wrapper $id: {wid}: {e}", file=sys.stderr)
            return 1

        if isinstance(schema, dict):
            # Ensure internal refs resolve (allOf wraps legacy schema)
            for r in sorted(collect_refs(schema)):
                try:
                    resolver.resolve_remote(r)
                except Exception as e:
                    print(f"FAIL: wrapper {wid} contains unresolved $ref {r}: {e}", file=sys.stderr)
                    return 1

        print(f"OK: wrapper resolved: {wid}")

    # 2) End-to-end instance validation (IncidentEvent)
    incident_wrapper = wrappers[0]

    schema_ref = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": incident_wrapper,
    }

    instance = {
        "event_id": "evt_ci_0001",
        "event_name": "incident.freeze",
        "occurred_at": "2026-04-19T00:00:00Z",
        "actor": {"kind": "service", "id": "ci"},
        "status": "succeeded",
    }

    try:
        validate(instance, schema_ref, resolver=resolver)
    except Exception as e:
        print(f"FAIL: IncidentEvent wrapper end-to-end validation failed: {e}", file=sys.stderr)
        return 1

    print("OK: IncidentEvent wrapper end-to-end validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
