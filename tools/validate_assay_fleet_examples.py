#!/usr/bin/env python3
"""Validate the Assay fleet-tier contracts (cloud-mesh): AssayRollup + AssayStandardRollout.

Schema conformance plus aggregation/rollout soundness — the same discipline as the
node-tier validator, one level up:
  * a rollup's ok/sad/bad counts must sum to totalAssays, its unassayedReasons must
    not exceed the sad band, its standardAdoption node counts must match scope, and
    driftDetected must agree with what the adoption table actually shows;
  * a rollout's rolloutPct must match its promoted/observing node share, its
    guard.decision must be consistent with its phase, and it may not have widened
    past canary without an observed rollup (no promotion-by-hope).
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

PCT_TOLERANCE = 0.5

PAIRS = [
    (ROOT / "schemas" / "AssayRollup.json", ROOT / "examples" / "assay_rollup.json"),
    (ROOT / "schemas" / "AssayStandardRollout.json", ROOT / "examples" / "assay_standard_rollout.json"),
]


def check_rollup(r: dict, name: str) -> None:
    dist = r["distribution"]
    total = r["totalAssays"]
    dist_sum = dist["ok"] + dist["sad"] + dist["bad"]
    if dist_sum != total:
        raise SystemExit(f"rollup {name}: distribution sums to {dist_sum} but totalAssays={total}")

    for field in ("byMethod", "unassayedReasons"):
        block = r.get(field)
        if not block:
            continue
        s = sum(block.values())
        cap = dist["sad"] if field == "unassayedReasons" else total
        if s > cap:
            raise SystemExit(f"rollup {name}: {field} sums to {s} but cap is {cap}")

    adoption = r.get("standardAdoption")
    if adoption:
        node_sum = sum(a["nodeCount"] for a in adoption)
        if node_sum != r["scope"]["nodeCount"]:
            raise SystemExit(
                f"rollup {name}: standardAdoption node counts sum to {node_sum} "
                f"but scope.nodeCount={r['scope']['nodeCount']}"
            )
        versions = {a["calibrationRef"] for a in adoption}
        any_uncalibrated = any(not a["calibrated"] for a in adoption)
        expected_drift = len(versions) > 1 or any_uncalibrated
        if "driftDetected" in r and r["driftDetected"] != expected_drift:
            raise SystemExit(
                f"rollup {name}: driftDetected={r['driftDetected']} but adoption table "
                f"(versions={len(versions)}, any_uncalibrated={any_uncalibrated}) implies {expected_drift}"
            )


def check_rollout(r: dict, name: str) -> None:
    cohorts = r["cohorts"]
    total_nodes = sum(c["nodeCount"] for c in cohorts)
    on_new = sum(c["nodeCount"] for c in cohorts if c["state"] in ("promoted", "observing"))
    if "rolloutPct" in r and total_nodes:
        expected = 100.0 * on_new / total_nodes
        if abs(r["rolloutPct"] - expected) > PCT_TOLERANCE:
            raise SystemExit(
                f"rollout {name}: rolloutPct={r['rolloutPct']} but promoted/observing share "
                f"is {expected:.1f}% ({on_new}/{total_nodes})"
            )

    phase = r["phase"]
    guard = r.get("guard") or {}
    decision = guard.get("decision")
    if decision:
        expected_phase = {
            "continue": {"canary", "widening", "complete"},
            "hold": {"halted"},
            "rollback": {"rolled-back"},
        }[decision]
        if phase not in expected_phase:
            raise SystemExit(
                f"rollout {name}: guard.decision={decision!r} is inconsistent with phase={phase!r}"
            )

    # No promotion-by-hope: past canary requires an observed rollup.
    if phase in ("widening", "complete") and not guard.get("observedRollupRef"):
        raise SystemExit(
            f"rollout {name}: phase={phase!r} but no guard.observedRollupRef — widening "
            "must be gated on an observed AssayRollup, not hope"
        )


def validate_pair(schema_path: Path, example_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema).check_schema(schema)
    example = json.loads(example_path.read_text(encoding="utf-8"))
    jsonschema.validate(example, schema)
    if example.get("type") == "AssayRollup":
        check_rollup(example, example_path.name)
    if example.get("type") == "AssayStandardRollout":
        check_rollout(example, example_path.name)


def main() -> int:
    checks: dict[str, bool] = {}
    for schema_path, example_path in PAIRS:
        validate_pair(schema_path, example_path)
        checks[example_path.name] = True
    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
