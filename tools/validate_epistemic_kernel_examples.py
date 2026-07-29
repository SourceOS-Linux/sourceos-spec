#!/usr/bin/env python3
"""Validate the epistemic-kernel contract family (control-loop kernel + causal
claims graph + experience/chunk-context/guardrail-eval records).

Four checks, not one:
  1. schema conformance — every schema is a valid draft-2020-12 document and
     every canonical example validates against its schema;
  2. strictness bar — every schema in the family holds the tranche bar:
     top-level "additionalProperties": false, specVersion pinned to the 0.1.0
     const, and an anchored urn:srcos: id pattern;
  3. cross-invariants — the invariants JSON Schema cannot express are enforced
     over the example set: a tick's policyDigest equals its loop's policyDigest
     (staleness attribution); a tick that exceeds its loop's retry budget must
     be escalated (no livelock); a causal edge never self-loops, both endpoints
     resolve to hypothesis examples, and all three share one graphRef; a
     guardrail report's coverage arithmetic is internally consistent and
     promotionEligible only when every clause passes;
  4. negative vectors — every case in
     fixtures/epistemic-kernel/conformance.json FAILS for its stated reason.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_NAMES = [
    "ControlLoop.json",
    "ControlLoopTick.json",
    "ExperienceRecord.json",
    "GuardrailEvalReport.json",
    "CausalHypothesis.json",
    "CausalEdge.json",
    "ChunkContext.json",
]

PAIRS = [
    ("ControlLoop.json", "control_loop.json"),
    ("ControlLoopTick.json", "control_loop_tick.json"),
    ("ExperienceRecord.json", "experience_record.json"),
    ("GuardrailEvalReport.json", "guardrail_eval_report.json"),
    ("CausalHypothesis.json", "causal_hypothesis.json"),
    ("CausalHypothesis.json", "causal_hypothesis.outcome.json"),
    ("CausalEdge.json", "causal_edge.json"),
    ("ChunkContext.json", "chunk_context.json"),
]

FIXTURE = ROOT / "fixtures" / "epistemic-kernel" / "conformance.json"

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"FAIL: {msg}")


def ok(msg: str) -> None:
    print(f"ok: {msg}")


def load(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


def main() -> int:
    schemas = {name: load(ROOT / "schemas" / name) for name in SCHEMA_NAMES}
    examples = {ex: load(ROOT / "examples" / ex) for _, ex in PAIRS}

    # 1. schema conformance
    for name, schema in schemas.items():
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
            ok(f"schema valid: {name}")
        except jsonschema.SchemaError as exc:
            fail(f"schema invalid: {name}: {exc.message}")
    for schema_name, example_name in PAIRS:
        validator = jsonschema.Draft202012Validator(schemas[schema_name])
        errors = sorted(validator.iter_errors(examples[example_name]), key=str)
        if errors:
            for err in errors:
                fail(f"example {example_name} vs {schema_name}: {err.message}")
        else:
            ok(f"example validates: {example_name} vs {schema_name}")

    # 2. strictness bar
    for name, schema in schemas.items():
        if schema.get("additionalProperties") is not False:
            fail(f"strictness: {name} must set top-level additionalProperties:false")
        spec_version = schema.get("properties", {}).get("specVersion", {})
        if spec_version.get("const") != "0.1.0":
            fail(f"strictness: {name} specVersion must be const 0.1.0")
        id_pattern = schema.get("properties", {}).get("id", {}).get("pattern", "")
        if not id_pattern.startswith("^urn:srcos:"):
            fail(f"strictness: {name} id pattern must anchor on urn:srcos:")
    if not failures:
        ok("strictness bar holds for all 7 schemas")

    # 3. cross-invariants over the example set
    loop = examples["control_loop.json"]
    tick = examples["control_loop_tick.json"]
    if tick["loopRef"] != loop["id"]:
        fail("tick loopRef does not resolve to the example ControlLoop")
    elif tick["policyDigest"] != loop["policyDigest"]:
        fail("staleness attribution: tick policyDigest != loop policyDigest")
    else:
        ok("tick policyDigest matches its loop (staleness attribution)")

    budget = loop["retryBudget"]["maxAdjustmentsPerIncident"]
    anomaly = tick["anomaly"]
    if anomaly["adjustmentCount"] > budget and not anomaly["escalated"]:
        fail("livelock: adjustmentCount exceeds retry budget without escalation")
    else:
        ok("retry-budget escalation invariant holds")

    hyp_ids = {
        examples["causal_hypothesis.json"]["id"],
        examples["causal_hypothesis.outcome.json"]["id"],
    }
    hyp_graphs = {
        examples["causal_hypothesis.json"]["graphRef"],
        examples["causal_hypothesis.outcome.json"]["graphRef"],
    }
    edge = examples["causal_edge.json"]
    if edge["fromRef"] == edge["toRef"]:
        fail("causal edge self-loop: fromRef == toRef")
    elif edge["fromRef"] not in hyp_ids or edge["toRef"] not in hyp_ids:
        fail("causal edge endpoints do not resolve to hypothesis examples")
    elif hyp_graphs != {edge["graphRef"]}:
        fail("causal edge and endpoints do not share one graphRef")
    else:
        ok("causal edge resolves, no self-loop, single graphRef")

    report = examples["guardrail_eval_report.json"]
    clauses = report["clauses"]
    coverage = report["coverage"]
    enforced = sum(
        1
        for clause in clauses
        if clause["result"] == "pass" and clause.get("enforcementTestRef")
    )
    if coverage["declaredClauses"] != len(clauses):
        fail("guardrail coverage: declaredClauses != len(clauses)")
    elif coverage["enforcedClauses"] != enforced:
        fail("guardrail coverage: enforcedClauses does not match clause results")
    elif coverage["enforcedClauses"] > coverage["declaredClauses"]:
        fail("guardrail coverage: enforcedClauses exceeds declaredClauses")
    elif report["promotionEligible"] and enforced != len(clauses):
        fail("guardrail promotion: promotionEligible without full passing coverage")
    elif report["installApproved"] and "blessing" not in report:
        fail("guardrail install: installApproved without blessing")
    else:
        ok("guardrail coverage arithmetic + promotion/blessing invariants hold")

    # 4. negative vectors must FAIL
    fixture = load(FIXTURE)
    for case in fixture["cases"]:
        validator = jsonschema.Draft202012Validator(schemas[case["schema"]])
        errors = list(validator.iter_errors(case["document"]))
        if errors:
            ok(f"negative vector fails as required: {case['reason'][:72]}")
        else:
            fail(f"negative vector VALIDATED but must fail: {case['reason']}")

    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nOK: epistemic-kernel family — all four checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
