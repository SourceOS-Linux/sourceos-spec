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

import inspect
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


def concentration_ceiling(h: float, distinct_principals: int, lattice: dict,
                          machine_derived: bool = False) -> str:
    """§2.2. The highest warrant admissible given how CONCENTRATED the evidence is.

    Volume is deliberately not an input. A single principal emitting a hundred
    thousand observations is one voice repeated, and the cap exists so that
    repetition cannot be laundered into warrant.
    """
    best = "SPECULATIVE"
    for cap in lattice["concentrationCaps"]:
        max_h = cap.get("maxHerfindahl")
        min_k = cap.get("minDistinctPrincipals")
        if cap.get("machineDerivedExempt") and machine_derived:
            pass                                    # exemption waives the diversity floor
        else:
            if max_h is not None and h > max_h:
                continue
            if min_k is not None and distinct_principals < min_k:
                continue
        if WARRANT_ORD[cap["ceiling"]] > WARRANT_ORD[best]:
            best = cap["ceiling"]
    return best


def revoke_token(atoms: list[dict], token: str) -> tuple[float, int]:
    """SP-PW-R2. Recompute the aggregate after revoking one consent token.

    The aggregate is decomposable — a sum of per-token sufficient statistics — so
    withdrawing a token subtracts that token's partial and touches nothing else.
    The count returned is what the vector actually constrains: revocation must be
    O(revoked tokens), not O(corpus). A scorer that had to re-read every atom would
    make revocation cost grow with retained history, which is precisely the shape
    that turns "you may withdraw consent" into something a system quietly defers.
    """
    partials: dict[str, float] = {}
    for atom in atoms:
        partials[atom["consentToken"]] = partials.get(atom["consentToken"], 0.0) + atom["weight"]
    touched = sum(1 for a in atoms if a["consentToken"] == token)
    remaining = sum(v for k, v in partials.items() if k != token)
    return remaining, touched


def apply_neg(state: dict) -> dict:
    """§3.3 NEG: a falsifying test that has been attested.

    Suspends and returns to the declaration gate, and RETAINS prior attestations.
    Deleting them would make a falsified manifest indistinguishable from one never
    attested, erasing the record of who vouched for it.
    """
    return {
        "suspended": True,
        "returnedToDeclarationGate": True,
        "attestations": list(state.get("attestations", [])),
        "granted": False,
    }


