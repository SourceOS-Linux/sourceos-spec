#!/usr/bin/env python3
"""Validate the reasoning-run contract family, including the epistemic Assay.

Three checks, not one:
  1. schema conformance — every example validates against its schema;
  2. measurement soundness — an AssayStandard's derived F1, declared metrics,
     and 'calibrated' flag must agree; a verdict's effectiveVotes cannot exceed
     its arms. Self-asserted trust is rejected: the numbers must corroborate;
  3. projection soundness — for each ReasoningAssay, the reference assay()
     projection recomputed from the stored axes matches the recorded
     projectedState. This keeps the ok/sad/bad readout an *executable*
     projection of the tuple rather than a stored opinion that can drift.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_CALIBRATION_THRESHOLD = 0.6
METRIC_TOLERANCE = 0.02

PAIRS = [
    (ROOT / "schemas" / "ReasoningRun.json", ROOT / "examples" / "reasoning_run.json"),
    (ROOT / "schemas" / "ReasoningEvent.json", ROOT / "examples" / "reasoning_event.json"),
    (ROOT / "schemas" / "ReasoningEvent.json", ROOT / "examples" / "reasoning_event_control_flow.json"),
    (ROOT / "schemas" / "ReasoningReceipt.json", ROOT / "examples" / "reasoning_receipt.json"),
    (ROOT / "schemas" / "ReasoningReplayPlan.json", ROOT / "examples" / "reasoning_replay_plan.json"),
    (ROOT / "schemas" / "ReasoningBenchmark.json", ROOT / "examples" / "reasoning_benchmark.json"),
    (ROOT / "schemas" / "AssayStandard.json", ROOT / "examples" / "assay_standard.json"),
    (ROOT / "schemas" / "AssayStandard.json", ROOT / "examples" / "assay_standard.uncalibrated.json"),
    (ROOT / "schemas" / "ReasoningAssay.json", ROOT / "examples" / "reasoning_assay.json"),
    (ROOT / "schemas" / "ReasoningAssay.json", ROOT / "examples" / "reasoning_assay.unassayed.json"),
    (ROOT / "schemas" / "ReasoningAssay.json", ROOT / "examples" / "reasoning_assay.refuted.json"),
]

ASSAY_EXAMPLES = [
    ROOT / "examples" / "reasoning_assay.json",
    ROOT / "examples" / "reasoning_assay.unassayed.json",
    ROOT / "examples" / "reasoning_assay.refuted.json",
]


def derived_f1(matrix: dict) -> float:
    """F1 from raw confusion-matrix counts. The matrix is authoritative;
    declared metrics and the 'calibrated' flag are checked against this."""
    tp = matrix["truePositive"]
    fp = matrix["falsePositive"]
    fn = matrix["falseNegative"]
    denom = 2 * tp + fp + fn
    return (2 * tp / denom) if denom else 0.0


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


def check_standard_soundness(standard: dict, name: str) -> None:
    """A verifier cannot declare itself trustworthy. F1 derived from the
    confusion matrix must agree with any declared metrics, and the 'calibrated'
    flag must equal (derivedF1 >= calibrationThreshold)."""
    f1 = derived_f1(standard["confusionMatrix"])
    metrics = standard.get("metrics", {})
    if "f1" in metrics and abs(metrics["f1"] - f1) > METRIC_TOLERANCE:
        raise SystemExit(
            f"metric mismatch in {name}: declared f1={metrics['f1']} "
            f"but confusionMatrix implies {f1:.3f}"
        )
    if "calibrated" in standard:
        threshold = standard.get("calibrationThreshold", DEFAULT_CALIBRATION_THRESHOLD)
        expected = f1 >= threshold
        if standard["calibrated"] != expected:
            raise SystemExit(
                f"calibration mismatch in {name}: flag calibrated={standard['calibrated']} "
                f"but derivedF1={f1:.3f} vs threshold={threshold} implies {expected}"
            )


def check_agreement_soundness(record: dict, name: str) -> None:
    agreement = record.get("agreement")
    if not agreement:
        return
    arms = agreement.get("arms")
    votes = agreement.get("effectiveVotes")
    if arms is not None and votes is not None and votes > arms:
        raise SystemExit(
            f"agreement mismatch in {name}: effectiveVotes={votes} exceeds arms={arms} "
            "(decorrelation can only reduce vote weight, never inflate it)"
        )


def assay(record: dict, standards: dict[str, dict]) -> str:
    """Reference projection: recompute the ok/sad/bad readout from the axes.

    bad  — authority is broken (envelope integrity failed), OR the claim was
           refuted by a *calibrated* verifier.
    ok   — verifier judgment is 'supported' AND binding is inline AND method is
           attestable (computed/retrieved) AND the verifier is calibrated.
    sad  — everything else: unassayed / unresolved but not decisively refuted
           (post-hoc binding, generated method, uncalibrated verifier, an
           abstention, or a refutation the verifier isn't calibrated to force).
    """
    authority = record.get("authority", {})
    if authority.get("integrityVerified") is False:
        return "bad"

    verifier = record["verifier"]
    standard = standards.get(verifier["calibrationRef"])
    calibrated = bool(standard and standard.get("calibrated"))
    judgment = verifier["judgment"]

    if judgment == "refuted":
        return "bad" if calibrated else "sad"

    inline = record["binding"] == "inline"
    attestable = record["method"] in ("computed", "retrieved")
    if judgment == "supported" and inline and attestable and calibrated:
        return "ok"
    return "sad"


def validate_pair(schema_path: Path, example_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema).check_schema(schema)
    example = json.loads(example_path.read_text(encoding="utf-8"))
    jsonschema.validate(example, schema)
    if example.get("type") == "AssayStandard":
        check_standard_soundness(example, example_path.name)
    if example.get("type") == "ReasoningAssay":
        check_agreement_soundness(example, example_path.name)


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
