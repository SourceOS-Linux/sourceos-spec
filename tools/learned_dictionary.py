#!/usr/bin/env python3
"""Learned spell-correction + user dictionary — from context, NOT dictionary matching (task #13).

A static wordlist flags every domain term ("epistemiclevel", "srcos", "governedloop") as a
misspelling and "corrects" it away. The estate's own vocabulary can't be a list of known-good
strings — it must be LEARNED from context. So for each UNKNOWN token this decides, from a skip-gram
word-sense predictor rather than membership in a dictionary:

  * LEARN  (add to the user dictionary) — the token RECURS with a COHERENT context (its context
    windows cluster = one stable word-sense), and it is not merely a spelling variant of a known
    word. A real term the dictionary simply hadn't seen yet.
  * CORRECT (to a known word w') — the token is RARE and both close in spelling (small edit
    distance) AND close in learned SENSE (high cosine between its skip-gram vector and w') to a
    known word. Sense — not edit distance alone — picks the target, so a token spelled near a known
    word but used in a DIFFERENT sense is NOT auto-corrected.
  * UNKNOWN — neither coherent enough to learn nor sense-close to a known word (leave for a human).

The predictor is a count-based skip-gram: PPMI over a co-occurrence window, then truncated SVD
(Levy-Goldberg: SGNS factorises shifted PPMI, so PPMI-SVD is the same word-sense family). No wordlist
decides correctness — context does. Fail-closed: every decision is a PROPOSAL (add / correct-to),
never a silent rewrite; a human or the superconscious admits it.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WINDOW = 3
EMBED_DIM = 12
KNOWN_MIN_COUNT = 4        # a word seen this often is treated as "known" (the learned base lexicon)
# A base common-English lexicon (in production this is a frequency list). It is NOT the domain
# dictionary — it just keeps generic English out of consideration so the learner judges DOMAIN
# unknowns. The point of the tool is that DOMAIN terms need no such list; they are learned.
COMMON_ENGLISH = {
    "the", "and", "was", "were", "not", "but", "for", "with", "from", "that", "this", "then",
    "until", "kept", "carried", "recorded", "held", "left", "over", "each", "any", "are", "has",
    "had", "have", "been", "will", "can", "may", "its", "our", "their", "when", "where", "which",
}
LEARN_MIN_DF = 2           # a term must recur across >= this many documents to be learned
COHERENCE_LEARN = 0.35     # context-window coherence needed to call it a stable sense
EDIT_MAX = 2               # max edit distance to consider a token a spelling variant
SENSE_SIM = 0.30           # min skip-gram cosine to a known word to accept a correction target


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z][a-z0-9]+", text.lower()) if len(t) >= 3]


def edit_distance(a: str, b: str) -> int:
    if abs(len(a) - len(b)) > EDIT_MAX:
        return EDIT_MAX + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def skipgram_embeddings(docs: list[list[str]]) -> tuple[dict[str, int], np.ndarray]:
    vocab = sorted({t for d in docs for t in d})
    idx = {w: i for i, w in enumerate(vocab)}
    n = len(vocab)
    C = np.zeros((n, n))
    for d in docs:
        for i, w in enumerate(d):
            for j in range(max(0, i - WINDOW), min(len(d), i + WINDOW + 1)):
                if j != i:
                    C[idx[w], idx[d[j]]] += 1
    total = C.sum() or 1.0
    row = C.sum(axis=1, keepdims=True)
    col = C.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        ppmi = np.maximum(0.0, np.log((C * total) / (row * col + 1e-12) + 1e-12))
    k = min(EMBED_DIM, n)
    U, S, _ = np.linalg.svd(ppmi, full_matrices=False)
    emb = U[:, :k] * np.sqrt(S[:k])
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    emb = emb / np.where(norms == 0, 1.0, norms)   # unit vectors -> dot product = cosine
    return idx, emb


def _context_coherence(docs: list[list[str]], w: str, idx: dict, emb: np.ndarray) -> float:
    # Each occurrence of w has a context vector (mean of its window's word vectors). Coherence =
    # how tightly those context vectors agree (a real term has one stable sense -> tight cluster).
    ctx_vecs = []
    for d in docs:
        for i, tok in enumerate(d):
            if tok != w:
                continue
            neigh = [emb[idx[d[j]]] for j in range(max(0, i - WINDOW), min(len(d), i + WINDOW + 1))
                     if j != i]
            if neigh:
                v = np.mean(neigh, axis=0)
                nv = np.linalg.norm(v)
                if nv:
                    ctx_vecs.append(v / nv)
    if len(ctx_vecs) < 2:
        return 0.0
    centroid = np.mean(ctx_vecs, axis=0)
    centroid /= (np.linalg.norm(centroid) or 1.0)
    return float(np.mean([c @ centroid for c in ctx_vecs]))


def learn(docs: list[list[str]]) -> dict:
    idx, emb = skipgram_embeddings(docs)
    counts = {w: sum(d.count(w) for d in docs) for w in idx}
    df = {w: sum(1 for d in docs if w in d) for w in idx}
    known = {w for w, c in counts.items() if c >= KNOWN_MIN_COUNT} | (COMMON_ENGLISH & set(idx))

    decisions = []
    for w in sorted(idx):
        if w in known:
            continue
        # nearest known word by SENSE among the spelling-near ones (sense, not edit distance, decides)
        near = [(kw, edit_distance(w, kw)) for kw in known if edit_distance(w, kw) <= EDIT_MAX]
        best_kw, best_sim = None, -1.0
        for kw, _ed in near:
            sim = float(emb[idx[w]] @ emb[idx[kw]])
            if sim > best_sim:
                best_kw, best_sim = kw, sim
        coherence = _context_coherence(docs, w, idx, emb)

        if best_kw is not None and best_sim >= SENSE_SIM and df[w] < LEARN_MIN_DF:
            decisions.append({"token": w, "decision": "correct", "correctTo": best_kw,
                              "senseSim": round(best_sim, 3), "editDistance": edit_distance(w, best_kw),
                              "why": "rare + spelling-near + sense matches a known word"})
        elif df[w] >= LEARN_MIN_DF and coherence >= COHERENCE_LEARN:
            decisions.append({"token": w, "decision": "learn", "coherence": round(coherence, 3),
                              "documentFreq": df[w],
                              "why": "recurs with a coherent word-sense — a real term, add to user dictionary"})
        else:
            decisions.append({"token": w, "decision": "unknown", "coherence": round(coherence, 3),
                              "documentFreq": df[w], "why": "neither coherent enough nor sense-close to a known word"})
    return {
        "knownCount": len(known),
        "learn": [d for d in decisions if d["decision"] == "learn"],
        "correct": [d for d in decisions if d["decision"] == "correct"],
        "unknown": [d for d in decisions if d["decision"] == "unknown"],
    }


def _load_fixture() -> list[list[str]]:
    FIX = ROOT / "fixtures" / "learned-dictionary"
    docs = []
    for p in sorted((FIX / "corpus").glob("*.json")):
        for d in json.loads(p.read_text())["documents"]:
            docs.append(tokenize(d["text"]))
    return docs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus-dir")
    args = ap.parse_args()
    if args.corpus_dir:
        docs = [tokenize(d["text"]) for p in sorted(Path(args.corpus_dir).glob("*.json"))
                for d in json.loads(Path(p).read_text())["documents"]]
    else:
        docs = _load_fixture()
    print(json.dumps(learn(docs), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
