#!/usr/bin/env python3
"""Validate the EvalItem schema — the atomic contract of the Provider Eval Seed
Strategy that feeds the Intelligence-Superiority Bench (iSOTA).

An EvalItem declares which corpus it belongs to (A provider-seed / B Sherlock-task /
C adversarial), its task family, the question, the traits an answer must have, how
it is graded, and its risk class. Load-bearing minimums are asserted by REJECTION:
an item with no expected traits is ungradeable, and a provider-sourced item must
name its provider (the harness stays neutral — provider is a label, never a winner).
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "EvalItem.json"
EXAMPLE = ROOT / "examples" / "eval-item.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> int:
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    v = Draft202012Validator(schema)

    example = load(EXAMPLE)
    errors = sorted(v.iter_errors(example), key=lambda e: list(e.path))
    if errors:
        loc = ".".join(str(p) for p in errors[0].path) or "<root>"
        fail(f"eval-item.json invalid: {loc}: {errors[0].message}")

    def must_reject(label: str, mutate) -> None:
        doc = mutate(copy.deepcopy(example))
        if v.is_valid(doc):
            fail(f"{label}: document was ACCEPTED but must be rejected")

    def drop(key):
        return lambda d: {k: val for k, val in d.items() if k != key}

    must_reject("EvalItem empty expected_answer_traits (ungradeable)", lambda d: {**d, "expected_answer_traits": []})
    must_reject("EvalItem unknown task_family", lambda d: {**d, "task_family": "vibes_check"})
    must_reject("EvalItem unknown corpus", lambda d: {**d, "corpus": "D"})
    must_reject("EvalItem missing grading_method", drop("grading_method"))
    must_reject("EvalItem missing risk_class", drop("risk_class"))
    must_reject("EvalItem provider source without provider name",
                lambda d: {**{k: val for k, val in d.items() if k != "provider"}, "source": "provider"})

    print("OK: EvalItem — schema + example validated; 6 rejection invariants enforced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
