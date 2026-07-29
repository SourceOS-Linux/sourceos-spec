#!/usr/bin/env python3
"""Validate the SemanticAction contract family (the declarative typed-action registry).

Five checks, not one:
  1. schema conformance — the schema is a valid draft-2020-12 document and
     every canonical example validates against it;
  2. strictness bar — the schema holds the tranche-0001 bar: top-level
     "additionalProperties": false, specVersion pinned to the 0.1.0 const, an
     anchored urn:srcos: id pattern, and a type const equal to the title;
  3. binding soundness — across the example set: input names are unique within
     each action, and every constraint subject resolves to a declared input
     name or the literal "output" (the planner must never meet a dangling
     constraint subject);
  4. purity posture — the schema's sideEffects vocabulary is exactly
     {"none", "effect-request"} (no direct-mutation value may ever be added
     silently), and the example set exercises both postures, including an
     effect-request action whose output is the EffectRequest proposal itself;
  5. negative vectors — fixtures/semantic-action/conformance.json all FAIL
     for their stated reasons.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_NAME = "SemanticAction.json"

EXAMPLES = [
    "semantic_action.json",
    "semantic_action.effect_request.json",
]

SIDE_EFFECTS_VOCABULARY = ["none", "effect-request"]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_conformance(schema: dict, checks: dict[str, bool]) -> None:
    jsonschema.validators.validator_for(schema).check_schema(schema)
    for example_name in EXAMPLES:
        example = load(ROOT / "examples" / example_name)
        jsonschema.validate(example, schema)
        checks[f"example:{example_name}"] = True


def check_strictness(schema: dict, checks: dict[str, bool]) -> None:
    if schema.get("additionalProperties") is not False:
        raise SystemExit(f"{SCHEMA_NAME}: top-level additionalProperties must be false")
    if schema["properties"]["specVersion"].get("const") != "0.1.0":
        raise SystemExit(f"{SCHEMA_NAME}: specVersion must be pinned to const 0.1.0")
    pattern = schema["properties"]["id"].get("pattern", "")
    if not (pattern.startswith("^urn:srcos:") and pattern.endswith("$")):
        raise SystemExit(f"{SCHEMA_NAME}: id pattern must be an anchored urn:srcos: pattern")
    if schema["properties"]["type"].get("const") != schema["title"]:
        raise SystemExit(f"{SCHEMA_NAME}: type const must equal title")
    checks[f"strictness:{SCHEMA_NAME}"] = True


def check_binding_soundness(checks: dict[str, bool]) -> None:
    for name in EXAMPLES:
        action = load(ROOT / "examples" / name)
        input_names = [slot["name"] for slot in action["inputs"]]
        assert len(input_names) == len(set(input_names)), (
            f"{name}: input names must be unique within an action"
        )
        subjects = set(input_names) | {"output"}
        for constraint in action["constraints"]:
            assert constraint["subject"] in subjects, (
                f"{name}: constraint subject {constraint['subject']!r} does not "
                f"resolve to a declared input name or \"output\""
            )
        checks[f"binding-soundness:{name}"] = True


def check_purity_posture(schema: dict, checks: dict[str, bool]) -> None:
    vocabulary = schema["properties"]["sideEffects"].get("enum")
    if vocabulary != SIDE_EFFECTS_VOCABULARY:
        raise SystemExit(
            f"{SCHEMA_NAME}: sideEffects vocabulary must be exactly "
            f"{SIDE_EFFECTS_VOCABULARY} — no direct-mutation value may be added silently"
        )
    postures = {}
    for name in EXAMPLES:
        action = load(ROOT / "examples" / name)
        postures[action["sideEffects"]] = action
    assert set(postures) == set(SIDE_EFFECTS_VOCABULARY), (
        "example set must exercise both sideEffects postures"
    )
    effect_action = postures["effect-request"]
    assert "EffectRequest" in effect_action["output"]["typeRef"], (
        "the effect-request example's output must be the EffectRequest proposal "
        "itself — the action proposes, it never acts directly"
    )
    checks["purity-posture:vocabulary"] = True
    checks["purity-posture:examples"] = True


def check_negative_vectors(schema: dict, checks: dict[str, bool]) -> None:
    fixture = load(ROOT / "fixtures" / "semantic-action" / "conformance.json")
    for i, case in enumerate(fixture["cases"]):
        if case["schema"] != SCHEMA_NAME:
            raise SystemExit(f"negative vector {i} targets unexpected schema {case['schema']}")
        try:
            jsonschema.validate(case["document"], schema)
        except jsonschema.ValidationError:
            checks[f"negative:{i}:{case['schema']}"] = True
            continue
        raise SystemExit(
            f"negative vector {i} ({case['schema']}) unexpectedly PASSED: {case['reason']}"
        )


def main() -> int:
    schema = load(ROOT / "schemas" / SCHEMA_NAME)
    checks: dict[str, bool] = {}

    check_conformance(schema, checks)
    check_strictness(schema, checks)
    check_binding_soundness(checks)
    check_purity_posture(schema, checks)
    check_negative_vectors(schema, checks)

    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
