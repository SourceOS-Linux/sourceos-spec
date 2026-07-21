#!/usr/bin/env python3
"""Validate the SP-PATT-WARR-001 pattern-warranted-manifest contract family.

Two checks, not one:
  1. schema conformance — every schema is a valid draft, and every example
     validates against its schema (cross-$ref resolved from a local registry
     so it works offline);
  2. projection soundness — the §9 conformance vectors are recomputed from the
     reference ceiling()/grant() projections over the default WarrantLattice and
     must match their recorded expectations. This keeps the warrant readout an
     *executable* projection of (W_p, C, quorum) rather than a stored opinion,
     and mechanically enforces SP-PW-I1 (no score authorizes) and SP-PW-I2
     (ZERO is never NEG).
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]

WARRANT_ORD = {"SPECULATIVE": 0, "EMPIRICAL": 1, "BOUNDED": 2, "PROVED": 3}
CLASS_ORD = {"C0": 0, "C1": 1, "C2": 2, "C3": 3}
ORD_CLASS = {v: k for k, v in CLASS_ORD.items()}

PAIRS = [
    (ROOT / "schemas" / "WarrantLattice.json", ROOT / "examples" / "warrant-lattice.default.json"),
    (ROOT / "schemas" / "CandidateManifest.json", ROOT / "examples" / "candidate-manifest.c2.json"),
]

SCHEMAS = [
    "EvidenceAtom.json",
    "PatternAtom.json",
    "ConsentAtom.json",
    "AttestationAtom.json",
    "WarrantEdge.json",
    "CandidateManifest.json",
    "WarrantLattice.json",
    "AbstentionEvent.json",
]


def build_registry() -> Registry:
    """Register every schema by its $id so cross-$ref (e.g. CandidateManifest ->
    AttestationAtom) resolves without network access."""
    resources = []
    for name in SCHEMAS:
        schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def ceiling(warrant: str, lattice: dict) -> str:
    """§3.3: C' = max{ c : minW(c) <= W_p }. The operating ceiling under any
    warrant; identical shape whether the warrant is at declaration or decayed."""
    w = WARRANT_ORD[warrant]
    admissible = [
        CLASS_ORD[c]
        for c, floor in lattice["minW"].items()
        if WARRANT_ORD[floor] <= w
    ]
    return ORD_CLASS[max(admissible)] if admissible else "C0"


def quorum_met(consequence_class: str, attestations: list, lattice: dict) -> bool:
    """Attested(m, Q(C)): distinct attestors meeting the required roles and count.
    Independent of W_p — high warrant never reduces the quorum."""
    q = lattice["quorum"][consequence_class]
    roles_present = {a.get("quorumRole") for a in attestations}
    return (
        len(attestations) >= q["minAttestors"]
        and set(q["roles"]).issubset(roles_present)
    )


def grant(warrant: str, consequence_class: str, attestations: list,
          revoked: bool, lattice: dict) -> bool:
    """§1.4 Grant predicate. SP-PW-I1: no value of `warrant` alone flips this true;
    the quorum conjunct is necessary regardless of warrant level."""
    return (
        quorum_met(consequence_class, attestations, lattice)
        and WARRANT_ORD[warrant] >= WARRANT_ORD[lattice["minW"][consequence_class]]
        and not revoked
    )


def check_vectors(lattice: dict) -> dict[str, bool]:
    """Recompute the computable §9 vectors from the reference projections."""
    checks: dict[str, bool] = {}

    # T1: PROVED + C3 + no attestation => grant false (I1).
    checks["T1"] = grant("PROVED", "C3", [], False, lattice) is False

    # T4: warrant decayed to EMPIRICAL on a C2 manifest => ceiling C1, ZERO abstain.
    c = ceiling("EMPIRICAL", lattice)
    ternary = "ZERO" if WARRANT_ORD["EMPIRICAL"] < WARRANT_ORD[lattice["minW"]["C2"]] else "POS"
    checks["T4"] = (c == "C1" and ternary == "ZERO")

    # T7 (structural): the ZERO response must never be representable as NEG. The
    # AbstentionEvent schema pins ternary to const ZERO; assert that here.
    abst = json.loads((ROOT / "schemas" / "AbstentionEvent.json").read_text(encoding="utf-8"))
    checks["T7"] = abst["properties"]["ternary"].get("const") == "ZERO"

    # Full grant path: the C2 example should grant with its two attestations.
    manifest = json.loads((ROOT / "examples" / "candidate-manifest.c2.json").read_text(encoding="utf-8"))
    checks["grant:c2-example"] = grant(
        manifest["warrantAtDeclaration"]["epistemicLevel"],
        manifest["consequenceClass"],
        manifest["attestations"],
        False,
        lattice,
    ) is True

    # I1 negative control: strip attestations from the granting example -> no grant.
    checks["I1:strip-attestations"] = grant(
        manifest["warrantAtDeclaration"]["epistemicLevel"],
        manifest["consequenceClass"],
        [],
        False,
        lattice,
    ) is False

    return checks


def main() -> int:
    registry = build_registry()
    checks: dict[str, bool] = {}

    # (1) schema conformance
    for name in SCHEMAS:
        schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        checks[f"schema:{name}"] = True

    for schema_path, example_path in PAIRS:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        example = json.loads(example_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema, registry=registry).validate(example)
        checks[f"example:{example_path.name}"] = True

    # (2) projection soundness
    lattice = json.loads((ROOT / "examples" / "warrant-lattice.default.json").read_text(encoding="utf-8"))
    vector_checks = check_vectors(lattice)
    for k, v in vector_checks.items():
        if not v:
            raise SystemExit(f"conformance vector failed: {k}")
        checks[f"vector:{k}"] = True

    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
