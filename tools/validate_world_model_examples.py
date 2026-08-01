#!/usr/bin/env python3
"""Validate the Twin World-Model & GAIA schema pack.

Six canonical schemas give a Twin a dynamical, geospatially-grounded world model
beneath its governance lifecycle: WorldModel (x+ = A*x + B*(G*u)), StateVector
(the latent state reading), ImpulseGate (governed admission), Impulse (a typed
input), Region (geospatial grounding), and GaiaObservation (the exogenous state
read from GAIA — the estate's weather/environmental world model).

The exit criterion — "schemas validate, example objects compile" — is enforced
here, and every load-bearing minimum is asserted by REJECTION. In particular the
two GAIA/fail-closed couplings are proven both ways: an exogenous shock with no
GAIA observation behind it is rejected, and a closed gate that still admits is
rejected.
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
    "WorldModel.json": "world-model.json",
    "StateVector.json": "state-vector.json",
    "ImpulseGate.json": "impulse-gate.json",
    "Impulse.json": "impulse.json",
    "Region.json": "region.json",
    "GaiaObservation.json": "gaia-observation.json",
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

    def drop(key):
        return lambda d: {k: v for k, v in d.items() if k != key}

    # GaiaObservation: an ungrounded / unprovenanced / mis-typed reading is inadmissible.
    must_reject("GaiaObservation.json", "GaiaObservation empty provenance_refs", lambda d: {**d, "provenance_refs": []})
    must_reject("GaiaObservation.json", "GaiaObservation missing gaia_cell", drop("gaia_cell"))
    must_reject("GaiaObservation.json", "GaiaObservation unknown field", lambda d: {**d, "field": "vibes"})

    # Region: a region with no GAIA cells cannot supply exogenous state.
    must_reject("Region.json", "Region empty gaia_cells", lambda d: {**d, "gaia_cells": []})
    must_reject("Region.json", "Region missing centroid", drop("centroid"))

    # ImpulseGate: fail-closed means a closed gate cannot pass signal.
    must_reject("ImpulseGate.json", "ImpulseGate closed but gate_factor>0",
                lambda d: {**d, "mode": "closed", "gate_factor": 0.5})
    must_reject("ImpulseGate.json", "ImpulseGate unknown impulse_class", lambda d: {**d, "impulse_class": "telepathy"})

    # Impulse: exogenous shocks MUST cite GAIA; a closed gate cannot admit.
    must_reject("Impulse.json", "Impulse exogenous_shock without GAIA source_ref", drop("source_ref"))
    must_reject("Impulse.json", "Impulse admitted through closed gate",
                lambda d: {**d, "gate_state": "closed", "admitted": True})

    # StateVector: no dimensions = unobservable; a component outside [0,1] is not a state.
    must_reject("StateVector.json", "StateVector empty dims", lambda d: {**d, "dims": {}})
    must_reject("StateVector.json", "StateVector dim out of range", lambda d: {**d, "dims": {"risk": 1.5}})
    must_reject("StateVector.json", "StateVector missing twin_id", drop("twin_id"))

    # WorldModel: no dims / no gates = not a model; exogenous gate without GAIA source is rejected.
    must_reject("WorldModel.json", "WorldModel empty state_dims", lambda d: {**d, "state_dims": []})
    must_reject("WorldModel.json", "WorldModel empty gates", lambda d: {**d, "gates": []})
    must_reject("WorldModel.json", "WorldModel exogenous gate but exogenous_source=none",
                lambda d: {**d, "exogenous_source": "none"})
    must_reject("WorldModel.json", "WorldModel missing twin_id", drop("twin_id"))

    print(
        "OK: world-model + GAIA pack — 6 schemas + examples validated "
        "(WorldModel, StateVector, ImpulseGate, Impulse, Region, GaiaObservation); "
        "16 rejection invariants enforced (incl. exogenous-shock⇒GAIA and closed-gate⇒no-admit)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
