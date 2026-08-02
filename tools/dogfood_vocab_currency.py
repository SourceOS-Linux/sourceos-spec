#!/usr/bin/env python3
"""Dogfood the vocab-currency GovernedLoop on THIS repo's own vocabulary (task #13).

Runs the governed loop over the estate's real material — every APPROVED GlossaryTerm in
`examples/` is the fixed set (LSA); `specs/*.md` is the corpus (LDA) — to answer, honestly: is
our own approved vocabulary current with our own specifications? On real incomplete vocab the
governed loop does exactly what it should: it connects what it can within the bound, then
ESCALATES-human with concrete proposals rather than pretending currency.

This is a REPORT, not a gate (it always exits 0): the estate vocab is legitimately incomplete
today, so failing CI on it would be wrong. It writes each proposed draft `GlossaryTerm` to
`build/vocab-currency-proposals/<slug>.json` — those are the artifacts ontogenesis ingests for
the 3-method alignment pass. The ENFORCEMENT lives in `validate_vocab_currency_loop.py` (synthetic
fixtures with a known-good outcome); this shows the same loop on live data.
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vocab_currency_loop as vcl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "vocab-currency-proposals"
LOOP = ROOT / "examples" / "governed_loop.vocab_currency.json"

# Real prose carries generic words that aren't estate vocabulary. The core loop stays general;
# for a live scan of Markdown specs we extend the tokenizer's stoplist here so the surfaced
# candidates are DOMAIN terms (contract, runtime, attestation) rather than filler (one, every,
# same). This is corpus configuration, not a change to the loop's semantics.
GENERIC = {
    "one", "two", "three", "every", "only", "same", "may", "what", "each", "also", "both",
    "here", "there", "when", "where", "which", "these", "those", "such", "more", "most",
    "some", "other", "another", "using", "used", "use", "via", "per", "yet", "still", "now",
    "does", "done", "make", "makes", "made", "way", "ways", "like", "just", "even", "them",
    "they", "you", "your", "who", "how", "why", "but", "all", "not", "has", "had", "have",
}


def clean_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)   # fenced code
    text = re.sub(r"`[^`]*`", " ", text)                  # inline code
    text = re.sub(r"https?://\S+", " ", text)             # urls
    text = re.sub(r"[#>*\-_|]", " ", text)                # md punctuation
    return text


def real_glossary() -> dict:
    """Every GlossaryTerm found in examples/ (bundle `terms` arrays + standalone term docs),
    deduped by id. run_loop counts only status==approved as coverage."""
    by_id: dict[str, dict] = {}
    for f in sorted(glob.glob(str(ROOT / "examples" / "*.json"))):
        try:
            doc = json.loads(Path(f).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        items = doc["terms"] if isinstance(doc, dict) and isinstance(doc.get("terms"), list) else [doc]
        for it in items:
            if isinstance(it, dict) and str(it.get("id", "")).startswith("urn:srcos:glossary:"):
                by_id[it["id"]] = it
    return {"terms": list(by_id.values())}


def real_corpus() -> dict:
    docs = []
    for f in sorted(glob.glob(str(ROOT / "specs" / "*.md"))):
        docs.append({"id": Path(f).stem, "text": clean_markdown(Path(f).read_text(encoding="utf-8"))})
    return {"documents": docs}


def main() -> int:
    vcl.STOP |= GENERIC  # configure the tokenizer for prose (domain terms surface, not filler)
    glossary = real_glossary()
    corpus = real_corpus()
    approved = [t["id"] for t in glossary["terms"] if t.get("status") == "approved"]

    loop = vcl.load(LOOP)
    result = vcl.run_loop(loop, glossary, corpus)

    # Persist the proposed draft terms — the real artifacts for ontogenesis ingestion.
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for term in result.get("proposedTerms", []):
        slug = term["id"].split(":")[-1]
        (OUT / f"{slug}.json").write_text(json.dumps(term, indent=2) + "\n", encoding="utf-8")
        written.append(slug)

    print(json.dumps({
        "scan": "vocab-currency dogfood (specs/*.md vs approved glossary)",
        "corpusDocs": len(corpus["documents"]),
        "approvedTerms": approved,
        "governedBy": result.get("admittedBy"),
        "initialDivergence": result.get("trace", [{}])[0].get("divergence"),
        "finalDivergence": result.get("finalDivergence"),
        "iterations": result.get("iterations"),
        "maxIterations": result.get("maxIterations"),
        "outcome": ("current" if result.get("ok") else result.get("escalated") or result.get("refused")),
        "detail": result.get("detail"),
        "proposalsWritten": written,
        "topRemainingCandidates": [c["term"] for c in result.get("candidateNewVocab", [])],
    }, indent=2))
    # Always exit 0 — this is an informational currency scan of live vocab, not a gate.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
