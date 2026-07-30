#!/usr/bin/env python3
"""Validate the MeshActionRegistry schema against its example + negative controls.

Apple's AppIntents surface is system-wide by default: any app can register intents
any other app can invoke, all queryable via one SQLite. This is our equivalent
SHAPE without the ambient trust — each participant's catalogue is referenced by a
signed manifest, the mesh registry is itself signed, and each entry carries a
capabilityRef and consentRequired discipline.

The critical property this validator asserts by rejection: `participants:[]`
must fail, `catalogDigest` cannot be a bare string, the signature block must
carry all three of keyRef/algorithm/signature or none of them. A registry with
no participants is nothing; a registry with unverifiable digests is worse than
none.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "MeshActionRegistry.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "mesh-action-registry.example.json"


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
            got = "accepted" if accepted else f"rejected ({errors[0].message[:110]})"
            failures.append(f"{label}: expected {want}, was {got}")
        else:
            print(f"  {'ACCEPTED' if accepted else 'REJECTED'} {label}")

    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    # ── Positive: the shipped example must validate ────────────────────────
    case("examples/mesh-action-registry.example.json", example, True)

    # ── Positive: signature is optional (a valid registry MAY be unsigned) ──
    unsigned = copy.deepcopy(example)
    unsigned.pop("signature", None)
    case("unsigned registry (signature is optional but consumers must treat as untrusted)", unsigned, True)

    # ── Positive: single-participant is fine ───────────────────────────────
    single = copy.deepcopy(example)
    single["participants"] = single["participants"][:1]
    case("single participant", single, True)

    # ── Negative controls ──────────────────────────────────────────────────
    def broken(mutation) -> dict:
        b = copy.deepcopy(example)
        mutation(b)
        return b

    case("empty participants — the exact 'declared but empty' shape",
         broken(lambda b: b.__setitem__("participants", [])), False)

    case("catalogDigest is a bare string, not sha256:hex",
         broken(lambda b: b["participants"][0].__setitem__("catalogDigest", "abcd1234")), False)

    case("registryDigest is a bare string, not sha256:hex",
         broken(lambda b: b.__setitem__("registryDigest", "abcd1234")), False)

    case("participant missing manifestRef (consumers cannot check policyClasses)",
         broken(lambda b: b["participants"][0].pop("manifestRef")), False)

    case("participant missing catalogDigest (a swap would be undetectable)",
         broken(lambda b: b["participants"][0].pop("catalogDigest")), False)

    case("signature block missing algorithm",
         broken(lambda b: b["signature"].pop("algorithm")), False)

    case("unknown signature algorithm",
         broken(lambda b: b["signature"].__setitem__("algorithm", "md5")), False)

    case("repo identifier not owner/repo shape",
         broken(lambda b: b["participants"][0].__setitem__("repo", "just-a-repo")), False)

    case("generatedAt not a date-time",
         broken(lambda b: b.__setitem__("generatedAt", "yesterday")), False)

    case("type discriminator wrong",
         broken(lambda b: b.__setitem__("type", "WhateverElseRegistry")), False)

    case("id URN not the mesh-action-registry namespace",
         broken(lambda b: b.__setitem__("id", "urn:srcos:something:x")), False)

    # implementsAbb — new field. Absent is fine (participant claims no ABB slots); present must be
    # non-empty when set, and each entry must match the ABB.NN pattern.
    print("  implementsAbb")
    case("implementsAbb absent (participant claims no ABB slots)",
         broken(lambda b: b["participants"][0].pop("implementsAbb", None)), True)
    case("implementsAbb with a valid ABB claim",
         broken(lambda b: b["participants"][0].__setitem__("implementsAbb", ["ABB.03"])), True)
    case("implementsAbb with multiple valid ABB claims",
         broken(lambda b: b["participants"][0].__setitem__("implementsAbb", ["ABB.03", "ABB.07"])), True)
    case("implementsAbb non-conforming pattern (bare number)",
         broken(lambda b: b["participants"][0].__setitem__("implementsAbb", ["3"])), False)
    case("implementsAbb non-conforming pattern (three digits)",
         broken(lambda b: b["participants"][0].__setitem__("implementsAbb", ["ABB.003"])), False)
    case("implementsAbb with duplicate ABB entries (uniqueItems)",
         broken(lambda b: b["participants"][0].__setitem__("implementsAbb", ["ABB.03", "ABB.03"])), False)
    case("implementsAbb wrong namespace",
         broken(lambda b: b["participants"][0].__setitem__("implementsAbb", ["ARC.03"])), False)

    case("undeclared property on a participant (schema is closed)",
         broken(lambda b: b["participants"][0].__setitem__("zzUnknown", "leak")), False)

    if failures:
        print(f"\n{len(failures)} failure(s):", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print("\nOK MeshActionRegistry: participants cannot be empty, digests cannot be trivial, signature block is all-or-nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
