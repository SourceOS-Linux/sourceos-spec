#!/usr/bin/env python3
"""Validate SeamDefinition: typed architectural-seam registry objects (T0-2).

A seam names an ungated boundary that is an attack surface. The invariants that
make a seam actionable are asserted BY REJECTION — a control never observed
refusing is indistinguishable from no control.

Positive: every examples/seam-definition*.json validates; the set covers >= 3
distinct seams.

Negative (each fed to the SCHEMA; each MUST be rejected):
  R1  implementation_status not one of the four allowed values
  R2  empty gate_requirements (a seam with no stated gate is not actionable)
  R3  missing seam_id (no stable identity)
  R4  malformed seam_id (not SEAM-###)
  R5  priority outside {critical, high, medium}
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - installed by the Makefile target
    print("FAIL: jsonschema is not installed; run `python3 -m pip install jsonschema`")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "SeamDefinition.json"
EXAMPLE_GLOB = "seam-definition*.json"
EXPECTED_STATUS = {"open", "designed", "partially_gated", "implemented"}


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> int:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    status_enum = (
        schema.get("properties", {}).get("implementation_status", {}).get("enum")
        if isinstance(schema, dict)
        else None
    )
    if not isinstance(status_enum, list) or set(status_enum) != EXPECTED_STATUS:
        fail(f"implementation_status enum must be exactly {sorted(EXPECTED_STATUS)}")

    example_paths = sorted((REPO_ROOT / "examples").glob(EXAMPLE_GLOB))
    if not example_paths:
        fail(f"no example files matched examples/{EXAMPLE_GLOB}")

    seam_ids = set()
    for path in example_paths:
        seam = load(path)
        if not isinstance(seam, dict):
            fail(f"{path.name}: each example must be a single SeamDefinition object")
        errors = sorted(validator.iter_errors(seam), key=lambda e: list(e.path))
        if errors:
            lines = [f"{path.name} ({seam.get('seam_id', '?')}) failed validation:"]
            for e in errors:
                loc = ".".join(str(p) for p in e.path) or "<root>"
                lines.append(f"  - {loc}: {e.message}")
            fail("\n".join(lines))
        seam_ids.add(seam.get("seam_id"))

    if len(seam_ids) < 3:
        fail(f"examples must cover at least three distinct seams, found {sorted(seam_ids)}")

    base = {
        "seam_id": "SEAM-999",
        "name": "Example seam",
        "boundary_from": "A",
        "boundary_to": "B",
        "attack_vector": "example vector",
        "gate_requirements": ["example gate"],
        "implementation_status": "open",
        "priority": "high",
    }

    def must_reject(label: str, doc: dict[str, Any]) -> None:
        if validator.is_valid(doc):
            fail(f"{label}: document was ACCEPTED but must be rejected: {json.dumps(doc)}")

    r1 = copy.deepcopy(base); r1["implementation_status"] = "mostly_gated"
    must_reject("R1 bad implementation_status", r1)

    r2 = copy.deepcopy(base); r2["gate_requirements"] = []
    must_reject("R2 empty gate_requirements", r2)

    r3 = copy.deepcopy(base); del r3["seam_id"]
    must_reject("R3 missing seam_id", r3)

    r4 = copy.deepcopy(base); r4["seam_id"] = "seam-13"
    must_reject("R4 malformed seam_id", r4)

    r5 = copy.deepcopy(base); r5["priority"] = "trivial"
    must_reject("R5 bad priority", r5)

    print(
        f"OK: SeamDefinition schema valid; {len(example_paths)} seams validated "
        f"({', '.join(sorted(s for s in seam_ids if s))}); "
        f"5 rejection invariants enforced (R1-R5)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
