#!/usr/bin/env python3
"""Validate .sourceos/manifest.json against SourceOSRepoManifest.json.

The register item this closes: `.sourceos/manifest.json` `policyClasses` — no code
reads the file. Every consuming repo carried the manifest and every field was
required-in-schema, but nothing loaded any of them. `policyClasses` was declared,
constrained to an enum of {low,medium,high,critical}, and answered by 16 repos —
in a form no code had ever asked for. That is the Apple diagnostic in miniature:
schema presence is not enforcement, and empty is not populated.

This script IS the reader. It validates:

  1. examples/sourceos-repo-manifest.json (the canonical positive example)
  2. .sourceos/manifest.json at this repo root (so THIS repo is asserted to
     conform to the schema it publishes — dogfooding, and a real reader).

Negative controls surround both: policyClasses:[] must be rejected, unknown
policy classes must be rejected, duplicate entries must be rejected. A
constraint with no negative control is indistinguishable from one that is
not enforced.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "SourceOSRepoManifest.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "sourceos-repo-manifest.json"
OWN_MANIFEST_PATH = REPO_ROOT / ".sourceos" / "manifest.json"


def main() -> int:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("Missing dependency: jsonschema", file=sys.stderr)
        return 1

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    failures: list[str] = []

    def case(label: str, instance: Any, should_pass: bool) -> None:
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        accepted = not errors
        if accepted != should_pass:
            want = "accepted" if should_pass else "rejected"
            got = "accepted" if accepted else f"rejected ({errors[0].message[:100]})"
            failures.append(f"{label}: expected {want}, was {got}")
        else:
            print(f"  {'ACCEPTED' if accepted else 'REJECTED'} {label}")

    # ── Positive: the shipped example must validate ────────────────────────
    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    case("examples/sourceos-repo-manifest.json", example, True)

    # ── Positive: this repo's own manifest must validate (dogfooding) ──────
    if OWN_MANIFEST_PATH.exists():
        own = json.loads(OWN_MANIFEST_PATH.read_text(encoding="utf-8"))
        case(".sourceos/manifest.json (this repo)", own, True)
    else:
        failures.append(".sourceos/manifest.json missing at repo root — the repo publishes the schema but does not conform to it")

    # ── Negative controls: the schema must REJECT these ────────────────────
    def broken(mutation) -> dict:
        b = copy.deepcopy(example)
        mutation(b)
        return b

    case("empty policyClasses (was the exact 'declared but empty' defect)",
         broken(lambda b: b.__setitem__("policyClasses", [])), False)
    case("unknown policy class",
         broken(lambda b: b.__setitem__("policyClasses", ["catastrophic"])), False)
    case("duplicate policy class entries",
         broken(lambda b: b.__setitem__("policyClasses", ["high", "high"])), False)
    case("policyClasses missing entirely (required key)",
         broken(lambda b: b.pop("policyClasses")), False)
    case("policyClasses of wrong shape (string not array)",
         broken(lambda b: b.__setitem__("policyClasses", "critical")), False)
    case("required top-level field dropped (repo)",
         broken(lambda b: b.pop("repo")), False)

    if failures:
        print(f"\n{len(failures)} failure(s):", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print("\nOK SourceOSRepoManifest: schema is populated and read; policyClasses cannot be empty or trivial")
    return 0


if __name__ == "__main__":
    sys.exit(main())
