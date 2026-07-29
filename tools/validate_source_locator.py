#!/usr/bin/env python3
"""Validate that EvidenceAtom.sourceLocator cannot claim a grade it does not carry.

`payloadDigest` answers "is this the same payload". It cannot answer "which passage
did this come from", so before sourceLocator existed an EvidenceAtom identified its
source but never its position: a reader could not check a claim without re-deriving
the whole document.

The point of the enum is that the three grades are NOT interchangeable. A chunk
ordinal resolves only if the chunker is re-run identically; a character span resolves
against the extraction directly. Recording the weaker one as though it were the
stronger is the failure this file exists to prevent, so most of the checks below are
negative controls — a constraint with no negative control is indistinguishable from
one that is not enforced.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = REPO_ROOT / "schemas" / "EvidenceAtom.json"

BASE = {
    "id": "urn:srcos:evidence:a1b2c3",
    "type": "EvidenceAtom",
    "specVersion": "1.0.0",
    "patternRef": "urn:srcos:pattern:p1",
    "principal": "urn:srcos:principal:u1",
    "observedAt": "2026-07-29T00:00:00Z",
    "channel": "doc_access",
    "payloadDigest": "sha256:" + "a" * 64,
}
DIGEST = "sha256:" + "b" * 64


def main() -> int:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("Missing dependency: jsonschema", file=sys.stderr)
        return 1

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    failures: list[str] = []

    def case(label: str, locator: dict | None, should_pass: bool) -> None:
        instance = dict(BASE)
        if locator is not None:
            instance["sourceLocator"] = locator
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        accepted = not errors
        if accepted != should_pass:
            want = "accepted" if should_pass else "rejected"
            got = "accepted" if accepted else f"rejected ({errors[0].message})"
            failures.append(f"{label}: expected {want}, was {got}")
        else:
            print(f"  {'ACCEPTED' if accepted else 'REJECTED'} {label}")

    # Admissible shapes.
    case("no locator — silent about whether a position was even available", None, True)
    case("document-only", {"provenanceVersion": "document-only", "sourceRef": "d1"}, True)
    case("chunk-ordinal carrying its index",
         {"provenanceVersion": "chunk-ordinal", "sourceRef": "d1", "chunkIndex": 12}, True)
    case("character-span carrying offsets and the extraction they index",
         {"provenanceVersion": "character-span", "sourceRef": "d1",
          "start": 120, "end": 240, "extractionDigest": DIGEST}, True)
    case("character-span with an optional page",
         {"provenanceVersion": "character-span", "sourceRef": "d1", "page": 3,
          "start": 120, "end": 240, "extractionDigest": DIGEST}, True)

    # Negative controls: a grade asserted without what makes it true.
    case("chunk-ordinal with no chunkIndex",
         {"provenanceVersion": "chunk-ordinal", "sourceRef": "d1"}, False)
    case("character-span with no offsets",
         {"provenanceVersion": "character-span", "sourceRef": "d1", "extractionDigest": DIGEST}, False)
    case("character-span with only a start",
         {"provenanceVersion": "character-span", "sourceRef": "d1", "start": 120,
          "extractionDigest": DIGEST}, False)
    case("character-span with no extractionDigest — offsets unverifiable against a re-extraction",
         {"provenanceVersion": "character-span", "sourceRef": "d1", "start": 120, "end": 240}, False)
    case("negative offset", {"provenanceVersion": "character-span", "sourceRef": "d1",
                             "start": -1, "end": 240, "extractionDigest": DIGEST}, False)
    case("page 0 — pages are 1-based", {"provenanceVersion": "character-span", "sourceRef": "d1",
                                        "page": 0, "start": 1, "end": 2, "extractionDigest": DIGEST}, False)
    case("no sourceRef — offsets relative to nothing",
         {"provenanceVersion": "character-span", "start": 1, "end": 2, "extractionDigest": DIGEST}, False)
    case("unknown grade", {"provenanceVersion": "byte-range", "sourceRef": "d1"}, False)
    case("undeclared field", {"provenanceVersion": "document-only", "sourceRef": "d1", "line": 4}, False)

    if failures:
        print(f"\n{len(failures)} failure(s):", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("\nOK sourceLocator: a provenance grade cannot be claimed without the fields that justify it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
