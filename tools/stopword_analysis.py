#!/usr/bin/env python3
"""Stopword deviation analysis — the words we DROP are ungoverned vocabulary too (task #13).

The vocab-currency loop drops a fixed stoplist so domain terms surface. But that list is itself an
ungoverned governance decision: a word that is noise in one domain ("set", "class", "state",
"value", "required") can be a real TERM in another (math, OOP, state machines, config). Dropping it
universally erases signal where it matters. So we evaluate the dropped words the same way we
evaluate the kept ones — their frequency, connections, and compositional density — ACROSS domains,
and use TWO signals — cross-domain deviation AND compositional density — because frequency alone
lies (a stylistic word like "and" can be concentrated in a chatty domain without being a term):

  * TERM-CANDIDATE — the word's mass is CONCENTRATED in a subset of domains (deviates) AND it recurs
    in fixed collocations there ("empty set", "state machine"): a domain term hiding in the stoplist,
    a candidate to UN-stoplist in that domain (a remediation signal, like the currency loop's
    candidate terms and the agreement test's drift). Confirmed by the k-gram tf-idf/lsa differential.
  * STYLISTIC — concentrated but its neighbours are arbitrary/unique (no repeated collocations): the
    deviation is style, not signal (e.g. "and"). Keep stoplisted; flagged for the k-gram check.
  * NOISE — uniformly frequent across domains: a true stopword everywhere.

Only a governance signal, never a silent drop: the stoplist becomes an auditable, per-domain
artifact instead of a hard-coded assumption. Compositional density here is the bigram floor of the
k-gram TF-IDF/LSA differential (orders 3..7) — the deeper follow-on that confirms these candidates.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_OCCURRENCES = 3          # below this we can't judge a word — verdict "insufficient-data"
CONCENTRATION_INTERESTING = 0.66   # >= this share of freq-mass in one domain => concentrated (deviates)
DENSITY_TERMLIKE = 0.30            # >= this repeated-collocation density => behaves like a term, not filler


def raw_tokenize(text: str) -> list[str]:
    # RAW: unlike the loop, we do NOT drop stopwords — the stopwords are exactly what we analyze.
    return [t for t in re.findall(r"[a-z][a-z0-9-]+", text.lower()) if len(t) >= 2]


def analyze(domains: dict[str, str], stoplist: set[str]) -> dict:
    tokens = {d: raw_tokenize(text) for d, text in domains.items()}
    totals = {d: len(t) or 1 for d, t in tokens.items()}

    interesting, noise, insufficient = [], [], []
    for w in sorted(stoplist):
        occ = {d: t.count(w) for d, t in tokens.items()}
        total_occ = sum(occ.values())
        if total_occ < MIN_OCCURRENCES:
            insufficient.append(w)
            continue
        relfreq = {d: occ[d] / totals[d] for d in domains}
        rf_sum = sum(relfreq.values()) or 1.0
        concentration = max(relfreq.values()) / rf_sum          # 1/D (uniform) .. 1.0 (concentrated)
        cand = max(relfreq, key=relfreq.get)

        # Compositional DENSITY in the concentrated domain: of all (w, content-neighbour) adjacencies,
        # what fraction belong to a collocation that REPEATS (>=2)? A domain term recurs in fixed
        # collocations ("empty set", "state machine"); a stylistic function word ("and") glues
        # arbitrary, mostly-unique content. This is the discriminator that frequency alone can't give
        # — and the light, bigram version of the k-gram TF-IDF differential (the deeper follow-on).
        toks = tokens[cand]
        pairs: dict[str, int] = {}
        for i, tok in enumerate(toks):
            if tok != w:
                continue
            for j in (i - 1, i + 1):
                if 0 <= j < len(toks) and toks[j] not in stoplist:
                    pairs[toks[j]] = pairs.get(toks[j], 0) + 1
        total_adj = sum(pairs.values())
        repeated_adj = sum(c for c in pairs.values() if c >= 2)
        density = round(repeated_adj / total_adj, 3) if total_adj else 0.0

        row = {"word": w, "concentration": round(concentration, 3), "candidateDomain": cand,
               "compositionalDensity": density, "occurrences": total_occ,
               "perDomainFreq": {d: round(relfreq[d], 5) for d in domains},
               "topPartners": sorted(pairs, key=pairs.get, reverse=True)[:5]}

        if concentration < CONCENTRATION_INTERESTING:
            row["verdict"] = "noise"            # uniform across domains — a true stopword everywhere
            noise.append(row)
        elif density >= DENSITY_TERMLIKE:
            row["verdict"] = "term-candidate"   # concentrated AND recurs in fixed collocations
            row["proposal"] = f"un-stoplist '{w}' in domain '{cand}' (candidate domain term)"
            row["confirmWith"] = "k-gram tf-idf/lsa differential"
            interesting.append(row)
        else:
            row["verdict"] = "stylistic"        # concentrated by STYLE, not collocation (e.g. 'and')
            row["note"] = "deviation is stylistic, not compositional — keep stoplisted pending k-gram check"
            noise.append(row)

    return {"domains": list(domains), "stoplistSize": len(stoplist),
            "termCandidates": interesting,
            "noiseCount": len(noise), "insufficientDataCount": len(insufficient),
            "noiseWords": [r["word"] for r in noise]}


def _live_domains() -> dict[str, str]:
    # Each spec file is a mini-domain — cross-file deviation is a proxy for cross-domain deviation.
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted((ROOT / "specs").glob("*.md"))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="analyze the shipped stoplist over specs/*.md")
    args = ap.parse_args()
    if args.live:
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        import vocab_currency_loop as vcl  # noqa: E402
        result = analyze(_live_domains(), vcl.STOP)
    else:
        FIX = ROOT / "fixtures" / "stopword-analysis"
        domains = {d["domain"]: "\n".join(x["text"] for x in d["documents"])
                   for d in (json.loads(p.read_text()) for p in sorted((FIX / "domains").glob("*.json")))}
        stoplist = set(json.loads((FIX / "stoplist.json").read_text())["stoplist"])
        result = analyze(domains, stoplist)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
