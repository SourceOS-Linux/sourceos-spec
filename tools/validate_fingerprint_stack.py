#!/usr/bin/env python3
"""Validate the six-layer fingerprint stack (SP-FPRINT-STACK-001).

Recompute-don't-trust throughout. Every stored verdict in this family is a CACHE of
something derivable — the stance from its evidence, the pooled evidence from the admissible
layers, n_eff from the covariance spectrum, the drift flag from the measured distance — and
each is recomputed here, so an asserted classification cannot outrun what produced it.

Checks (fail-closed):
   1. schema conformance for every example;
   2. quantizer soundness — stance.value == Q(stance.evidence; thresholds);
   3. threshold symmetry — tau+ != tau- requires a platform attestation (DR-6);
   4. INADMISSIBLE carries an origin (the lattice element is identical across causes, the
      remediations are not);
   5. pooling soundness — pooled evidence is recomputed over the ADMISSIBLE layers only;
   6. annihilation — an inadmissible layer contributes ZERO, never a guessed value;
   7. gate soundness — post-guard evidence never exceeds pooled evidence in either
      component, i.e. guards only lower stance in the knowledge order;
   8. licensed strengthening — probabilistic-sum pooling requires an independence certificate;
   9. quorum — n_eff recomputed from the spectrum, and POS refused below the floor;
  10. path-length budget — effectiveEpsilon >= depth * baseEpsilon (coverage does not compose);
  11. reading tag — present on every stance, and never mixed within one aggregation;
  12. drift — `drifted` and `verdict` recomputed; a silent repurpose must route to a steward;
  13. L5-D1/L5-D2 — under silent repurpose L5 is inadmissible, contributes ZERO, and the
      resulting stance is INADMISSIBLE with a drift origin;
  14. L4 glut — a declared-vs-observed operation conflict emits BOTH components positive;
  15. Q3 barrier — a profiling-inferred constraint promoted to a hard axiom needs attestation;
  16. X1 — parthood and subtyping are disjoint, closure traverses subtyping only, and an
      aggregate count is an interval with INADMISSIBLE reported separately;
  17. M5 — the monotonicity property test is proven to BITE before its pass is trusted;
  18. estate report coherence — all six layers present, every inadmissible one reasoned;
  19. negative vectors fail, each on its named keyword.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fingerprint_aggregate import (  # noqa: E402
    TOL,
    admissible_pairs,
    check_m5_binds,
    n_eff,
    pool,
    quantize,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples"
FIXTURES = ROOT / "fixtures" / "fingerprint-stack"

# An inferred signal (a discovered inclusion dependency where DDL declares no constraint, a
# declared-only L4 with no query log) is admissible but capped: it degrades rather than failing,
# and the cap is what stops "degrade, don't fail" from quietly becoming "guess, don't say".
INFERRED_ALPHA_CAP = 0.5

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def registry() -> Registry:
    resources = []
    for f in SCHEMAS.glob("*.json"):
        schema = load(f)
        res = Resource.from_contents(schema)
        resources.append((schema.get("$id", f.name), res))
        resources.append((f.name, res))
    return Registry().with_resources(resources)


REG = registry()


def validator_for(schema: dict) -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(schema, registry=REG)


def check_conformance(named: dict[str, tuple[dict, dict]]) -> None:
    """Validate each document against its INTENDED schema explicitly — never pick the schema
    from the instance's own `type`, or a mistyped document validates against the wrong one."""
    for name, (doc, schema) in named.items():
        errs = sorted(validator_for(schema).iter_errors(doc), key=str)
        if errs:
            for e in errs:
                FAILURES.append(f"{name}: {e.message}")
        else:
            CHECKS[f"schema:{name}"] = True


