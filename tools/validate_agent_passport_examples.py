#!/usr/bin/env python3
"""Validate AgentPassport: five-class typed host-agent classification (T0-1).

AgentPassport is the anchor vocabulary object: downstream tranches (ontogenesis
OWL/SHACL, mcp-a2a-zero-trust tiers, synapseiq enrichment, workstation-contracts
fixtures, source-os eBPF) all import urn:srcos:agent-passport:* as a stable
reference. So the invariants that make a classification meaningful are asserted
here BY REJECTION — a validator never observed refusing is indistinguishable
from no validator.

Positive: every element of examples/agent-passport.json validates, and the
collection covers at least one third_party and one system_core instance.

Negative (each fed to the SCHEMA as a real document; each MUST be rejected):
  R1  third_party with system_bundle: true            (class elevation)
  R2  suppress_user_authorization_prompt: true while   (unsigned suppression)
      is_apple_signed: false
  R3  intelligence_automation missing an intelligence  (unconstrained intel agent)
      constraint field
  R4  unknown agent_class (not one of the five)        (unclassified / anySource)
  R5  missing bundle_id                                (no stable identity)
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "AgentPassport.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "agent-passport.json"

EXPECTED_CLASSES = {
    "system_core",
    "intelligence_automation",
    "app_helper",
    "legacy_bridge",
    "third_party",
}


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

    # agent_class enum must contain exactly the five canonical values.
    enum = set(schema["properties"]["agent_class"]["enum"])
    if enum != EXPECTED_CLASSES:
        fail(f"agent_class enum must be exactly the five classes, got {sorted(enum)}")

    examples = load(EXAMPLE_PATH)
    if not isinstance(examples, list) or not examples:
        fail("examples/agent-passport.json must be a non-empty array of passports")

    # Positive: every element validates.
    seen_classes = set()
    for i, passport in enumerate(examples):
        errors = sorted(validator.iter_errors(passport), key=lambda e: list(e.path))
        if errors:
            lines = [f"example[{i}] ({passport.get('bundle_id', '?')}) failed validation:"]
            for e in errors:
                loc = ".".join(str(p) for p in e.path) or "<root>"
                lines.append(f"  - {loc}: {e.message}")
            fail("\n".join(lines))
        seen_classes.add(passport.get("agent_class"))

    # Coverage: at least one third_party and one system_core instance.
    for required_class in ("third_party", "system_core"):
        if required_class not in seen_classes:
            fail(f"examples must cover at least one {required_class} instance")

    # Negative: each bad document MUST be rejected. A valid base to mutate:
    base = {
        "bundle_id": "com.example.app",
        "agent_class": "app_helper",
        "is_daemon": False,
        "is_apple_signed": True,
        "suppress_user_authorization_prompt": False,
        "system_bundle": False,
        "interrupt_level": "standard",
    }

    def must_reject(label: str, doc: dict[str, Any]) -> None:
        if validator.is_valid(doc):
            fail(f"{label}: document was ACCEPTED but must be rejected: {json.dumps(doc)}")

    # R1: third_party cannot claim system_bundle: true.
    r1 = copy.deepcopy(base)
    r1["agent_class"] = "third_party"
    r1["system_bundle"] = True
    must_reject("R1 third_party+system_bundle", r1)

    # R2: suppression requires apple-signed.
    r2 = copy.deepcopy(base)
    r2["suppress_user_authorization_prompt"] = True
    r2["is_apple_signed"] = False
    must_reject("R2 unsigned suppression", r2)

    # R3: intelligence_automation must carry all three constraint fields.
    r3 = copy.deepcopy(base)
    r3["agent_class"] = "intelligence_automation"
    r3["summarize_previews_permitted"] = False
    r3["dnd_intelligent_management_permitted"] = False
    # autonomous_action_permitted intentionally omitted
    must_reject("R3 intel missing constraint", r3)

    # R4: unknown class (anySource is not a valid class).
    r4 = copy.deepcopy(base)
    r4["agent_class"] = "anySource"
    must_reject("R4 unknown class", r4)

    # R5: no stable identity.
    r5 = copy.deepcopy(base)
    del r5["bundle_id"]
    must_reject("R5 missing bundle_id", r5)

    print(
        f"OK: AgentPassport schema valid; {len(examples)} example passports validated "
        f"(classes: {', '.join(sorted(c for c in seen_classes if c))}); "
        f"5 rejection invariants enforced (R1-R5)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
