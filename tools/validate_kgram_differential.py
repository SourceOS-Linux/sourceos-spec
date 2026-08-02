#!/usr/bin/env python3
"""CI teeth for the k-gram TF-IDF/LSA differential (task #13).

Asserts the differential confirms a stopword candidate only when its domain-specific signal PERSISTS
across n-gram orders 3..7 AND is intrinsic (unigram-backed) — so a real term is confirmed, a merely
concentrated-but-diffuse word ('and') is not, and a word that only BORROWS phrase specificity ('the')
is stripped by the unigram discount.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kgram_tfidf_differential as K  # noqa: E402

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def main() -> int:
    domains, candidates = K._load_fixture()
    r = K.differential(domains, candidates)
    confirmed = set(r["confirmed"])
    row = {x["word"]: x for x in r["rows"]}

    # 0. Orders are exactly 3..7.
    if r["orders"] != [3, 4, 5, 6, 7]:
        FAILURES.append(f"orders must be [3,4,5,6,7], got {r['orders']}")
    else:
        CHECKS["orders:3-7"] = True

    # 1. Real domain terms are confirmed (signal persists across orders).
    for w in ("set", "class", "state"):
        if w not in confirmed:
            FAILURES.append(f"'{w}' is a domain term whose signal persists 3..7 but was not confirmed")
    if not any("not confirmed" in m for m in FAILURES):
        CHECKS["terms:confirmed-across-orders"] = True

    # 2. Confirmed terms actually PERSIST — cleared on a majority of orders, not one spike.
    if all(row[w]["ordersCleared"] >= 3 for w in ("set", "class", "state")):
        CHECKS["terms:persist-not-spike"] = True
    else:
        FAILURES.append("a confirmed term did not persist across a majority of orders")

    # 3. THE TRAP: 'and' is concentrated (narrative-only) but its n-grams are diffuse -> unconfirmed.
    if "and" in confirmed or row["and"]["ordersCleared"] != 0:
        FAILURES.append("'and' (concentrated but not compositional) must not be confirmed")
    else:
        CHECKS["diffuse-word:unconfirmed"] = True

    # 4. 'the' borrows phrase specificity; the unigram discount must strip it -> unconfirmed + low uspec.
    if "the" in confirmed or row["the"]["unigramSpecificity"] >= 0.5:
        FAILURES.append("'the' must be stripped by the unigram-specificity discount (borrowed signal)")
    else:
        CHECKS["borrowed-specificity:stripped"] = True

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS, "confirmed": sorted(confirmed)}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