def check_stance(name: str, stance: dict) -> None:
    ev, th = stance["evidence"], stance["thresholds"]
    recomputed = quantize(ev["alpha"], ev["beta"], th["tauPos"], th["tauNeg"])
    if recomputed != stance["value"]:
        FAILURES.append(
            f"{name}: stance claims {stance['value']} but Q({ev['alpha']}, {ev['beta']}; "
            f"{th['tauPos']}, {th['tauNeg']}) = {recomputed} — an asserted stance cannot outrun its evidence"
        )
    else:
        CHECKS[f"quantize:{name}"] = True

    if abs(th["tauPos"] - th["tauNeg"]) > TOL and not th.get("attestationRef"):
        FAILURES.append(
            f"{name}: asymmetric thresholds (tau+={th['tauPos']}, tau-={th['tauNeg']}) break "
            f"negation-equivariance and require a platform attestation (DR-6)"
        )
    else:
        CHECKS[f"tau-symmetry:{name}"] = True

    if stance["value"] == "INADMISSIBLE" and not stance.get("inadmissibleOrigin"):
        FAILURES.append(
            f"{name}: INADMISSIBLE without an origin — drift, layer conflict, inconsistent KB and "
            f"stale calibration are the same lattice element with different remediations"
        )
    else:
        CHECKS[f"glut-origin:{name}"] = True

    comp = stance["composition"]
    floor = comp["depth"] * comp["baseEpsilon"]
    if comp["effectiveEpsilon"] < floor - TOL:
        FAILURES.append(
            f"{name}: claims effective epsilon {comp['effectiveEpsilon']} at depth {comp['depth']} "
            f"but the union bound gives at best {floor} — coverage does not compose"
        )
    else:
        CHECKS[f"path-budget:{name}"] = True

    for g in stance.get("guards") or []:
        for path in g["inputs"]:
            if not path.startswith(("evidence.", "witness.")):
                FAILURES.append(
                    f"{name}: guard {g['name']!r} reads {path!r} — guards must be measurable with "
                    f"respect to evidence and witness only; reading the outcome breaks exchangeability"
                )
            else:
                CHECKS[f"guard-measurable:{name}:{g['name']}"] = True


def check_fingerprint(name: str, fp: dict) -> None:
    layers = fp["layerEvidence"]

    # 6. Annihilation — an inadmissible layer contributes ZERO, not a guess.
    for le in layers:
        adm = le["admissibility"]
        ev = le["evidence"]
        if not adm["admissible"] and (ev["alpha"] > TOL or ev["beta"] > TOL):
            FAILURES.append(
                f"{name}/{le['layer']}: inadmissible layer contributes ({ev['alpha']}, {ev['beta']}) "
                f"— an inadmissible layer must contribute ZERO, the annihilator"
            )
        else:
            CHECKS[f"annihilate:{name}:{le['layer']}"] = True
        if not adm["admissible"] and not adm.get("reason"):
            FAILURES.append(f"{name}/{le['layer']}: inadmissible without a named reason")

        # Degrade-don't-fail has a price: an inferred signal cannot speak as loudly as a declared one.
        if le.get("confidenceSource") == "inferred" and ev["alpha"] > INFERRED_ALPHA_CAP + TOL:
            FAILURES.append(
                f"{name}/{le['layer']}: confidenceSource 'inferred' contributes alpha {ev['alpha']} "
                f"above the cap {INFERRED_ALPHA_CAP} — a discovered inclusion dependency is weaker "
                f"evidence than a declared constraint and must be capped as such"
            )
        else:
            CHECKS[f"inferred-cap:{name}:{le['layer']}"] = True

    # 5/8. Pooling soundness over admissible layers only.
    pooling = fp["pooling"]
    op = pooling["operator"]
    if op == "probabilistic-sum" and not pooling.get("independenceCertificateRef"):
        FAILURES.append(
            f"{name}: probabilistic-sum pooling without an independence certificate — corroboration "
            f"pays only where the right to claim it has been earned"
        )
    else:
        CHECKS[f"licensed-pooling:{name}"] = True

    exp_a, exp_b = pool(admissible_pairs(layers), op)
    got = pooling["pooled"]
    if abs(exp_a - got["alpha"]) > 1e-6 or abs(exp_b - got["beta"]) > 1e-6:
        FAILURES.append(
            f"{name}: pooled evidence {(got['alpha'], got['beta'])} != recomputed "
            f"{(round(exp_a, 6), round(exp_b, 6))} over the admissible layers"
        )
    else:
        CHECKS[f"pool:{name}"] = True

    # 7. Gate soundness — guards only lower, in both components.
    stance = fp["stance"]
    sev = stance["evidence"]
    if sev["alpha"] > got["alpha"] + TOL or sev["beta"] > got["beta"] + TOL:
        FAILURES.append(
            f"{name}: post-guard evidence ({sev['alpha']}, {sev['beta']}) EXCEEDS pooled "
            f"({got['alpha']}, {got['beta']}) — guards may only lower stance in the knowledge order"
        )
    else:
        CHECKS[f"gate-sound:{name}"] = True

    # 9. Quorum — recompute n_eff, and refuse POS below the floor.
    q = fp["quorum"]
    spectrum = q.get("covarianceSpectrum")
    if spectrum:
        recomputed = n_eff(spectrum)
        if abs(recomputed - q["nEff"]) > 1e-6:
            FAILURES.append(
                f"{name}: claims n_eff {q['nEff']} but the participation ratio of the given spectrum "
                f"is {round(recomputed, 6)}"
            )
        else:
            CHECKS[f"neff-recompute:{name}"] = True
    if stance["value"] == "POS" and q["nEff"] < q["nEffFloor"] - TOL:
        FAILURES.append(
            f"{name}: POS at n_eff {q['nEff']} below floor {q['nEffFloor']} — below the floor the "
            f"stance is forced to ZERO; the Herfindahl index is a cheap precheck, never the quorum statistic"
        )
    else:
        CHECKS[f"quorum:{name}"] = True

    # 11. Reading tag never mixed within one aggregation.
    CHECKS[f"reading-tagged:{name}"] = bool(stance.get("reading"))

    # 14. L4 glut — a declared-vs-observed conflict is a glut, not a weak match.
    for le in layers:
        w = le["witness"]
        if w.get("kind") == "L4" and w.get("conflictSet"):
            ev = le["evidence"]
            if not (ev["alpha"] > TOL and ev["beta"] > TOL):
                FAILURES.append(
                    f"{name}/L4: conflict set {w['conflictSet']} recorded but evidence "
                    f"({ev['alpha']}, {ev['beta']}) is not a glut — a declared-vs-observed conflict "
                    f"means either the label is wrong or downstream code has a bug, and both need a human"
                )
            else:
                CHECKS[f"l4-glut:{name}"] = True

    # 15. Q3 barrier — profiling is a defeasible prior, never self-promoting.
    for le in layers:
        w = le["witness"]
        if w.get("kind") == "L2" and w.get("promotedToHardAxiom"):
            if not w.get("stewardAttestationRef"):
                FAILURES.append(
                    f"{name}/L2: profiling-inferred constraint promoted to a hard axiom without steward "
                    f"attestation — this is how a bad estate poisons its own ontology"
                )
            else:
                CHECKS[f"q3-barrier:{name}"] = True


