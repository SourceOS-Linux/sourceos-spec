#!/usr/bin/env python3
"""Validate OperationalDAG + GovernedLoop — the loops-vs-graphs governance (task #15).

Fail-closed:
  * OperationalDAG — every edge references real nodes, and the graph is ACYCLIC. A cycle is
    refused: a loop where a DAG belongs is unsatisfiable (identity/dependency can't be circular).
    Every node is semantically grounded (schema-required semanticRef).
  * GovernedLoop — is bounded (maxIterations ≥ 1), convergent (a measure), fail-closed
    (onNonConvergence ∈ {refuse, escalate-human}, never 'continue'), and admitted by the
    superconscious (admission.superconsciousRef). A loop that self-authorizes or cannot fail
    is not governed.
  * negative vectors fail on their named keyword.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DAG_SCHEMA = "OperationalDAG.json"
LOOP_SCHEMA = "GovernedLoop.json"
DAG_EXAMPLES = ["operational_dag.promotion.json"]
LOOP_EXAMPLES = ["governed_loop.vocab_currency.json"]

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def check_conformance(schema_name, examples) -> None:
    schema = load(ROOT / "schemas" / schema_name)
    jsonschema.Draft202012Validator.check_schema(schema)
    for name in examples:
        errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(load(ROOT / "examples" / name)), key=str)
        if errs:
            for e in errs:
                FAILURES.append(f"{name}: {e.message}")
        else:
            CHECKS[f"schema:{name}"] = True


def check_dag_acyclic(dags: dict[str, dict]) -> None:
    for name, dag in dags.items():
        node_ids = {n["id"] for n in dag["nodes"]}
        adj: dict[str, list[str]] = {n: [] for n in node_ids}
        ok_edges = True
        for e in dag["edges"]:
            if e["from"] not in node_ids or e["to"] not in node_ids:
                FAILURES.append(f"{name}: edge {e['from']}→{e['to']} references a node not in the DAG")
                ok_edges = False
            else:
                adj[e["from"]].append(e["to"])
        if ok_edges:
            CHECKS[f"dag:{name}:edges-resolve"] = True

        # DFS cycle detection — a cycle is refused (a loop where a DAG belongs).
        WHITE, GREY, BLACK = 0, 1, 2
        color = {n: WHITE for n in node_ids}

        def dfs(u: str) -> bool:
            color[u] = GREY
            for v in adj[u]:
                if color[v] == GREY or (color[v] == WHITE and dfs(v)):
                    return True
            color[u] = BLACK
            return False

        if any(color[n] == WHITE and dfs(n) for n in node_ids):
            FAILURES.append(f"{name}: OperationalDAG has a CYCLE — identity/dependency cannot be circular; "
                            f"model correction as a GovernedLoop, not a cycle here")
        else:
            CHECKS[f"dag:{name}:acyclic"] = True


def check_loop_governed(loops: dict[str, dict]) -> None:
    for name, lp in loops.items():
        if lp["bound"]["maxIterations"] < 1:
            FAILURES.append(f"{name}: loop bound must be ≥ 1 (a loop that cannot terminate is not governed)")
        elif lp["onNonConvergence"] not in ("refuse", "escalate-human"):
            FAILURES.append(f"{name}: onNonConvergence must be fail-closed (refuse|escalate-human), not silent spin")
        elif not lp["admission"].get("superconsciousRef"):
            FAILURES.append(f"{name}: loop must be admitted by the superconscious — loops don't self-authorize")
        else:
            CHECKS[f"loop:{name}:bounded-convergent-failclosed-admitted"] = True


def check_negatives() -> None:
    fx = load(ROOT / "fixtures" / "dag-loop" / "conformance.json")
    schemas = {s: load(ROOT / "schemas" / s) for s in (DAG_SCHEMA, LOOP_SCHEMA)}
    for i, case in enumerate(fx["cases"]):
        exp = case.get("failValidator")
        try:
            jsonschema.validate(case["document"], schemas[case["schema"]])
            FAILURES.append(f"negative {i} unexpectedly PASSED: {case['reason']}")
        except jsonschema.ValidationError as exc:
            if exp and exc.validator != exp:
                FAILURES.append(f"negative {i}: failed on {exc.validator!r}, not {exp!r}")
            else:
                CHECKS[f"negative:{i}:{exc.validator}"] = True


def main() -> int:
    check_conformance(DAG_SCHEMA, DAG_EXAMPLES)
    check_conformance(LOOP_SCHEMA, LOOP_EXAMPLES)
    dags = {n: load(ROOT / "examples" / n) for n in DAG_EXAMPLES}
    loops = {n: load(ROOT / "examples" / n) for n in LOOP_EXAMPLES}
    check_dag_acyclic(dags)
    check_loop_governed(loops)
    check_negatives()

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
