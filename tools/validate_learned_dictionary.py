#!/usr/bin/env python3
"""CI teeth for the learned spell-correction + user dictionary (task #13).

Asserts the decisions are made from the LEARNED skip-gram word-sense predictor, not a wordlist:
an unknown token that recurs coherently is LEARNED (not corrected away), a rare token whose SENSE
(not just spelling) matches a known word is CORRECTED to it, and a garbage token is left UNKNOWN
(fail-closed — never silently rewritten).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import learned_dictionary as L  # noqa: E402

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def main() -> int:
    r = L.learn(L._load_fixture())
    learn = {d["token"] for d in r["learn"]}
    correct = {d["token"]: d for d in r["correct"]}
    unknown = {d["token"] for d in r["unknown"]}

    # 1. A novel domain term the dictionary never saw is LEARNED (not corrected away).
    if "epistemiclevel" not in learn:
        FAILURES.append("'epistemiclevel' recurs coherently and must be LEARNED, not corrected/dropped")
    else:
        CHECKS["novel-term:learned"] = True

    # 2. A typo is CORRECTED to the known word its SENSE matches (skip-gram cosine drives the target).
    c = correct.get("reciept")
    if not c or c["correctTo"] != "receipt":
        FAILURES.append("'reciept' must be corrected to 'receipt' by learned sense")
    elif "senseSim" not in c:
        FAILURES.append("a correction must be sense-driven (carry senseSim), not edit-distance-only")
    else:
        CHECKS["typo:corrected-by-sense"] = True

    # 3. A garbage token is left UNKNOWN — fail-closed, never silently rewritten.
    if "qwzptl" not in unknown:
        FAILURES.append("garbage 'qwzptl' must be UNKNOWN (not learned, not corrected)")
    else:
        CHECKS["garbage:unknown-fail-closed"] = True

    # 4. The learned term is NOT in the correct set (a real term must not be auto-corrected away).
    if "epistemiclevel" in correct:
        FAILURES.append("a learned term must never be auto-corrected away")
    else:
        CHECKS["learned-term:not-corrected"] = True

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS,
                      "learn": sorted(learn), "correct": {k: v["correctTo"] for k, v in correct.items()},
                      "unknown": sorted(unknown)}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
