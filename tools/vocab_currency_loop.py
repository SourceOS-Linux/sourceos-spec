#!/usr/bin/env python3
"""LIVE vocab-currency GovernedLoop (task #13) — instantiates the merged GovernedLoop contract.

The doctrine (vocabulary is the governance substrate): the approved glossary is the FIXED set
(LSA side); the corpus is the OPEN set (LDA side); their divergence is the currency signal —
"new fields become new vocab not yet connected." A static glossary can't stay current, so
currency is a LOOP, not a DAG. But per [[feedback_loops_vs_dags_governed]] a loop is admissible
only when GOVERNED, so this runner does NOT invent its own iteration budget: it reads bound +
convergence-tolerance + onNonConvergence + admission FROM a validated `GovernedLoop` document and
obeys them. The contract governs the runtime.

Divergence measure (monotone, information-theoretic, dependency-free):
    D = uncovered probability mass = Σ Q(t) for corpus tokens t the approved vocab does NOT name,
where Q is the corpus token distribution (what the current state actually discusses). Remediation
= connect the single highest-Q uncovered token (propose it as a new GlossaryTerm), which lowers D
by exactly Q(t) — strictly monotone-decreasing, so `monotone-decrease` convergence is real.

Fail-closed teeth:
  * a loop with no `admission.superconsciousRef` is REFUSED (loops don't self-authorize);
  * the loop runs AT MOST `bound.maxIterations` — it never spins;
  * if D has not reached `tolerance` within the bound, it applies `onNonConvergence`
    (escalate-human | refuse) and exits non-zero with an escalation record — it does not
    silently declare success;
  * a remediation step that failed to decrease D (measure not monotone) escalates.

Run:
    python3 tools/vocab_currency_loop.py                 # default fixtures → converges
    python3 tools/vocab_currency_loop.py --corpus <f>    # point at another corpus
    python3 tools/vocab_currency_loop.py --trace         # include per-iteration divergence trace
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
LOOP_SCHEMA = ROOT / "schemas" / "GovernedLoop.json"
FIX = ROOT / "fixtures" / "vocab-currency"

# Minimal English stopword set — function words carry no domain vocab, so they are neither
# "covered" nor "divergent"; excluding them keeps the currency signal about domain terms.
STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "are", "be", "by",
    "that", "this", "it", "as", "at", "with", "from", "must", "can", "will", "any", "no",
    "not", "so", "if", "then", "than", "into", "over", "each", "we", "our", "its", "their",
    "until", "required", "left", "held", "recorded", "carried", "could", "never", "was",
}


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z][a-z0-9-]+", text.lower()) if t not in STOP and len(t) > 2]


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def vocab_tokens(glossary: dict) -> set[str]:
    """The FIXED set: every content token named by an APPROVED glossary term (label+definition+id
    slug). A draft/unaligned term does not yet regulate state, so it does not count as coverage."""
    toks: set[str] = set()
    for term in glossary["terms"]:
        if term.get("status") != "approved":
            continue
        slug = term["id"].split(":")[-1].replace("-", " ")
        toks.update(tokenize(" ".join(filter(None, [term.get("label"), term.get("definition"), slug]))))
    return toks


def corpus_distribution(corpus: dict) -> dict[str, float]:
    """The OPEN set: the normalized token distribution Q over the corpus (what is discussed now)."""
    counts: dict[str, int] = {}
    for doc in corpus["documents"]:
        for t in tokenize(doc["text"]):
            counts[t] = counts.get(t, 0) + 1
    total = sum(counts.values()) or 1
    return {t: c / total for t, c in counts.items()}


def uncovered_mass(Q: dict[str, float], covered: set[str]) -> float:
    return sum(q for t, q in Q.items() if t not in covered)


def run_loop(loop: dict, glossary: dict, corpus: dict) -> dict:
    # Admission first — a loop that does not name its superconscious governor may not run.
    if not (loop.get("admission") or {}).get("superconsciousRef"):
        return {"ok": False, "refused": "unadmitted",
                "detail": "GovernedLoop has no admission.superconsciousRef — loops don't self-authorize"}

    max_iter = loop["bound"]["maxIterations"]
    tolerance = loop["convergence"].get("tolerance", 0.0)
    on_nonconv = loop["onNonConvergence"]

    covered = vocab_tokens(glossary)
    Q = corpus_distribution(corpus)
    D = uncovered_mass(Q, covered)
    trace = [{"iteration": 0, "divergence": round(D, 6), "connected": None}]
    connected: list[dict] = []

    for i in range(1, max_iter + 1):
        if D <= tolerance:
            break
        # Remediation: connect the single highest-Q uncovered token (propose it as new vocab).
        candidates = sorted(((q, t) for t, q in Q.items() if t not in covered), reverse=True)
        if not candidates:
            break
        q, tok = candidates[0]
        prev = D
        covered.add(tok)
        D = uncovered_mass(Q, covered)
        if D >= prev:  # measure must strictly decrease — otherwise it is not a convergent loop
            return {"ok": False, "escalated": "non-monotone",
                    "handler": on_nonconv, "detail": f"divergence did not decrease at step {i}",
                    "trace": trace}
        connected.append({"term": tok, "massConnected": round(q, 6)})
        trace.append({"iteration": i, "divergence": round(D, 6), "connected": tok})

    converged = D <= tolerance
    remaining = sorted(((round(q, 6), t) for t, q in Q.items() if t not in covered), reverse=True)
    result = {
        "loopRef": loop["id"],
        "admittedBy": loop["admission"]["superconsciousRef"],
        "iterations": len(trace) - 1,
        "maxIterations": max_iter,
        "tolerance": tolerance,
        "finalDivergence": round(D, 6),
        "converged": converged,
        "connectedVocab": connected,
        "candidateNewVocab": [{"term": t, "mass": q} for q, t in remaining[:10]],
        "trace": trace,
    }
    if not converged:
        # Fail-closed: within the bound the loop could not make the vocab current → do NOT spin,
        # do NOT declare success. Escalate per the contract's onNonConvergence handler.
        result["ok"] = False
        result["escalated"] = on_nonconv
        result["detail"] = (f"vocab currency not reached in {max_iter} iterations "
                            f"(divergence {D:.4f} > tolerance {tolerance}); "
                            f"{len(remaining)} corpus terms remain unnamed by the glossary")
        return result
    result["ok"] = True
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", default=str(ROOT / "examples" / "governed_loop.vocab_currency.json"))
    ap.add_argument("--glossary", default=str(FIX / "glossary.json"))
    ap.add_argument("--corpus", default=str(FIX / "corpus.json"))
    ap.add_argument("--trace", action="store_true", help="include the per-iteration divergence trace")
    args = ap.parse_args()

    loop = load(Path(args.loop))
    # The runtime is governed by the contract — so the contract must itself be valid.
    errs = sorted(jsonschema.Draft202012Validator(load(LOOP_SCHEMA)).iter_errors(loop), key=str)
    if errs:
        print(json.dumps({"ok": False, "invalidContract": [e.message for e in errs]}, indent=2))
        return 1

    result = run_loop(loop, load(Path(args.glossary)), load(Path(args.corpus)))
    if not args.trace:
        result.pop("trace", None)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
