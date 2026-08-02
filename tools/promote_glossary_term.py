#!/usr/bin/env python3
"""Governed draft->approved promotion of a GlossaryTerm via the 3-method alignment (task #13).

The vocab-currency loop ingests terms as `draft`; a draft term names something but does not yet
regulate state. It becomes `approved` — able to regulate — only through the 3-method alignment
from the GlossaryTerm contract (#250), and only if all three hold as a FAIL-CLOSED MEET (the same
shape as DAR promotion = governance ∧ IP/legal):

    capture      — alignment.ontologyClassRef  (bound to a formal ontology class)
    vector-align — alignment.vectorLink         (an NP↔VP link in the sovereign 768 space,
                   RECIPROCATED by the named peer — a one-way link is not an alignment)
    implement    — alignment.estateBinding      (bound to a real estate entity/service/action)

promote() returns the approved term ONLY if the meet holds; otherwise it REFUSES and names the
unaligned method(s), leaving the term draft. It never approves on a partial alignment — an approved
term that isn't captured+aligned+implemented is a governance hole (exactly what #250's drift-guard
rejects; this is the active promotion whose output that guard then accepts).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EMBED_MODEL = "nomic-ai/nomic-embed-text-v1.5"
EMBED_DIM = 768
ESTATE_KINDS = {"entity", "service", "action"}


def load(p: Path) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _method_failures(term: dict, alignment: dict, peer: dict | None) -> list[str]:
    """Recompute the meet — never trust a declared 'aligned' flag. Returns the missing methods."""
    fails = []
    # 1. capture
    if not str(alignment.get("ontologyClassRef") or "").strip():
        fails.append("capture (alignment.ontologyClassRef missing)")
    # 2. vector-align — present, const-pinned to the sovereign space, and RECIPROCATED by the peer
    vl = alignment.get("vectorLink") or {}
    if not vl.get("peerRef"):
        fails.append("vector-align (alignment.vectorLink missing)")
    elif vl.get("model") != EMBED_MODEL or vl.get("dimension") != EMBED_DIM:
        fails.append(f"vector-align (vectorLink must pin {EMBED_MODEL} / dim {EMBED_DIM})")
    else:
        back = ((peer or {}).get("alignment") or {}).get("vectorLink") or {}
        if not peer or peer.get("id") != vl["peerRef"]:
            fails.append(f"vector-align (peer {vl['peerRef']} not supplied for reciprocity check)")
        elif back.get("peerRef") != term.get("id"):
            fails.append(f"vector-align (peer {vl['peerRef']} does not link back — one-way link is not an alignment)")
    # 3. implement
    eb = alignment.get("estateBinding") or {}
    if eb.get("kind") not in ESTATE_KINDS or not str(eb.get("ref") or "").strip():
        fails.append("implement (alignment.estateBinding missing a valid kind+ref)")
    return fails


def promote(term: dict, alignment: dict, peer: dict | None = None) -> dict:
    fails = _method_failures(term, alignment, peer)
    if fails:
        return {"promoted": False, "term": term.get("id"), "status": "draft",
                "refused": "incomplete-alignment", "unaligned": fails,
                "detail": "draft->approved refused: an approved term must be captured + vector-aligned "
                          "+ implemented (fail-closed meet); it stays draft"}
    approved = {**term, "status": "approved", "alignment": alignment}
    return {"promoted": True, "term": term["id"], "status": "approved", "approvedTerm": approved}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--term", required=True, help="draft GlossaryTerm JSON")
    ap.add_argument("--alignment", required=True, help="proposed alignment JSON")
    ap.add_argument("--peer", help="the vectorLink peer term JSON (for reciprocity)")
    args = ap.parse_args()
    result = promote(load(Path(args.term)), load(Path(args.alignment)),
                     load(Path(args.peer)) if args.peer else None)
    print(json.dumps(result, indent=2))
    return 0 if result.get("promoted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
