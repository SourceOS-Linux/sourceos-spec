#!/usr/bin/env python3
"""CI teeth for the glossary<->blast-radius agreement test (task #13).

Asserts the two views are held to AGREE fail-closed: an aligned vocabulary agrees; a vocabulary
that overclaims a dependency the estate doesn't exhibit is REFUSED (governance hole); and an estate
dependency the vocabulary hasn't named is surfaced as a remediation candidate (drift), not silently
passed and not hard-failed.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agreement_test as A  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures" / "agreement"

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}

EPI_EDGE = {"from": "urn:srcos:service:release-gate", "to": "urn:srcos:service:epistemic-evaluator"}
EPI_REL = {"predicate": "has-a", "target": "urn:srcos:glossary:epistemic-level"}


def main() -> int:
    glossary = A.load(FIX / "glossary.json")
    graph = A.load(FIX / "blast_radius_graph.json")

    # 1. Aligned vocabulary agrees with the observed graph.
    r = A.agreement(glossary, graph)
    if not r["ok"] or len(r["agreements"]) < 1 or r["overclaims"]:
        FAILURES.append(f"aligned case should agree, got overclaims={r['overclaims']}")
    else:
        CHECKS["aligned:agrees"] = True

    # 2. OVERCLAIM — declare release-gate has-a epistemic-level, but the graph has no such edge.
    g2 = copy.deepcopy(glossary)
    next(t for t in g2["terms"] if t["id"].endswith("release-gate"))["relations"].append(EPI_REL)
    r = A.agreement(g2, graph)  # graph lacks release-gate->epistemic-evaluator
    if r["ok"] or not any(o["edge"][1].endswith("epistemic-evaluator") for o in r["overclaims"]):
        FAILURES.append("an overclaimed dependency (no observed edge) must fail")
    else:
        CHECKS["overclaim:refused"] = True

    # 3. DRIFT — the graph shows release-gate->epistemic-evaluator, but no relation names it.
    g3 = copy.deepcopy(graph)
    g3["edges"].append(EPI_EDGE)
    r = A.agreement(glossary, g3)  # glossary has no has-a epistemic-level
    drifted = [d for d in r["driftCandidates"] if d["edge"][1].endswith("epistemic-evaluator")]
    if not r["ok"]:
        FAILURES.append("drift (observed-but-undeclared) must be reported, not hard-failed")
    elif not drifted or drifted[0]["proposedRelation"]["predicate"] != "has-a":
        FAILURES.append("drift must surface a proposed has-a relation as a remediation candidate")
    else:
        CHECKS["drift:reported-as-candidate"] = True

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
