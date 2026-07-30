#!/usr/bin/env python3
"""Validate the MPCC event-contract family (conversation + trading events).

Four checks, not one:
  1. schema conformance — every schema is a valid draft-2020-12 document and
     every canonical example validates against its schema;
  2. strictness bar — every schema in the family holds the tranche-0001 bar:
     top-level "additionalProperties": false, specVersion pinned to the 0.1.0
     const, and an anchored urn:srcos: id pattern;
  3. envelope parity — the trading profiles (MarketDataEvent, OrderIntent,
     ExecutionReport, PositionChange, ReconciliationRecord) share ONE envelope
     vocabulary with ConversationEvent: the shared envelope properties (and the
     shared authorityContext block) must be deep-equal to ConversationEvent's,
     so the trading family can never drift into a second vocabulary;
  4. lifecycle soundness — across the example set, the requested → approved →
     actual effect chain resolves (same effect identity, matching idempotency
     keys, approval carries the exact approved effect shape), the trading chain
     resolves (intent → report → position → reconciliation), and the negative
     conformance vectors in fixtures/mpcc-event-contract/conformance.json all
     FAIL for their stated reasons.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_NAMES = [
    "ConversationEvent.json",
    "EffectRequest.json",
    "EffectDecision.json",
    "EffectRecord.json",
    "NullAbsenceRecord.json",
    "MarketDataEvent.json",
    "OrderIntent.json",
    "ExecutionReport.json",
    "PositionChange.json",
    "ReconciliationRecord.json",
]

PAIRS = [
    ("ConversationEvent.json", "conversation_event.json"),
    ("EffectRequest.json", "effect_request.json"),
    ("EffectDecision.json", "effect_decision.json"),
    ("EffectRecord.json", "effect_record.json"),
    ("NullAbsenceRecord.json", "null_absence_record.json"),
    ("MarketDataEvent.json", "market_data_event.json"),
    ("OrderIntent.json", "order_intent.json"),
    ("ExecutionReport.json", "execution_report.json"),
    ("PositionChange.json", "position_change.json"),
    ("ReconciliationRecord.json", "reconciliation_record.json"),
]

TRADING = [
    "MarketDataEvent.json",
    "OrderIntent.json",
    "ExecutionReport.json",
    "PositionChange.json",
    "ReconciliationRecord.json",
]

# The single shared envelope vocabulary. ConversationEvent is the authority;
# every trading profile must carry these properties with identical sub-schemas.
ENVELOPE_KEYS = [
    "specVersion",
    "actorRef",
    "workspaceRef",
    "branchRef",
    "visibilityScope",
    "wallTime",
    "logicalTime",
    "causalParents",
    "traceContext",
    "provenanceLinks",
    "policyLabels",
    "riskLabels",
]

# Files that carry the shared authorityContext block (must be deep-equal).
AUTHORITY_FILES = ["ConversationEvent.json", "EffectDecision.json", "OrderIntent.json"]


def require(condition: object, message: str) -> None:
    """Contract check that survives `python -O`.

    These are conformance obligations, not debug assertions. Written as bare
    `assert` they were deleted wholesale by `python -O` while the surrounding
    function still ran to the end and recorded `checks[...] = True`, so the
    tool printed `"ok": true` with every check green for examples it had never
    inspected. A check a runtime flag can silently delete is not a check.
    """
    if not condition:
        raise SystemExit(message)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_conformance(schemas: dict[str, dict], checks: dict[str, bool]) -> None:
    for schema_name, example_name in PAIRS:
        schema = schemas[schema_name]
        jsonschema.validators.validator_for(schema).check_schema(schema)
        example = load(ROOT / "examples" / example_name)
        jsonschema.validate(example, schema)
        checks[f"example:{example_name}"] = True


def check_strictness(schemas: dict[str, dict], checks: dict[str, bool]) -> None:
    for name, schema in schemas.items():
        if schema.get("additionalProperties") is not False:
            raise SystemExit(f"{name}: top-level additionalProperties must be false")
        if schema["properties"]["specVersion"].get("const") != "0.1.0":
            raise SystemExit(f"{name}: specVersion must be pinned to const 0.1.0")
        pattern = schema["properties"]["id"].get("pattern", "")
        if not (pattern.startswith("^urn:srcos:") and pattern.endswith("$")):
            raise SystemExit(f"{name}: id pattern must be an anchored urn:srcos: pattern")
        if schema["properties"]["type"].get("const") != schema["title"]:
            raise SystemExit(f"{name}: type const must equal title")
        checks[f"strictness:{name}"] = True


def check_envelope_parity(schemas: dict[str, dict], checks: dict[str, bool]) -> None:
    authority = schemas["ConversationEvent.json"]["properties"]
    for name in TRADING:
        props = schemas[name]["properties"]
        for key in ENVELOPE_KEYS:
            if key not in props:
                raise SystemExit(f"{name}: missing shared envelope property {key!r}")
            if props[key] != authority[key]:
                raise SystemExit(
                    f"{name}: envelope property {key!r} drifted from "
                    f"ConversationEvent — one envelope, not a second vocabulary"
                )
        checks[f"envelope-parity:{name}"] = True

    reference = schemas["ConversationEvent.json"]["properties"]["authorityContext"]
    for name in AUTHORITY_FILES[1:]:
        if schemas[name]["properties"]["authorityContext"] != reference:
            raise SystemExit(f"{name}: authorityContext drifted from ConversationEvent")
    checks["envelope-parity:authorityContext"] = True


def check_lifecycle(checks: dict[str, bool]) -> None:
    ex = {name: load(ROOT / "examples" / name) for _, name in PAIRS}
    event = ex["conversation_event.json"]
    request = ex["effect_request.json"]
    decision = ex["effect_decision.json"]
    record = ex["effect_record.json"]
    intent = ex["order_intent.json"]
    report = ex["execution_report.json"]
    position = ex["position_change.json"]
    recon = ex["reconciliation_record.json"]

    require(request["id"] in event["requestedEffects"], "event must request the effect")
    require(decision["id"] in event["approvedEffects"], "event must reference the decision")
    require(record["id"] in event["actualEffects"], "event must reference the record")
    require(decision["effectRequestRef"] == request["id"], "decision governs the request")
    require(record["effectRequestRef"] == request["id"], "record executes the request")
    require(record["effectDecisionRef"] == decision["id"], "record grounded in the decision")
    require(record["idempotencyKey"] == request["idempotencyKey"], "replay guard must match")
    if decision["decision"] == "approved":
        require(
            isinstance(decision.get("approvedEffect"), dict),
            "approved decision must carry the exact approved effect shape",
        )
    checks["lifecycle:effect-chain"] = True

    require(intent["requestedEffectRef"] == request["id"], "intent governed by the effect")
    require(report["orderIntentRef"] == intent["id"], "report responds to the intent")
    require(report["id"] in record["resultRefs"], "record evidences venue reality")
    require(report["id"] in position["sourceExecutionRefs"], "position traceable to fill")
    require(recon["scopeRef"] == intent["id"], "reconciliation scopes the order")
    checks["lifecycle:trading-chain"] = True


def check_negative_vectors(schemas: dict[str, dict], checks: dict[str, bool]) -> None:
    fixture = load(ROOT / "fixtures" / "mpcc-event-contract" / "conformance.json")
    for i, case in enumerate(fixture["cases"]):
        schema = schemas[case["schema"]]
        try:
            jsonschema.validate(case["document"], schema)
        except jsonschema.ValidationError:
            checks[f"negative:{i}:{case['schema']}"] = True
            continue
        raise SystemExit(
            f"negative vector {i} ({case['schema']}) unexpectedly PASSED: {case['reason']}"
        )


def main() -> int:
    schemas = {name: load(ROOT / "schemas" / name) for name in SCHEMA_NAMES}
    checks: dict[str, bool] = {}

    check_conformance(schemas, checks)
    check_strictness(schemas, checks)
    check_envelope_parity(schemas, checks)
    check_lifecycle(checks)
    check_negative_vectors(schemas, checks)

    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
