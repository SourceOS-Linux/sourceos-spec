#!/usr/bin/env python3
"""Validate LawfulDispatchReceipt: Truth = Law × Evidence, enforced by the CONTRACT.

The estate's governance thesis is that a dispatch is true only when both a Law factor and
an Evidence factor are established. Stating that in a docstring is worth nothing — the
Noetica ledger stated it for its whole life while every call site passed the literal 'POS',
and 34 of 53 real entries recorded `grounded: false` next to `verdict: 'POS'` in the same
object. A per-app implementation can always drift back into that. A schema cannot.

So the two governance rules live in the schema, where any validator in any language
enforces them without trusting the emitter:

  INVARIANT 1  verdict == law.factor × evidence.factor, where × is the MEET in the chain
               NEG < ZERO < POS (strong-Kleene conjunction, i.e. min). The 9 branches are
               GENERATED from min(), so the schema cannot disagree with the algebra by
               typo. Critically this is NOT sign multiplication in {-1,0,+1}: that reading
               gives NEG × NEG = POS, certifying a refused gate with a refuted outcome as
               true. This validator asserts that exact receipt is REJECTED.

  INVARIANT 2  evidenceTier T1 is unavailable when either factor is 'declared'. T1 means
               instrumented; claiming it for a value no instrument produced is the same
               defect one level up.

The critical property is asserted by REJECTION. A schema never observed refusing is
indistinguishable from no schema, so every cell of the 3×3 table is checked in both
directions: the 9 correct products accepted, and for each, a wrong verdict rejected.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "LawfulDispatchReceipt.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "lawful-dispatch-receipt.example.json"
VECTORS_PATH = REPO_ROOT / "conformance" / "lawful-verdict-vectors.json"

VERDICTS = ["NEG", "ZERO", "POS"]
RANK = {"NEG": 0, "ZERO": 1, "POS": 2}


def product(law: str, evidence: str) -> str:
    """The meet. Kept as the single definition in this file so the checks below cannot
    silently agree with a wrong schema — the schema's branches were generated from the
    same function, and the vectors are asserted against it too."""
    return VERDICTS[min(RANK[law], RANK[evidence])]


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def seal(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(obj).encode()).hexdigest()


def main() -> int:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("Missing dependency: jsonschema", file=sys.stderr)
        return 1

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    failures: list[str] = []
    checks = 0

    def case(label: str, instance: Any, should_pass: bool) -> None:
        nonlocal checks
        checks += 1
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        accepted = not errors
        if accepted != should_pass:
            want = "accepted" if should_pass else "rejected"
            got = "accepted" if accepted else f"rejected ({errors[0].message[:100]})"
            failures.append(f"{label}: expected {want}, was {got}")

    # Every section line below derives its OK/FAIL from `failures`, never from a bare
    # print(). The first version of this file printed "all 9 cells accepted" unconditionally
    # and duly printed it while 9 of 9 cells were failing on an unrelated regex bug. A gate
    # that narrates success independently of its own result is the exact defect this contract
    # exists to prevent, reproduced inside the checker for it.

    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    vectors = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))

    # ── the shipped example ────────────────────────────────────────────────────
    case("examples/lawful-dispatch-receipt.example.json", example, True)

    # Its seal must actually verify. An example carrying a placeholder digest would
    # teach every implementation to emit a placeholder digest.
    body = copy.deepcopy(example)
    recorded = body["seal"].pop("attestation")
    if seal(body) != recorded:
        failures.append(f"example seal does not verify: recorded {recorded}, recomputed {seal(body)}")
    checks += 1

    def with_factors(law: str, ev: str, verdict: str, tier: str = "T2") -> dict:
        r = copy.deepcopy(example)
        r["law"]["factor"], r["evidence"]["factor"] = law, ev
        r["verdict"], r["evidenceTier"] = verdict, tier
        # Keep the factor bodies consistent so a rejection can only be about the product.
        r["law"]["barCleared"] = law != "NEG"
        r["law"]["residual"] = [] if law == "POS" else ["citation.resolves"]
        if ev == "NEG":
            r["evidence"]["refuted"] = True
        elif ev == "ZERO":
            r["evidence"]["grounded"] = False
        return r

    # ── INVARIANT 1: every cell, both directions ───────────────────────────────
    print("  INVARIANT 1 — verdict = law × evidence (the meet, not the sign product)")
    for law in VERDICTS:
        for ev in VERDICTS:
            right = product(law, ev)
            case(f"{law} × {ev} = {right}", with_factors(law, ev, right), True)
            for wrong in [v for v in VERDICTS if v != right]:
                case(f"{law} × {ev} ≠ {wrong}", with_factors(law, ev, wrong), False)
    print(f"    {'OK  ' if not failures else 'FAIL'} 9 cells accepted, 18 wrong verdicts rejected")

    # The one cell that distinguishes a defensible product from a catastrophic one.
    case("NEG × NEG = POS — the sign-multiplication trap MUST be rejected",
         with_factors("NEG", "NEG", "POS"), False)
    print(f"    {'OK  ' if not failures else 'FAIL'} NEG × NEG = POS rejected (sign arithmetic would have said +1)")

    # ── INVARIANT 2: a declared factor cannot claim T1 ─────────────────────────
    print("  INVARIANT 2 — a declared factor cannot claim instrumented tier")
    for law_src, ev_src, tier, ok in [
        ("measured", "measured", "T1", True),
        ("measured", "measured", "T2", True),   # under-claiming is always allowed
        ("declared", "measured", "T2", True),
        ("measured", "declared", "T2", True),
        ("declared", "declared", "T2", True),
        ("declared", "measured", "T1", False),
        ("measured", "declared", "T1", False),
        ("declared", "declared", "T1", False),
    ]:
        r = copy.deepcopy(example)
        r["law"]["source"], r["evidence"]["source"], r["evidenceTier"] = law_src, ev_src, tier
        case(f"law={law_src} evidence={ev_src} tier={tier}", r, ok)
    print(f"    {'OK  ' if not failures else 'FAIL'} T1 rejected whenever either factor is declared; T2 always permitted")

    # ── the vectors must agree with the algebra ────────────────────────────────
    # The vector file is what cross-language implementations test against, so a typo there
    # would propagate into every consumer rather than being caught by one of them.
    print("  conformance vectors")
    for row in vectors["product"]["table"]:
        checks += 1
        if product(row["law"], row["evidence"]) != row["verdict"]:
            failures.append(f"vector disagrees with min(): {row}")
    if len(vectors["product"]["table"]) != 9:
        failures.append(f"product table must have 9 rows, has {len(vectors['product']['table'])}")
    for bad in vectors["product"]["mustNotHold"]:
        checks += 1
        if product(bad["law"], bad["evidence"]) == bad["verdict"]:
            failures.append(f"mustNotHold vector actually holds: {bad}")
        case(f"vector mustNotHold {bad['law']}×{bad['evidence']}={bad['verdict']}",
             with_factors(bad["law"], bad["evidence"], bad["verdict"]), False)
    print(f"    {'OK  ' if not failures else 'FAIL'} {len(vectors['product']['table'])} product rows agree "
          f"with min(); {len(vectors['product']['mustNotHold'])} mustNotHold rows rejected by the schema")

    # ── ordinary shape controls ────────────────────────────────────────────────
    print("  shape")

    def broken(mutation) -> dict:
        b = copy.deepcopy(example)
        mutation(b)
        return b

    for label, mut in [
        ("kind discriminator wrong", lambda b: b.__setitem__("kind", "SomeOtherReceipt")),
        ("dispatchId not the dispatch URN namespace", lambda b: b.__setitem__("dispatchId", "urn:srcos:other:x")),
        ("ts not a date-time", lambda b: b.__setitem__("ts", "yesterday")),
        ("verdict outside the ternary", lambda b: b.__setitem__("verdict", "MAYBE")),
        ("evidenceTier outside T1/T2", lambda b: b.__setitem__("evidenceTier", "T3")),
        ("attestation not sha256:hex", lambda b: b["seal"].__setitem__("attestation", "abcd")),
        ("prev neither genesis nor sha256:hex", lambda b: b["seal"].__setitem__("prev", "yesterday")),
        ("negative seq", lambda b: b["seal"].__setitem__("seq", -1)),
        ("requestHash not sha256:hex", lambda b: b["evidence"].__setitem__("requestHash", "deadbeef")),
        ("law.source outside measured/declared", lambda b: b["law"].__setitem__("source", "vibes")),
        ("residual item empty string", lambda b: b["law"].__setitem__("residual", [""])),
        ("missing law block entirely", lambda b: b.pop("law")),
        ("missing seal block entirely", lambda b: b.pop("seal")),
        ("undeclared property at root (schema is closed)", lambda b: b.__setitem__("zzUnknown", "leak")),
        ("undeclared property on law (schema is closed)", lambda b: b["law"].__setitem__("zzUnknown", "leak")),
    ]:
        case(label, broken(mut), False)
    print(f"    {'OK  ' if not failures else 'FAIL'} 15 shape controls rejected")

    if failures:
        print(f"\n{len(failures)} failure(s) of {checks} checks:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print(f"\nOK LawfulDispatchReceipt: {checks} checks. A receipt whose verdict does not equal "
          f"law × evidence, or which claims T1 on a declared factor, is invalid by shape.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
