#!/usr/bin/env python3
"""CI teeth for the governed draft->approved glossary promotion (task #13).

Asserts the promotion is a real fail-closed meet: a full 3-method alignment promotes, ANY missing
method refuses (term stays draft), and — crucially — the promoted output PASSES #250's own
alignment drift-guard, so promotion can never mint a governance hole (an approved-but-unaligned
term). Reuses `validate_glossary_alignment_examples.check_alignment` rather than reimplementing it.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import promote_glossary_term as P  # noqa: E402
import validate_glossary_alignment_examples as G250  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "examples" / "glossary_promotion.governed_loop.json"

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def main() -> int:
    b = json.loads(BUNDLE.read_text(encoding="utf-8"))
    draft, alignment, peer = b["draftTerm"], b["alignment"], b["peer"]

    # 1. Full 3-method alignment -> promoted to approved.
    r = P.promote(draft, alignment, peer)
    if not r.get("promoted") or r["status"] != "approved":
        FAILURES.append(f"full alignment should promote to approved, got {r.get('refused')} {r.get('unaligned')}")
    else:
        CHECKS["full-alignment:promotes"] = True
        approved = r["approvedTerm"]

        # 1b. The promoted output must PASS #250's drift-guard (no governance hole). Feed the
        #     approved term + its peer so the reciprocity lookup resolves.
        G250.FAILURES.clear()
        G250.check_alignment({"approved": approved, "peer": peer})
        holes = [m for m in G250.FAILURES if approved["id"] in m or "governance hole" in m]
        if holes:
            FAILURES.append(f"promoted term fails #250 alignment drift-guard: {holes}")
        else:
            CHECKS["promoted-output:passes-250-guard"] = True

    # 2. Missing a method (implement) -> refused, stays draft.
    r = P.promote(draft, {k: v for k, v in alignment.items() if k != "estateBinding"}, peer)
    if r.get("promoted") or not any("implement" in m for m in r.get("unaligned", [])):
        FAILURES.append("a term missing estateBinding must be refused (implement)")
    else:
        CHECKS["missing-implement:refused"] = True

    # 3. Non-reciprocal vectorLink (peer doesn't link back) -> refused.
    lonely = copy.deepcopy(peer)
    lonely["alignment"]["vectorLink"]["peerRef"] = "urn:srcos:glossary:someone-else"
    r = P.promote(draft, alignment, lonely)
    if r.get("promoted") or not any("vector-align" in m for m in r.get("unaligned", [])):
        FAILURES.append("a one-way vectorLink (peer does not reciprocate) must be refused")
    else:
        CHECKS["non-reciprocal:refused"] = True

    # 4. Off-space embedding (wrong model) -> refused (sovereign-space pin).
    offspace = copy.deepcopy(alignment)
    offspace["vectorLink"]["model"] = "openai/text-embedding-3-small"
    r = P.promote(draft, offspace, peer)
    if r.get("promoted") or not any("vector-align" in m for m in r.get("unaligned", [])):
        FAILURES.append("a vectorLink off the sovereign embedding space must be refused")
    else:
        CHECKS["off-space-embedding:refused"] = True

    # 5. Input guards — a non-term and an already-approved term are both refused (no silent mutation).
    r = P.promote({"id": "x", "type": "NotATerm"}, alignment, peer)
    if r.get("promoted") or r.get("refused") != "not-a-draft-glossary-term":
        FAILURES.append("a non-GlossaryTerm input must be refused")
    else:
        CHECKS["non-term-input:refused"] = True
    r = P.promote({**draft, "status": "approved"}, alignment, peer)
    if r.get("promoted") or r.get("refused") != "already-approved":
        FAILURES.append("an already-approved term must be refused (nothing to promote)")
    else:
        CHECKS["already-approved:refused"] = True

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
