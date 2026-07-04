#!/usr/bin/env python3
"""Validate digital-soul identity and reputation examples.

Beyond JSON Schema, this validator enforces the invariants that make the
two-layer design safe:

  * unique ids and the expected URN prefix per contract;
  * timestamp parseability;
  * the PRIVACY BOUNDARY: no reputation document (ReputationDimension,
    SacredCapitalLedger, PortableReputationClaim) may contain any given-identity
    input key (birthdate / faith / personality*). Identity inputs live only in
    DigitalSoulIdentity.givenInputs and must never appear on the reputation side;
  * DIRECTIONALITY: AscensionReading must be on-device, network-prohibited, and
    declare works->inner-axes allowed / identity-inputs->reputation forbidden;
  * EVIDENCE BACKING: capital entries and claimed dimensions reference at least
    one works-receipt urn.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    ("schemas/IdentitySpine.json", "examples/identity_spine.json"),
    ("schemas/DigitalSoulIdentity.json", "examples/digital_soul_identity.json"),
    ("schemas/AscensionReading.json", "examples/ascension_reading.json"),
    ("schemas/ReputationDimension.json", "examples/reputation_dimension.json"),
    ("schemas/SacredCapitalLedger.json", "examples/sacred_capital_ledger.json"),
    ("schemas/PortableReputationClaim.json", "examples/portable_reputation_claim.json"),
]

EXPECTED_IDS = {
    "IdentitySpine": "urn:srcos:identity-spine:",
    "DigitalSoulIdentity": "urn:srcos:digital-soul:",
    "AscensionReading": "urn:srcos:ascension-reading:",
    "ReputationDimension": "urn:srcos:reputation-dimension:",
    "SacredCapitalLedger": "urn:srcos:sacred-capital:",
    "PortableReputationClaim": "urn:srcos:reputation-claim:",
}

REPUTATION_TYPES = {"ReputationDimension", "SacredCapitalLedger", "PortableReputationClaim"}
FORBIDDEN_ON_REPUTATION = ("birthdate", "faith", "personality", "personalityprofile", "giveninputs")
TIMESTAMP_KEYS = {"createdAt", "capturedAt", "asOf"}


def walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_keys(v)


def check_timestamps(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in TIMESTAMP_KEYS and isinstance(v, str):
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            check_timestamps(v)
    elif isinstance(obj, list):
        for v in obj:
            check_timestamps(v)


def main() -> int:
    errors: list[str] = []
    seen_ids: set[str] = set()

    for schema_rel, ex_rel in PAIRS:
        schema = json.loads((ROOT / schema_rel).read_text())
        doc = json.loads((ROOT / ex_rel).read_text())

        try:
            jsonschema.validate(doc, schema, cls=jsonschema.Draft202012Validator)
        except jsonschema.ValidationError as e:
            errors.append(f"{ex_rel}: schema invalid: {e.message} @ {list(e.absolute_path)}")
            continue

        t = doc.get("type")
        prefix = EXPECTED_IDS.get(t)
        if prefix and not str(doc.get("id", "")).startswith(prefix):
            errors.append(f"{ex_rel}: id '{doc.get('id')}' must start with '{prefix}'")
        if doc.get("id") in seen_ids:
            errors.append(f"{ex_rel}: duplicate id '{doc.get('id')}'")
        seen_ids.add(doc.get("id"))

        try:
            check_timestamps(doc)
        except ValueError as e:
            errors.append(f"{ex_rel}: unparseable timestamp: {e}")

        # PRIVACY BOUNDARY
        if t in REPUTATION_TYPES:
            for key in walk_keys(doc):
                if key.lower() in FORBIDDEN_ON_REPUTATION:
                    errors.append(f"{ex_rel}: privacy-boundary violation: reputation doc carries identity key '{key}'")

        # DIRECTIONALITY
        if t == "AscensionReading":
            if doc.get("networkServiceProhibited") is not True:
                errors.append(f"{ex_rel}: AscensionReading must set networkServiceProhibited=true")
            if doc.get("computedOn") not in {"holder-device", "holder-agent"}:
                errors.append(f"{ex_rel}: AscensionReading must be computed in a holder context")
            d = doc.get("directionality", {})
            if d.get("identityInputsToReputation") != "forbidden":
                errors.append(f"{ex_rel}: directionality.identityInputsToReputation must be 'forbidden'")
            if d.get("worksToInnerAxes") != "allowed":
                errors.append(f"{ex_rel}: directionality.worksToInnerAxes must be 'allowed'")

        # EVIDENCE BACKING
        if t == "SacredCapitalLedger":
            for i, entry in enumerate(doc.get("entries", [])):
                if not entry.get("evidenceRefs"):
                    errors.append(f"{ex_rel}: entry[{i}] must reference at least one works-receipt")
        if t == "PortableReputationClaim":
            for i, cd in enumerate(doc.get("claimedDimensions", [])):
                if not cd.get("evidenceRefs"):
                    errors.append(f"{ex_rel}: claimedDimensions[{i}] must reference at least one works-receipt")
            if doc.get("noGlobalScore") is False:
                errors.append(f"{ex_rel}: must not assert a global score")

        if not any(e.startswith(ex_rel) for e in errors):
            print(f"OK   {ex_rel}")

    # IdentitySpine: exactly 64 gates with unique ids
    spine = json.loads((ROOT / "examples/identity_spine.json").read_text())
    gate_ids = [g["gateId"] for g in spine.get("gates", [])]
    if len(gate_ids) != 64 or len(set(gate_ids)) != 64:
        errors.append("identity_spine.json: spine must define exactly 64 unique gates")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nAll digital-soul examples valid (schema + invariants).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
