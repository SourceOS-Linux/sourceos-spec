#!/usr/bin/env python3
"""Validate the KnowledgeNugget contract family (the estate's L2 content grain).

Five checks, not one:
  1. schema conformance — the schema is a valid draft-2020-12 document and
     every canonical example validates against it;
  2. strictness bar — the schema holds the tranche-0001 bar: top-level
     "additionalProperties": false, specVersion pinned to the 0.1.0 const, an
     anchored urn:srcos: id pattern, and a type const equal to the title;
  3. envelope consistency — the wallTime and logicalTime sub-schemas are
     deep-equal to the MPCC ConversationEvent envelope's, so the content grain
     can never drift into a second time vocabulary;
  4. warrant soundness — across the example set: span offsets are ordered
     (end >= start), a direct-quote span's length equals its text length
     (exactness), computed/inferred warrants carry at least one evidence ref,
     and the set exercises the admissibility contrast (at least one
     direct-quote and at least one model-generated nugget, so downstream
     surfaces always have both poles to distinguish);
  5. negative vectors — fixtures/knowledge-nugget/conformance.json all FAIL
     for their stated reasons.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_NAME = "KnowledgeNugget.json"
ENVELOPE_AUTHORITY = "ConversationEvent.json"

EXAMPLES = [
    "knowledge_nugget.json",
    "knowledge_nugget.model_generated.json",
]

# Time vocabulary carried verbatim from the MPCC ConversationEvent envelope.
TIME_KEYS = ["wallTime", "logicalTime"]


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


def check_envelope_consistency(schema: dict, checks: dict[str, bool]) -> None:
    authority = load(ROOT / "schemas" / ENVELOPE_AUTHORITY)["properties"]
    props = schema["properties"]
    for key in TIME_KEYS:
        if key not in props:
            raise SystemExit(f"{SCHEMA_NAME}: missing shared envelope property {key!r}")
        if props[key] != authority[key]:
            raise SystemExit(
                f"{SCHEMA_NAME}: envelope property {key!r} drifted from "
                f"ConversationEvent — one time vocabulary, not a second one"
            )
        checks[f"envelope-consistency:{key}"] = True


def check_warrant_soundness(checks: dict[str, bool]) -> None:
    examples = [load(ROOT / "examples" / name) for name in EXAMPLES]
    warrant_types = set()
    for name, nugget in zip(EXAMPLES, examples):
        span = nugget["sourceRef"]["span"]
        assert span["end"] >= span["start"], f"{name}: span.end must be >= span.start"
        warrant = nugget["warrant"]
        warrant_types.add(warrant["type"])
        if warrant["type"] == "direct-quote":
            assert span["end"] - span["start"] == len(nugget["text"]), (
                f"{name}: a direct-quote span must be exactly as long as its text"
            )
        if warrant["type"] in ("computed", "inferred"):
            assert len(warrant["evidence"]) >= 1, (
                f"{name}: computed/inferred warrants must cite evidence"
            )
    assert "direct-quote" in warrant_types, "example set must include a direct-quote nugget"
    assert "model-generated" in warrant_types, (
        "example set must include a model-generated nugget — the admissibility "
        "contrast must stay exercised"
    )
    checks["warrant-soundness:examples"] = True


def check_negative_vectors(schema: dict, checks: dict[str, bool]) -> None:
    fixture = load(ROOT / "fixtures" / "knowledge-nugget" / "conformance.json")
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
    check_envelope_consistency(schema, checks)
    check_warrant_soundness(checks)
    check_negative_vectors(schema, checks)

    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
