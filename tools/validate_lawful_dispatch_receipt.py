#!/usr/bin/env python3
"""Validate LawfulDispatchReceipt: Truth = Law × Evidence, enforced by the CONTRACT.

The estate's governance thesis is that a dispatch is true only when both a Law factor and
an Evidence factor are established. Stating that in a docstring is worth nothing — the
Noetica ledger stated it for its whole life while every call site passed the literal 'POS',
and 34 of 53 real entries recorded `grounded: false` next to `verdict: 'POS'` in the same
object. A per-app implementation can always drift back into that. A schema cannot.

So the governance rules live in the schema, where any validator in any language enforces
them without trusting the emitter. There are FOUR, and the last two were missing from the
first revision:

  INVARIANT 1  verdict == law.factor × evidence.factor, where × is the MEET in the chain
               NEG < ZERO < POS (strong-Kleene conjunction, i.e. min). The 9 branches are
               GENERATED from min(), so the schema cannot disagree with the algebra by
               typo. Critically this is NOT sign multiplication in {-1,0,+1}: that reading
               gives NEG × NEG = POS, certifying a refused gate with a refuted outcome as
               true. This validator asserts that exact receipt is REJECTED.

  INVARIANT 2  evidenceTier T1 is unavailable when either factor is 'declared'. T1 means
               instrumented; claiming it for a value no instrument produced is the same
               defect one level up.

  INVARIANT 3  law.factor is a FUNCTION of (barCleared, residual), enforced both ways.
  INVARIANT 4  evidence.factor is a FUNCTION of (digests, grounded, refuted), both ways.

               3 and 4 were found by adversarial probe after the first revision shipped, and
               they matter more than 1 and 2. Binding the verdict to its factors while
               leaving the factors unbound enforces nothing: all six of these were ACCEPTED
               — `law.factor: POS` alongside `barCleared: false`, an `evidence.factor: POS`
               carrying no digests at all — and the product then faithfully multiplied the
               lie. Enforcing an invariant one level too high is indistinguishable from not
               enforcing it. Now checked exhaustively: 12 law and 24 evidence combinations,
               accepting only the derivable factor, plus the six attacks by name.

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
    r"""ensure_ascii=False is load-bearing: Python's default escapes non-ASCII as \uXXXX while
    JavaScript's JSON.stringify emits it raw, so the default would make every seal over
    non-ASCII content diverge between languages."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


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

    def broken_factor(base: dict, mutation) -> dict:
        b = copy.deepcopy(base)
        mutation(b)
        return b

    def with_factors(law: str, ev: str, verdict: str, tier: str = "T2") -> dict:
        r = copy.deepcopy(example)
        r["law"]["factor"], r["evidence"]["factor"] = law, ev
        r["verdict"], r["evidenceTier"] = verdict, tier
        # Each factor body must DERIVE its declared factor, or invariants 3/4 reject the
        # receipt and every product case below becomes vacuous — passing for the wrong
        # reason. This is the same trap as comparing two empty result sets and calling them
        # identical, so the derivations are spelled out rather than approximated.
        r["law"]["barCleared"] = law != "NEG"
        r["law"]["residual"] = ["citation.resolves"] if law == "ZERO" else []
        r["evidence"].pop("refuted", None)
        if ev == "NEG":
            r["evidence"]["refuted"] = True
            r["evidence"]["grounded"] = True
        elif ev == "ZERO":
            r["evidence"]["grounded"] = False
        else:
            r["evidence"]["grounded"] = True
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

    # ── INVARIANTS 3 & 4: each FACTOR is a function of the record ──────────────
    # Found by adversarial probe AFTER the first version shipped: the product invariant
    # binds verdict to the factors, but nothing bound the factors to their own evidence.
    # All six of these were ACCEPTED — `law.factor: POS` with `barCleared: false`, an
    # `evidence.factor: POS` carrying no digests at all — and the product then faithfully
    # multiplied the lie. Enforcing the product one level too high enforces nothing.
    print("  INVARIANTS 3 & 4 — each factor is a function of the record it derives from")

    def law_factor(cleared: bool, residual: list[str]) -> str:
        return "NEG" if not cleared else ("POS" if not residual else "ZERO")

    def evidence_factor(digests: bool, grounded: bool, refuted: bool) -> str:
        return "NEG" if refuted else ("POS" if digests and grounded else "ZERO")

    import itertools
    a_hash = example["evidence"]["requestHash"]

    # Exhaustive over the law inputs: only the derivable factor may be accepted, so the
    # schema is checked for admitting too much AND for refusing what it should allow.
    for cleared, residual in itertools.product([True, False], [[], ["citation.resolves"]]):
        right = law_factor(cleared, residual)
        for claim in VERDICTS:
            r = copy.deepcopy(example)
            r["law"] = {"factor": claim, "barCleared": cleared, "residual": residual, "source": "measured"}
            r["verdict"] = product(claim, r["evidence"]["factor"])
            case(f"law claim={claim} barCleared={cleared} residual={len(residual)}", r, claim == right)
    print(f"    {'OK  ' if not failures else 'FAIL'} 12 law combinations: only the derivable factor accepted")

    for digests, grounded, refuted in itertools.product([True, False], [True, False], [True, False]):
        right = evidence_factor(digests, grounded, refuted)
        for claim in VERDICTS:
            r = copy.deepcopy(example)
            ev: dict[str, Any] = {"factor": claim, "grounded": grounded, "source": "measured"}
            if digests:
                ev["requestHash"], ev["answerHash"] = a_hash, a_hash
            if refuted:
                ev["refuted"] = True
            r["evidence"] = ev
            r["verdict"] = product(r["law"]["factor"], claim)
            case(f"evidence claim={claim} digests={digests} grounded={grounded} refuted={refuted}", r, claim == right)
    print(f"    {'OK  ' if not failures else 'FAIL'} 24 evidence combinations: only the derivable factor accepted")

    # The six attacks by name, so a future edit that reopens one of them fails loudly rather
    # than merely dropping a count.
    for label, mut in [
        ("law POS while the gate REFUSED", lambda b: (b["law"].update({"factor": "POS", "barCleared": False}), b.update({"verdict": "POS"}))),
        ("law POS carrying undischarged residual", lambda b: b["law"].update({"factor": "POS", "residual": ["citation.resolves"]})),
        ("evidence POS while refuted", lambda b: b["evidence"].update({"factor": "POS", "refuted": True})),
        ("evidence POS with NO digests at all", lambda b: (b["evidence"].pop("requestHash"), b["evidence"].pop("answerHash"))),
        ("evidence POS while ungrounded", lambda b: b["evidence"].update({"factor": "POS", "grounded": False})),
        ("evidence POS with grounded absent entirely", lambda b: b["evidence"].pop("grounded")),
    ]:
        case(f"ATTACK: {label}", broken_factor(example, mut), False)
    print(f"    {'OK  ' if not failures else 'FAIL'} all 6 factor-forging attacks rejected by name")

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
    # canonicalJson and contentHash define the SEAL, so the vectors must be self-consistent:
    # a wrong expected value here propagates into every consumer rather than being caught by
    # one of them. Recomputed with this file's own canonicaliser, which is also what the
    # example receipt's seal was checked against above.
    for cs in vectors["canonicalJson"]["cases"]:
        checks += 1
        got = canonical_json(cs["input"])
        if got != cs["expected"]:
            failures.append(f"canonicalJson vector: input {cs['input']!r} expected {cs['expected']!r}, got {got!r}")
    for cs in vectors["contentHash"]["cases"]:
        checks += 1
        got = "sha256:" + hashlib.sha256(canonical_json(cs["input"]).encode("utf-8")).hexdigest()
        if got != cs["expected"]:
            failures.append(f"contentHash vector: input {cs['input']!r} expected {cs['expected']}, got {got}")
    # And at least one case must exercise non-ASCII, or the ensure_ascii trap is untested.
    checks += 1
    if not any(any(ord(ch) > 127 for ch in json.dumps(c["input"], ensure_ascii=False))
               for c in vectors["canonicalJson"]["cases"]):
        failures.append("canonicalJson vectors contain no non-ASCII case — the ensure_ascii trap is untested")
    print(f"    {'OK  ' if not failures else 'FAIL'} {len(vectors['canonicalJson']['cases'])} canonicalJson + "
          f"{len(vectors['contentHash']['cases'])} contentHash cases agree, non-ASCII covered")

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