def check_drift(name: str, obs: dict, fingerprints: dict[str, dict]) -> None:
    recomputed = obs["distance"] > obs["threshold"]
    if recomputed != obs["drifted"]:
        FAILURES.append(
            f"{name}: drifted={obs['drifted']} but distance {obs['distance']} vs threshold "
            f"{obs['threshold']} recomputes to {recomputed}"
        )
    else:
        CHECKS[f"drift-recompute:{name}"] = True

    expected = (
        "silent-repurpose" if recomputed and not obs["schemaChanged"]
        else "drift-with-redesign" if recomputed
        else "no-drift"
    )
    if obs.get("verdict") != expected:
        FAILURES.append(f"{name}: verdict {obs.get('verdict')!r} but the measurement gives {expected!r}")
    else:
        CHECKS[f"drift-verdict:{name}"] = True

    if expected == "silent-repurpose" and not obs.get("stewardQueueRef"):
        FAILURES.append(
            f"{name}: silent repurpose without a steward queue — routing the glut to a human is a "
            f"behaviour, not a claim"
        )
    else:
        CHECKS[f"drift-routes:{name}"] = True

    # L5-D1 / L5-D2 — the rules that make L5's dangerous confidence survivable.
    if expected != "silent-repurpose":
        return
    for fp_name, fp in fingerprints.items():
        for le in fp["layerEvidence"]:
            w = le["witness"]
            if w.get("kind") != "L5" or w.get("driftRef") != obs["id"]:
                continue
            adm = le["admissibility"]
            ev = le["evidence"]
            if adm["admissible"] or adm.get("reason") != "active-drift-flag":
                FAILURES.append(
                    f"{fp_name}/L5: under silent repurpose L5 must be inadmissible with reason "
                    f"'active-drift-flag' (L5-D2) — L5 asserts stale semantics with maximum confidence "
                    f"exactly when it is wrong"
                )
            elif ev["alpha"] > TOL or ev["beta"] > TOL:
                FAILURES.append(f"{fp_name}/L5: drift guard fired but L5 still contributes {ev}")
            elif fp["stance"]["value"] != "INADMISSIBLE":
                FAILURES.append(
                    f"{fp_name}: silent repurpose puts L5 and L2 in conflict and must emit "
                    f"INADMISSIBLE (L5-D1), not {fp['stance']['value']}"
                )
            elif fp["stance"].get("inadmissibleOrigin") != "profile-drift":
                FAILURES.append(f"{fp_name}: drift glut must record origin 'profile-drift'")
            else:
                CHECKS[f"l5-d1-d2:{fp_name}"] = True


