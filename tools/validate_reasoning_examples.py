#!/usr/bin/env python3
"""Validate the reasoning-run contract family, including the epistemic Assay.

Two checks, not one:
  1. schema conformance — every example validates against its schema;
  2. projection soundness — for each ReasoningAssay, the reference assay()
     projection recomputed from the stored axes matches the recorded
     projectedState. This keeps the ok/sad/bad readout an *executable*
     projection of the tuple rather than a stored opinion that can drift.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    (ROOT / "schemas" / "ReasoningRun.json", ROOT / "examples" / "reasoning_run.json"),
    (ROOT / "schemas" / "ReasoningEvent.json", ROOT / "examples" / "reasoning_event.json"),
    (ROOT / "schemas" / "ReasoningEvent.json", ROOT / "examples" / "reasoning_event_control_flow.json"),
    (ROOT / "schemas" / "ReasoningReceipt.json", ROOT / "examples" / "reasoning_receipt.json"),
    (ROOT / "schemas" / "ReasoningReplayPlan.json", ROOT / "examples" / "reasoning_replay_plan.json"),
    (ROOT / "schemas" / "ReasoningBenchmark.json", ROOT / "examples" / "reasoning_benchmark.json"),
    (ROOT / "schemas" / "AssayStandard.json", ROOT / "examples" / "assay_standard.json"),
    (ROOT / "schemas" / "ReasoningAssay.json", ROOT / "examples" / "reasoning_assay.json"),
    (ROOT / "schemas" / "ReasoningAssay.json", ROOT / "examples" / "reasoning_assay.unassayed.json"),
    (ROOT / "schemas" / "ReasoningAssay.json", ROOT / "examples" / "reasoning_assay.refuted.json"),
]

ASSAY_EXAMPLES = [
    ROOT / "examples" / "reasoning_assay.json",
    ROOT / "examples" / "reasoning_assay.unassayed.json",
    ROOT / "examples" / "reasoning_assay.refuted.json",
]


def load_standards() -> dict[str, dict]:
    """Index every AssayStandard fixture by its URN so assay() can look up
    whether a verdict's verifier is actually calibrated."""
    standards: dict[str, dict] = {}
    for path in ROOT.glob("examples/*.json"):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(doc, dict) and doc.get("type") == "AssayStandard":
            standards[doc["id"]] = doc
    return standards


def assay(record: dict, standards: dict[str, dict]) -> str:
    """Reference projection: recompute the ok/sad/bad readout from the axes.

    bad  — authority is broken (envelope integrity did not verify).
    ok   — inline-bound AND method is attestable (computed/retrieved)
           AND the verifier points at a calibrated AssayStandard.
    sad  — everything else: unassayed / unresolved but not refuted.
    """
    authority = record.get("authority", {})
    if authority.get("integrityVerified") is False:
        return "bad"

    calibration_ref = record["verifier"]["calibrationRef"]
    standard = standards.get(calibration_ref)
    calibrated = bool(standard and standard.get("calibrated"))

    inline = record["binding"] == "inline"
    attestable = record["method"] in ("computed", "retrieved")

    if inline and attestable and calibrated:
        return "ok"
    return "sad"


def validate_pair(schema_path: Path, example_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema).check_schema(schema)
    example = json.loads(example_path.read_text(encoding="utf-8"))
    jsonschema.validate(example, schema)


def main() -> int:
    checks: dict[str, bool] = {}

    for schema_path, example_path in PAIRS:
        validate_pair(schema_path, example_path)
        checks[example_path.name] = True

    standards = load_standards()
    for example_path in ASSAY_EXAMPLES:
        record = json.loads(example_path.read_text(encoding="utf-8"))
        recorded = record.get("projectedState")
        recomputed = assay(record, standards)
        if recorded != recomputed:
            raise SystemExit(
                f"projection mismatch in {example_path.name}: "
                f"recorded={recorded!r} but assay()={recomputed!r}"
            )
        checks[f"projection:{example_path.name}"] = True

    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
