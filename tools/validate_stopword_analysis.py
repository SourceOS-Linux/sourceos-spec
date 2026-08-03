#!/usr/bin/env python3
"""CI teeth for the stopword deviation analysis (task #13).

Asserts the two-signal discrimination holds: a word concentrated in one domain WITH repeated
collocations is a term-candidate (a domain term hiding in the stoplist); a word concentrated only
by STYLE (no repeated collocations) is NOT promoted (the trap frequency-alone falls into); and a
word uniform across domains is noise. This is what makes the stoplist auditable rather than a silent
universal drop.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stopword_analysis as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures" / "stopword-analysis"

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def main() -> int:
    domains = {d["domain"]: "\n".join(x["text"] for x in d["documents"])
               for d in (json.loads(p.read_text()) for p in sorted((FIX / "domains").glob("*.json")))}
    stoplist = set(json.loads((FIX / "stoplist.json").read_text())["stoplist"])
    r = S.analyze(domains, stoplist)
    cand = {c["word"] for c in r["termCandidates"]}
    noise = set(r["noiseWords"])

    # 1. Domain terms hiding in the stoplist ARE surfaced as term-candidates.
    for w in ("set", "class", "state", "required"):
        if w not in cand:
            FAILURES.append(f"'{w}' is a domain term in 'formal' but was not surfaced as a candidate")
    if not FAILURES:
        CHECKS["domain-terms:surfaced"] = True

    # 2. Each term-candidate is CONCENTRATED and points at the domain that uses it as a term.
    #    Require at least one candidate — all([]) is vacuously True and would mask an empty result.
    if r["termCandidates"] and all(c["concentration"] >= S.CONCENTRATION_INTERESTING and c["candidateDomain"] == "formal"
                                   for c in r["termCandidates"]):
        CHECKS["candidates:concentrated-in-right-domain"] = True
    else:
        FAILURES.append("a term-candidate was not concentrated in the formal domain")

    # 3. THE TRAP: a stylistically-concentrated function word ('and') must NOT be a term-candidate
    #    (frequency deviation alone would wrongly promote it; compositional density saves it).
    if "and" in cand:
        FAILURES.append("'and' was wrongly promoted — stylistic concentration must not read as a term")
    elif "and" not in noise:
        FAILURES.append("'and' should be classified stylistic/noise")
    else:
        CHECKS["stylistic-word:not-promoted"] = True

    # 4. A uniformly-frequent function word ('the') is noise.
    if "the" not in noise or "the" in cand:
        FAILURES.append("'the' (uniform across domains) must be noise")
    else:
        CHECKS["uniform-word:noise"] = True

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS,
                      "termCandidates": sorted(cand), "noise": sorted(noise)}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
