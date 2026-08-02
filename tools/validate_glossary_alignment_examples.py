#!/usr/bin/env python3
"""Validate GlossaryTerm alignment — the vocabulary drift-guard (task #13).

Language is the governance substrate. An APPROVED term must be usable to reason about
governance, which means all three methods must hold, fail-closed:
  1. capture     — bound to a formal ontology class (alignment.ontologyClassRef);
  2. vector-align — an NP↔VP link in the sovereign 768 space (alignment.vectorLink),
                    and the peer must link back (a link is a relation, not a claim);
  3. implement   — bound to a real estate entity/service (alignment.estateBinding),
                    with NP→entity and VP→action|service (Tesnière).
A 'draft' term may be partially aligned (capture in flight); an approved term may not.
Plus: negative vectors fail on their named JSON-Schema keyword.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "GlossaryTerm.json"
EXAMPLES = [
    "glossary_term.np_entity.json",
    "glossary_term.vp_action.json",
    "glossary_term.draft_unaligned.json",
]

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def check_conformance(schema: dict, terms: dict[str, dict]) -> None:
    jsonschema.Draft202012Validator.check_schema(schema)
    for name, t in terms.items():
        errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(t), key=str)
        if errs:
            for e in errs:
                FAILURES.append(f"{name}: {e.message}")
        else:
            CHECKS[f"schema:{name}"] = True


def check_alignment(terms: dict[str, dict]) -> None:
    by_id = {t["id"]: t for t in terms.values()}
    for name, t in terms.items():
        a = t.get("alignment") or {}
        status = t.get("status", "draft")
        pos = t.get("partOfSpeech")

        if status == "approved":
            missing = [k for k in ("ontologyClassRef", "vectorLink", "estateBinding") if not a.get(k)]
            if missing:
                FAILURES.append(f"{name}: approved term is a governance hole — unaligned method(s) {missing} "
                                f"(an approved term must be captured + vector-aligned + implemented)")
                continue
            CHECKS[f"aligned:{name}"] = True
            # NP→entity, VP→action|service
            kind = a["estateBinding"]["kind"]
            if pos == "noun-phrase" and kind != "entity":
                FAILURES.append(f"{name}: an NP term must bind to an entity, not {kind!r}")
            elif pos == "verb-phrase" and kind not in ("action", "service"):
                FAILURES.append(f"{name}: a VP term must bind to an action/service, not {kind!r}")
            else:
                CHECKS[f"pos-binding:{name}"] = True
            # vector link must be reciprocal (a relation, not a one-sided claim)
            peer = by_id.get(a["vectorLink"]["peerRef"])
            if peer is not None:
                back = ((peer.get("alignment") or {}).get("vectorLink") or {}).get("peerRef")
                if back != t["id"]:
                    FAILURES.append(f"{name}: vectorLink to {a['vectorLink']['peerRef']} is not reciprocated "
                                    f"(peer links back to {back!r}) — a link is a relation, not a claim")
                else:
                    CHECKS[f"vector-reciprocal:{name}"] = True
        else:
            CHECKS[f"draft-ok:{name}"] = True  # a draft may be partial


INVERSE = {"is-type": "has-type", "has-type": "is-type",
           "is-member": "has-member", "has-member": "is-member",
           "skos:broader": "skos:narrower", "skos:narrower": "skos:broader"}
SYMMETRIC = {"skos:related"}


def check_relations(terms: dict[str, dict]) -> None:
    """Reasoner-consistency over the typed relations: inverse pairs reciprocate,
    skos:related is symmetric, and is-a (subsumption) is acyclic. This is what lets a
    reasoner derive dependencies + constraints (and cross-check them against the
    blast-radius graph + neurosymbolic domain — the follow-up standard test)."""
    by_id = {t["id"]: t for t in terms.values()}

    def rels(t):
        return [(r["predicate"], r["target"]) for r in (t.get("relations") or [])]

    for name, t in terms.items():
        for pred, tgt in rels(t):
            peer = by_id.get(tgt)
            if peer is None:
                continue  # external ontology-class / estate target — resolved elsewhere
            peer_rels = rels(peer)
            if pred in INVERSE and (INVERSE[pred], t["id"]) not in peer_rels:
                FAILURES.append(f"{name}: {pred} → {tgt} not reciprocated by inverse {INVERSE[pred]} — "
                                f"an unreciprocated relation is a claim, not a fact the reasoner can use")
            elif pred in SYMMETRIC and (pred, t["id"]) not in peer_rels:
                FAILURES.append(f"{name}: {pred} → {tgt} is not symmetric (peer does not relate back)")
            else:
                CHECKS[f"relation:{name}:{pred}"] = True

    # is-a (subsumption) must be acyclic — a cycle is an unsatisfiable constraint.
    isa = {t["id"]: [tg for pr, tg in rels(t) if pr == "is-a"] for t in terms.values()}
    WHITE, GREY, BLACK = 0, 1, 2
    color = {k: WHITE for k in isa}

    def dfs(n: str) -> bool:
        color[n] = GREY
        for m in isa.get(n, []):
            if m not in color:
                continue
            if color[m] == GREY or (color[m] == WHITE and dfs(m)):
                return True
        color[n] = BLACK
        return False

    if any(color[n] == WHITE and dfs(n) for n in isa):
        FAILURES.append("is-a subsumption graph has a cycle — an unsatisfiable constraint")
    else:
        CHECKS["is-a:acyclic"] = True


def check_negatives(schema: dict) -> None:
    fx = load(ROOT / "fixtures" / "glossary-alignment" / "conformance.json")
    for i, case in enumerate(fx["cases"]):
        expected = case.get("failValidator")
        try:
            jsonschema.validate(case["document"], schema)
        except jsonschema.ValidationError as exc:
            if expected is not None and exc.validator != expected:
                FAILURES.append(f"negative {i}: failed on {exc.validator!r}, not {expected!r}: {case['reason']}")
            else:
                CHECKS[f"negative:{i}:{exc.validator}"] = True
            continue
        FAILURES.append(f"negative {i} unexpectedly PASSED: {case['reason']}")


def main() -> int:
    schema = load(ROOT / "schemas" / SCHEMA)
    terms = {n: load(ROOT / "examples" / n) for n in EXAMPLES}
    check_conformance(schema, terms)
    check_alignment(terms)
    check_relations(terms)
    check_negatives(schema)
    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