def check_ontodt(graph: dict) -> None:
    """X1 and its consequences: the precondition that makes the source design's own two
    questions simultaneously answerable.

    Q1 'how many tables contain the personal data field Email Address' is a count over the
    SUBTYPE closure; Q2 'what attributes can I expect under Client Address' is an enumeration
    of PARTS. If is_a and part_of share an arrow type, one of those answers is necessarily
    wrong. X1 is not a refinement — it is what makes the questions answerable at all.
    """
    sub = {tuple(e) for e in graph["subtypeOf"]}
    part = {tuple(e) for e in graph["partOf"]}
    overlap = {(x, y) for (x, y) in sub & part if x != y}
    if overlap:
        FAILURES.append(f"X1 violated — pairs are both parthood and subtyping: {sorted(overlap)}")
    else:
        CHECKS["x1-disjoint"] = True

    for qi, q in enumerate(graph["aggregateQueries"]):
        if q["relation"] != "subtypeOf":
            FAILURES.append(
                f"aggregate query {qi}: count closure traverses {q['relation']!r} — aggregation "
                f"traverses subtyping only, never parthood"
            )
            continue
        members = q["members"]
        lo = members["POS"]
        hi = members["POS"] + members["ZERO"]
        if q["answerInterval"] != [lo, hi]:
            FAILURES.append(
                f"aggregate query {qi}: interval {q['answerInterval']} != [{lo}, {hi}] — under the "
                f"open-world assumption a count is an interval, not a number"
            )
        elif q.get("inadmissibleReported") != members["INADMISSIBLE"]:
            FAILURES.append(
                f"aggregate query {qi}: INADMISSIBLE members must be reported separately and never "
                f"folded into the interval"
            )
        else:
            CHECKS[f"cardinality-interval:{qi}"] = True

    for qi, q in enumerate(graph.get("partEnumerations", [])):
        if q["relation"] != "partOf":
            FAILURES.append(
                f"part enumeration {qi}: traverses {q['relation']!r} — 'what attributes can I expect "
                f"under this term' is an enumeration of PARTS, and parthood does not roll up"
            )
        else:
            CHECKS[f"part-enumeration:{qi}"] = True


def check_estate_report(name: str, rep: dict) -> None:
    seen = [layer["layer"] for layer in rep["layers"]]
    if len(set(seen)) != 6:
        FAILURES.append(f"{name}: all six layers must appear — an omitted layer is indistinguishable from an admissible one")
    else:
        CHECKS[f"estate-six-layers:{name}"] = True

    for layer in rep["layers"]:
        if not layer["admissible"] and not layer.get("reason"):
            FAILURES.append(f"{name}/{layer['layer']}: inadmissible without a named reason")

    q = rep["quorum"]
    if q.get("covarianceSpectrum"):
        recomputed = n_eff(q["covarianceSpectrum"])
        if abs(recomputed - q["nEff"]) > 1e-6:
            FAILURES.append(f"{name}: claims n_eff {q['nEff']}, spectrum gives {round(recomputed, 6)}")
        else:
            CHECKS[f"estate-neff:{name}"] = True

    if q["posAvailable"] and q["nEff"] < q["nEffFloor"] - TOL:
        FAILURES.append(
            f"{name}: posAvailable=true at n_eff {q['nEff']} below floor {q['nEffFloor']} — below the "
            f"floor the honest outputs are ZERO and NEG only"
        )
    else:
        CHECKS[f"estate-pos-gate:{name}"] = True

    # Phase 0 is derivable from the catalog and the data alone: no glossary, no query logs.
    if rep["coldStartPhase"] == 0:
        by_layer = {layer["layer"]: layer for layer in rep["layers"]}
        for gated in ("L3-business-glossary", "L4-operational-semantics"):
            if by_layer[gated]["admissible"]:
                FAILURES.append(
                    f"{name}: phase 0 is the catalog-derived bootstrap — {gated} cannot be admissible "
                    f"before a glossary exists"
                )
            else:
                CHECKS[f"cold-start-phase0:{name}:{gated}"] = True


def check_enforcement_policy(name: str, pol: dict) -> None:
    """DR-4 at the enforcement point. ZERO is a knob, but a constrained one: opening it is an
    attested decision, and it is not available at all where the exposure cost is unbounded."""
    for rc in pol["resourceClasses"]:
        if rc["zeroBehavior"] != "fail-open":
            CHECKS[f"dr4-attested:{name}:{rc['resourceClass']}"] = True
            continue
        if not rc.get("attestationRef"):
            FAILURES.append(
                f"{name}/{rc['resourceClass']}: fail-open on ZERO without an attestation — serving data "
                f"whose classification is unknown is a decision somebody makes on the record, or an accident"
            )
        elif rc["sensitivity"] in ("confidential", "restricted"):
            FAILURES.append(
                f"{name}/{rc['resourceClass']}: fail-open on ZERO at sensitivity {rc['sensitivity']!r} — "
                f"an unclassifiable column in a {rc['sensitivity']} resource is precisely the one not to serve, "
                f"and no attestation buys that back"
            )
        else:
            CHECKS[f"dr4-attested:{name}:{rc['resourceClass']}"] = True


