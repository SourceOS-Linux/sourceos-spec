#!/usr/bin/env python3
"""CI harness for the LIVE vocab-currency GovernedLoop — asserts the GOVERNANCE, not just that
it runs. A loop is only trustworthy if it (a) makes the vocab current when it can, (b) escalates
fail-closed when it cannot within the bound, and (c) refuses to run unadmitted. All three are
teeth: the divergent case must NOT silently pass, the unadmitted case must NOT self-authorize."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vocab_currency_loop as vcl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures" / "vocab-currency"
LOOP = ROOT / "examples" / "governed_loop.vocab_currency.json"
LOOP_SCHEMA = ROOT / "schemas" / "GovernedLoop.json"
GLOSSARY_SCHEMA = ROOT / "schemas" / "GlossaryTerm.json"

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def check_contract_conforms() -> None:
    # Schema conformance FIRST (like the repo's other validators) — so a drifted contract fails
    # with a clear conformance error, not a downstream KeyError from run_loop.
    errs = sorted(jsonschema.Draft202012Validator(vcl.load(LOOP_SCHEMA)).iter_errors(vcl.load(LOOP)), key=str)
    if errs:
        for e in errs:
            FAILURES.append(f"shipped GovernedLoop contract invalid: {e.message}")
    else:
        CHECKS["contract:conforms"] = True


def run(corpus_name: str, loop_override: dict | None = None) -> dict:
    loop = loop_override or vcl.load(LOOP)
    return vcl.run_loop(loop, vcl.load(FIX / "glossary.json"), vcl.load(FIX / corpus_name))


def main() -> int:
    check_contract_conforms()

    # 1. Convergent corpus — the loop connects the few new terms and reaches currency (ok).
    r = run("corpus.json")
    if not r.get("ok"):
        FAILURES.append(f"convergent corpus should reach currency, got {r.get('escalated') or r.get('refused')}")
    elif r["finalDivergence"] > r["tolerance"]:
        FAILURES.append("declared converged but divergence exceeds tolerance")
    else:
        CHECKS["convergent:reaches-currency"] = True

    # 1b. Every proposed remediation artifact MUST conform to GlossaryTerm.json and be status:draft
    #     — the loop proposes drafts for ontogenesis, it must never emit a malformed or self-approved
    #     term. (Uses the divergent run too, which proposes the most terms.)
    gt = jsonschema.Draft202012Validator(vcl.load(GLOSSARY_SCHEMA))
    proposals = r.get("proposedTerms", []) + run("corpus_divergent.json").get("proposedTerms", [])
    bad = [(t.get("id"), e.message) for t in proposals for e in gt.iter_errors(t)]
    self_approved = [t.get("id") for t in proposals if t.get("status") != "draft"]
    if bad:
        FAILURES.append(f"proposed term(s) do not conform to GlossaryTerm.json: {bad[:3]}")
    elif self_approved:
        FAILURES.append(f"proposed term(s) not status:draft — the loop must not self-approve: {self_approved[:3]}")
    elif not proposals:
        FAILURES.append("expected the loop to emit proposed draft terms, got none")
    else:
        CHECKS["proposed-terms:conform-and-draft"] = True

    # 2. Divergent corpus — a domain the vocab cannot name within the bound MUST escalate,
    #    never silently succeed, never spin past maxIterations.
    r = run("corpus_divergent.json")
    if r.get("ok"):
        FAILURES.append("divergent corpus silently PASSED — the loop failed open")
    elif r.get("escalated") != "escalate-human":
        FAILURES.append(f"divergent corpus should escalate-human, got {r.get('escalated')!r}")
    elif r["iterations"] > r["maxIterations"]:
        FAILURES.append("loop exceeded its bound — it spun")
    else:
        CHECKS["divergent:escalates-fail-closed"] = True

    # 3. Unadmitted loop — strip admission; the loop must REFUSE (loops don't self-authorize).
    unadmitted = vcl.load(LOOP)
    unadmitted["admission"] = {"superconsciousRef": ""}
    r = run("corpus.json", loop_override=unadmitted)
    if r.get("refused") != "unadmitted":
        FAILURES.append("a loop with no superconscious admission must be REFUSED, not run")
    else:
        CHECKS["unadmitted:refused"] = True

    # 4. Unsupported convergence measure — a contract declaring a measure this runner does not
    #    implement (e.g. fixpoint) MUST be refused, not run with mismatched semantics.
    mismatched = vcl.load(LOOP)
    mismatched["convergence"] = {**mismatched["convergence"], "measure": "fixpoint", "tolerance": None}
    r = run("corpus.json", loop_override=mismatched)
    if r.get("refused") != "unsupported-measure":
        FAILURES.append("a loop whose convergence measure the runner can't honor must be REFUSED")
    else:
        CHECKS["unsupported-measure:refused"] = True

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
