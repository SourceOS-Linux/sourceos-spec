#!/usr/bin/env python3
"""k-gram TF-IDF / LSA differential — confirm stopword candidates by compositional scale (task #13).

The stopword deviation analysis flags a dropped word as a term-candidate when it is concentrated in
a domain AND recurs in repeated (bigram) collocations. That is the bigram FLOOR. This tool is the
confirmation: it measures the word's domain-specificity across n-gram ORDERS 3..7 and takes the
DIFFERENTIAL.

For each order n, over the domain corpora:
  * build the n-gram x domain count matrix (n-grams over RAW tokens, so a stopword that is part of a
    real phrase — "held to maturity", "empty set of states" — is captured);
  * weight it TF-IDF (documents = domains): a phrase frequent in ONE domain and rare across the rest
    scores high — it is domain-specific;
  * take the LSA (truncated SVD) of that TF-IDF matrix: the top singular component is the dominant
    axis of cross-domain variation, and a domain-specific n-gram loads heavily on it.

A candidate word's signal at order n = the strongest domain-specific TF-IDF among the n-grams that
contain it (and its share of the LSA top-component energy). The DIFFERENTIAL across 3..7 is the
discriminator:
  * a TRUE domain term PERSISTS — it keeps appearing in domain-specific n-grams as n grows (it is
    the head of longer collocations), so its signal stays high across orders -> CONFIRMED-TERM;
  * a stylistic / noise word DECAYS — its longer n-grams become unique and diffuse (no repeated
    domain phrase), so its concentrated TF-IDF and LSA energy fall away -> UNCONFIRMED.

Confirmed candidates are the strongest un-stoplist proposals; unconfirmed ones stay stoplisted.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ORDERS = [3, 4, 5, 6, 7]
SIGNAL_TERMLIKE = 0.40       # per-order domain-specific-signal threshold
PERSIST_FRACTION = 0.5       # must clear the threshold on >= this share of the orders => persists


def raw_tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z][a-z0-9-]+", text.lower()) if len(t) >= 2]


def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def order_signal(domain_tokens: dict[str, list[str]], n: int, candidates: list[str]) -> dict:
    domains = list(domain_tokens)
    D = len(domains)
    # n-gram counts per domain
    counts = {d: {} for d in domains}
    vocab: set[tuple[str, ...]] = set()
    for d, toks in domain_tokens.items():
        for g in ngrams(toks, n):
            counts[d][g] = counts[d].get(g, 0) + 1
            vocab.add(g)
    if not vocab:
        return {w: {"tfidf": 0.0, "lsaEnergy": 0.0} for w in candidates}
    vocab = sorted(vocab)
    df = {g: sum(1 for d in domains if g in counts[d]) for g in vocab}

    # TF-IDF matrix rows=n-grams, cols=domains (smoothed idf).
    M = np.zeros((len(vocab), D))
    idx = {g: i for i, g in enumerate(vocab)}
    for j, d in enumerate(domains):
        for g, c in counts[d].items():
            M[idx[g], j] = (1 + math.log(c)) * math.log((1 + D) / (1 + df[g]))
    col_max = M.max() or 1.0

    # LSA — top singular component = dominant axis of cross-domain variation.
    try:
        U, S, _ = np.linalg.svd(M, full_matrices=False)
        loading = (U[:, 0] * S[0]) ** 2 if S.size else np.zeros(len(vocab))
    except np.linalg.LinAlgError:
        loading = np.zeros(len(vocab))
    total_energy = loading.sum() or 1.0

    out = {}
    for w in candidates:
        rows = [idx[g] for g in vocab if w in g]
        tfidf = float(M[rows].max() / col_max) if rows else 0.0            # strongest domain-specific phrase w heads
        energy = float(loading[rows].sum() / total_energy) if rows else 0.0  # share of latent variation from w's n-grams
        out[w] = {"tfidf": round(tfidf, 3), "lsaEnergy": round(energy, 3)}
    return out


def _unigram_specificity(domain_tokens: dict[str, list[str]], w: str) -> float:
    # Intrinsic domain-specificity of w AS A UNIGRAM (the stopword-analysis concentration), mapped
    # to [0,1]: uniform (1/D) -> 0, fully concentrated -> 1. A stopword embedded in a domain phrase
    # ("the state machine") borrows the phrase's n-gram specificity; discounting by unigram
    # specificity strips that borrowed signal, so only intrinsically domain-specific words persist.
    D = len(domain_tokens)
    relfreq = [domain_tokens[d].count(w) / (len(domain_tokens[d]) or 1) for d in domain_tokens]
    s = sum(relfreq) or 1.0
    concentration = max(relfreq) / s
    return max(0.0, min(1.0, (concentration - 1 / D) / (1 - 1 / D))) if D > 1 else 1.0


def differential(domains: dict[str, str], candidates: list[str]) -> dict:
    domain_tokens = {d: raw_tokenize(t) for d, t in domains.items()}
    by_order = {n: order_signal(domain_tokens, n, candidates) for n in ORDERS}
    uspec = {w: _unigram_specificity(domain_tokens, w) for w in candidates}

    rows = []
    for w in candidates:
        # discount each order's domain-specific n-gram signal by the word's intrinsic unigram
        # specificity — borrowed phrase-specificity (e.g. "the") is stripped away.
        signal = {n: round(by_order[n][w]["tfidf"] * uspec[w], 3) for n in ORDERS}
        lsa = {n: by_order[n][w]["lsaEnergy"] for n in ORDERS}
        deltas = {f"{ORDERS[i]}->{ORDERS[i + 1]}": round(signal[ORDERS[i + 1]] - signal[ORDERS[i]], 3)
                  for i in range(len(ORDERS) - 1)}
        cleared = sum(1 for n in ORDERS if signal[n] >= SIGNAL_TERMLIKE)
        persists = cleared >= math.ceil(len(ORDERS) * PERSIST_FRACTION)
        rows.append({
            "word": w,
            "unigramSpecificity": round(uspec[w], 3),
            "tfidfByOrder": signal,
            "lsaEnergyByOrder": lsa,
            "differential": deltas,
            "ordersCleared": cleared,
            "verdict": "confirmed-term" if persists else "unconfirmed",
        })
    return {"orders": ORDERS, "domains": list(domains),
            "confirmed": [r["word"] for r in rows if r["verdict"] == "confirmed-term"],
            "rows": rows}


def _load_fixture() -> tuple[dict, list[str]]:
    FIX = ROOT / "fixtures" / "kgram-differential"
    domains = {d["domain"]: "\n".join(x["text"] for x in d["documents"])
               for d in (json.loads(p.read_text()) for p in sorted((FIX / "domains").glob("*.json")))}
    candidates = json.loads((FIX / "candidates.json").read_text())["candidates"]
    return domains, candidates


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--domains-dir", help="dir of {domain, documents:[{text}]} JSON (default: fixture)")
    ap.add_argument("--candidates", nargs="*", help="candidate words (default: fixture)")
    args = ap.parse_args()
    if args.domains_dir:
        domains = {d["domain"]: "\n".join(x["text"] for x in d["documents"])
                   for d in (json.loads(p.read_text()) for p in sorted(Path(args.domains_dir).glob("*.json")))}
        candidates = args.candidates or []
    else:
        domains, candidates = _load_fixture()
    print(json.dumps(differential(domains, candidates), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