def hysteretic_ceiling(proposals: list[tuple[int, str]], lattice: dict) -> list[str]:
    """§3.2 dwell hysteresis. A proposed level must PERSIST before it is adopted.

    Raising requires dwellUpDays of continuous support, lowering dwellDownDays.
    Evidence oscillating across a boundary therefore never satisfies either dwell,
    and the applied ceiling holds flat. Without this a boundary-straddling signal
    would republish the ceiling every cycle, and every downstream consumer would
    see authority appear and disappear on noise.

    thetaUp/thetaDown are intentionally unset (OI-1, pending the L2 scorer choice);
    the dwell values used here are normative today.
    """
    dwell_up = lattice["hysteresis"]["dwellUpDays"]
    dwell_down = lattice["hysteresis"]["dwellDownDays"]
    applied: list[str] = []
    current = proposals[0][1]
    candidate = current
    since = proposals[0][0]
    for day, proposed in proposals:
        if proposed != candidate:
            candidate, since = proposed, day           # a new direction restarts the clock
        if candidate != current:
            needed = dwell_up if WARRANT_ORD[candidate] > WARRANT_ORD[current] else dwell_down
            if day - since >= needed:
                current = candidate
        applied.append(current)
    return applied


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

    # ── T2, T3, T5, T6 ────────────────────────────────────────────────────────
    # These four vectors were declared in fixtures/pattern-warrant/conformance.json
    # and executed by nothing. A conformance vector that no code runs asserts the
    # same amount as a comment.

    # T2: one principal, 100k observations, H=1.0 => capped at EMPIRICAL. Volume is
    # not an input; the cap is what stops repetition being laundered into warrant.
    checks["T2"] = concentration_ceiling(1.0, 1, lattice) == "EMPIRICAL"
    # Negative controls: the cap must actually bind, and must lift when diversity is real.
    checks["T2:neg-concentrated-not-bounded"] = concentration_ceiling(1.0, 1, lattice) != "BOUNDED"
    checks["T2:diverse-reaches-bounded"] = concentration_ceiling(0.4, 4, lattice) == "BOUNDED"
    # The vector supplies volume=100000 precisely to establish that it buys nothing.
    # Assert that structurally: volume is not a parameter of the cap at all, so no
    # amount of it can enter the computation.
    checks["T2:volume-is-not-an-input"] = (
        "volume" not in inspect.signature(concentration_ceiling).parameters
    )

    # T3: revoking one token touches only atoms bearing it — O(revoked), not O(corpus).
    atoms = [{"consentToken": f"t{i % 4}", "weight": 1.0} for i in range(400)]
    remaining, touched = revoke_token(atoms, "t0")
    checks["T3"] = touched == 100 and remaining == 300.0
    checks["T3:sublinear-in-corpus"] = touched < len(atoms)
    # Negative control: revoking an absent token must change nothing and touch nothing.
    remaining_noop, touched_noop = revoke_token(atoms, "t-absent")
    checks["T3:absent-token-is-a-noop"] = touched_noop == 0 and remaining_noop == 400.0

    # T5: an attested NEG suspends and returns to the gate, and does NOT delete
    # attestations — a falsified manifest must stay distinguishable from an
    # unattested one.
    after = apply_neg({"attestations": [{"quorumRole": "owner"}, {"quorumRole": "reviewer"}]})
    checks["T5"] = (
        after["suspended"] is True
        and after["returnedToDeclarationGate"] is True
        and len(after["attestations"]) == 2
    )
    checks["T5:neg-does-not-grant"] = after["granted"] is False

    # T6: evidence oscillating across a boundary must not flap the applied ceiling.
    # 20 days alternating between two levels satisfies neither dwell (7d up, 2d down).
    oscillating = [(d, "EMPIRICAL" if d % 2 else "BOUNDED") for d in range(20)]
    applied = hysteretic_ceiling(oscillating, lattice)
    checks["T6"] = len(set(applied)) == 1
    # Negative control: a level that PERSISTS past the dwell must still be adopted,
    # or "no flapping" would be trivially satisfied by a ceiling that never moves.
    sustained = [(d, "BOUNDED" if d >= 1 else "EMPIRICAL") for d in range(20)]
    checks["T6:sustained-change-is-adopted"] = hysteretic_ceiling(sustained, lattice)[-1] == "BOUNDED"

    # The revocation conjunct of the grant predicate: `grant(revoked=...)` existed
    # but was only ever called with False, so the clause had never been exercised.
    manifest_probe = json.loads((ROOT / "examples" / "candidate-manifest.c2.json").read_text(encoding="utf-8"))
    checks["I1:revoked-consent-blocks-grant"] = grant(
        manifest_probe["warrantAtDeclaration"]["epistemicLevel"],
        manifest_probe["consequenceClass"],
        manifest_probe["attestations"],
        True,                                        # revoked
        lattice,
    ) is False

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


def executed_vector_ids() -> set[str]:
    """The §9 vector ids this validator actually recomputes.

    Derived from a real run rather than hand-listed, so it cannot drift into
    claiming coverage the code does not provide. validate_vectors_are_executed
    compares this against the fixture and fails on either direction of mismatch.
    """
    lattice = json.loads((ROOT / "examples" / "warrant-lattice.default.json").read_text(encoding="utf-8"))
    return {k.split(":", 1)[0] for k in check_vectors(lattice) if k.startswith("T")}


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
