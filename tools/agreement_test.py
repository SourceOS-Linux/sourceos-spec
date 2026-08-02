#!/usr/bin/env python3
"""Agreement test — the glossary's DECLARED relations vs the estate's OBSERVED dependencies (task #13).

The neurosymbolic check: the vocabulary is the SYMBOLIC view (typed `relations` between terms, e.g.
`has-a` composition); the blast-radius graph is the OBSERVED view (actual dependency edges between
estate entities, as a governed blast-radius/GBRG analysis emits them). Two independent views of the
same structure must AGREE — if they don't, one is wrong:

  * OVERCLAIM — a term declares `A has-a B`, both bound to estate entities, but the blast-radius
    graph shows no corresponding edge. The vocabulary asserts a dependency the estate doesn't
    exhibit: a governance hole. FAIL-CLOSED.
  * DRIFT — the blast-radius graph shows an edge between two bound entities that no declared
    relation names. The estate has a dependency the vocabulary hasn't captured: staleness. Reported
    as a remediation candidate (a proposed `has-a` relation), not a hard failure — same treatment as
    the vocab-currency loop's candidate terms.

This tool CONSUMES a blast-radius graph (it does not define one — GBRG is that graph's authority);
it only projects the glossary's relations onto the estate via `alignment.estateBinding` and compares.

Dependency-implying predicates are the composition/aggregation ones (`has-a`, `has-member`) — the
whole depends on / blast-radiates to its parts. Subsumption (`is-a`) and lexical (`skos:*`) links
are NOT runtime dependencies and are excluded.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DEP_PREDICATES = {"has-a", "has-member"}


def load(p: Path) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _binding(term: dict) -> str | None:
    return ((term.get("alignment") or {}).get("estateBinding") or {}).get("ref")


def agreement(glossary: dict, graph: dict) -> dict:
    terms = {t["id"]: t for t in glossary["terms"]}
    # Only APPROVED terms regulate state, so only their relations are held to agreement — a draft
    # term hasn't been promoted through the alignment gate and can't overclaim the estate.
    bind = {tid: _binding(t) for tid, t in terms.items()
            if _binding(t) and t.get("status") == "approved"}
    observed = {(e["from"], e["to"]) for e in graph.get("edges", [])}

    # DECLARED estate edges: a dep-implying relation A->B where both A and B are bound entities.
    declared: dict[tuple[str, str], tuple[str, str]] = {}
    for tid, t in terms.items():
        if tid not in bind:
            continue
        for rel in t.get("relations", []):
            if rel.get("predicate") in DEP_PREDICATES and rel.get("target") in bind:
                declared[(bind[tid], bind[rel["target"]])] = (tid, rel["target"])

    agreements = [{"declaredBy": v, "edge": list(k)} for k, v in declared.items() if k in observed]
    overclaims = [{"declaredBy": v, "edge": list(k),
                   "detail": "vocabulary declares a dependency the blast-radius graph does not show"}
                  for k, v in declared.items() if k not in observed]

    # DRIFT: an observed edge between two bound entities with no declared dep relation -> propose one.
    ent_to_term = {ref: tid for tid, ref in bind.items()}
    drift = []
    for (ef, et) in sorted(observed):
        if ef in ent_to_term and et in ent_to_term and (ef, et) not in declared:
            drift.append({"edge": [ef, et],
                          "proposedRelation": {"subject": ent_to_term[ef], "predicate": "has-a",
                                               "target": ent_to_term[et]},
                          "detail": "estate shows a dependency the vocabulary does not name"})

    return {
        "ok": not overclaims,  # fail-closed on overclaims; drift is remediation, not failure
        "agreements": agreements,
        "overclaims": overclaims,
        "driftCandidates": drift,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glossary", default=str(Path(__file__).resolve().parents[1] / "fixtures" / "agreement" / "glossary.json"))
    ap.add_argument("--graph", default=str(Path(__file__).resolve().parents[1] / "fixtures" / "agreement" / "blast_radius_graph.json"))
    args = ap.parse_args()
    result = agreement(load(Path(args.glossary)), load(Path(args.graph)))
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
