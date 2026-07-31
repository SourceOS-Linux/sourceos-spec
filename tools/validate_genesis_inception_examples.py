#!/usr/bin/env python3
"""Validate the Cybernetic Agentic Genesis & Inception schema pack (Phase 0).

Four canonical schemas derived from the inception plan's sample objects:
GenesisSeed (formation artifact), Hologram (base semantic representation),
TwinEventEnvelope (K3 lifecycle event), AdapterDescriptor (world-changing
adapter). The plan's exit criteria — "schemas validate, example objects compile"
— are enforced here, and the load-bearing minimums are asserted by REJECTION.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples"

# schema file -> example file (both carry a `type` discriminator for the CI mapper)
PACK = {
    "GenesisSeed.json": "genesis-seed.json",
    "Hologram.json": "hologram.json",
    "TwinEventEnvelope.json": "twin-event-envelope.json",
    "AdapterDescriptor.json": "adapter-descriptor.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> int:
    validators: dict[str, Draft202012Validator] = {}
    for schema_file, example_file in PACK.items():
        schema = load(SCHEMAS / schema_file)
        Draft202012Validator.check_schema(schema)
        v = Draft202012Validator(schema)
        validators[schema_file] = v
        example = load(EXAMPLES / example_file)
        errors = sorted(v.iter_errors(example), key=lambda e: list(e.path))
        if errors:
            loc = ".".join(str(p) for p in errors[0].path) or "<root>"
            fail(f"{example_file} invalid against {schema_file}: {loc}: {errors[0].message}")

    def must_reject(schema_file: str, label: str, mutate) -> None:
        base = load(EXAMPLES / PACK[schema_file])
        doc = mutate(copy.deepcopy(base))
        if validators[schema_file].is_valid(doc):
            fail(f"{label}: document was ACCEPTED but must be rejected")

    # GenesisSeed: a seed with no ontology slice / no id is not a formation artifact.
    must_reject("GenesisSeed.json", "GenesisSeed empty ontology_slice", lambda d: {**d, "ontology_slice": []})
    must_reject("GenesisSeed.json", "GenesisSeed missing seed_id", lambda d: {k: v for k, v in d.items() if k != "seed_id"})
    # Hologram: no archetypes / no policy envelope = ungoverned object.
    must_reject("Hologram.json", "Hologram empty archetypes", lambda d: {**d, "archetypes": []})
    must_reject("Hologram.json", "Hologram missing policy_envelope", lambda d: {k: v for k, v in d.items() if k != "policy_envelope"})
    # TwinEventEnvelope: no provenance = unreplayable.
    must_reject("TwinEventEnvelope.json", "TwinEventEnvelope empty provenance_refs", lambda d: {**d, "provenance_refs": []})
    must_reject("TwinEventEnvelope.json", "TwinEventEnvelope missing twin_id", lambda d: {k: v for k, v in d.items() if k != "twin_id"})
    # AdapterDescriptor: no capabilities / no policy hooks = an ungated actuator.
    must_reject("AdapterDescriptor.json", "AdapterDescriptor empty capabilities", lambda d: {**d, "capabilities": []})
    must_reject("AdapterDescriptor.json", "AdapterDescriptor empty policy_hooks", lambda d: {**d, "policy_hooks": []})
    must_reject("AdapterDescriptor.json", "AdapterDescriptor bad kind", lambda d: {**d, "kind": "quantum"})

    print(
        f"OK: genesis-inception pack — {len(PACK)} schemas + examples validated "
        f"(GenesisSeed, Hologram, TwinEventEnvelope, AdapterDescriptor); "
        f"9 rejection invariants enforced"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