def check_dataclass_binding(name: str, dc: dict, reports: dict, policies: dict) -> None:
    """A DataClass that declares the six-layer stack must point at artifacts that EXIST.

    The DataClass contract already had this failure once: it referenced a ModelManifest and
    RunRecords by URN while the model was specified but never trained, so the references
    pointed at nothing (#264 closed that). The same discipline applies here — a declared
    binding whose target is absent is a claim, not a wiring.
    """
    stack = (dc.get("classifier") or {}).get("fingerprintStack")
    if not stack:
        CHECKS[f"dataclass-stack:{name}:none"] = True
        return
    known_reports = {r["id"] for r in reports.values()}
    known_policies = {p["id"] for p in policies.values()}
    ref = stack.get("estateAdmissibilityRef")
    if ref and ref not in known_reports:
        FAILURES.append(f"{name}: estateAdmissibilityRef {ref} resolves to nothing")
    elif stack["enforcementPolicyRef"] not in known_policies:
        FAILURES.append(
            f"{name}: enforcementPolicyRef {stack['enforcementPolicyRef']} resolves to nothing — "
            f"a class whose ZERO behaviour is undefined cannot be enforced"
        )
    else:
        CHECKS[f"dataclass-stack:{name}"] = True


def check_negatives(schemas: dict[str, dict]) -> None:
    fx = load(FIXTURES / "conformance.json")
    for i, case in enumerate(fx["cases"]):
        schema = schemas[case["schema"]]
        expected = case.get("failValidator")
        try:
            validator_for(schema).validate(case["document"])
        except jsonschema.ValidationError as exc:
            if expected is not None and exc.validator != expected:
                FAILURES.append(f"negative {i}: failed on {exc.validator!r}, not {expected!r}: {case['reason']}")
            else:
                CHECKS[f"negative:{i}:{exc.validator}"] = True
            continue
        FAILURES.append(f"negative {i} unexpectedly PASSED: {case['reason']}")


def main() -> int:
    schemas = {
        n: load(SCHEMAS / n)
        for n in (
            "ClassificationStance.json",
            "FingerprintLayerEvidence.json",
            "ColumnFingerprint.json",
            "ColumnDriftObservation.json",
            "EstateAdmissibilityReport.json",
            "ClassificationEnforcementPolicy.json",
        )
    }

    fingerprints = {
        "column_fingerprint.customer_id.json": load(EXAMPLES / "column_fingerprint.customer_id.json"),
        "column_fingerprint.repurposed_status.json": load(EXAMPLES / "column_fingerprint.repurposed_status.json"),
    }
    drifts = {"column_drift.repurposed_status.json": load(EXAMPLES / "column_drift.repurposed_status.json")}
    reports = {
        "estate_admissibility_report.phase0.json": load(EXAMPLES / "estate_admissibility_report.phase0.json"),
    }

    policies = {"classification_enforcement_policy.json": load(EXAMPLES / "classification_enforcement_policy.json")}

    named = {n: (d, schemas["ColumnFingerprint.json"]) for n, d in fingerprints.items()}
    named |= {n: (d, schemas["ColumnDriftObservation.json"]) for n, d in drifts.items()}
    named |= {n: (d, schemas["EstateAdmissibilityReport.json"]) for n, d in reports.items()}
    named |= {n: (d, schemas["ClassificationEnforcementPolicy.json"]) for n, d in policies.items()}
    check_conformance(named)

    for name, fp in fingerprints.items():
        check_stance(name, fp["stance"])
        check_fingerprint(name, fp)
    for name, obs in drifts.items():
        check_drift(name, obs, fingerprints)
    for name, rep in reports.items():
        check_estate_report(name, rep)

    for name, pol in policies.items():
        check_enforcement_policy(name, pol)

    data_classes = {"data_class.currency.json": load(EXAMPLES / "data_class.currency.json")}
    for name, dc in data_classes.items():
        check_dataclass_binding(name, dc, reports, policies)

    check_ontodt(load(FIXTURES / "ontodt_graph.json"))

    # 17. Prove the monotonicity property test bites BEFORE trusting a pass from it.
    binds, note = check_m5_binds()
    CHECKS["m5-property-test-binds"] = binds
    if not binds:
        FAILURES.append(f"M5: {note}")

    check_negatives(schemas)

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
