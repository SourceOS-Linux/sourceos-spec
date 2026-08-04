#!/usr/bin/env python3
"""Validate the image-trust family: ImageTrustReport, AgentImage, ImagePromotionGate.

Three checks, the same discipline the Assay uses one level down (claims → images):
  1. schema conformance — every example validates against its schema, with the
     ImageTrustReport check.measurement `$ref` resolved to Measurement.json (so a
     'declared'/'assumed' measurement is gate-ineligible by shape);
  2. projection soundness — projectedTrust recomputed from the checks must match the
     recorded value (ok/sad/bad is an executable projection, not a stored opinion);
  3. gate soundness — an ImagePromotionGate with decision 'approved' must reference an
     ImageTrustReport that projects 'ok'. An approval cannot be self-asserted.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]

# schemas that participate in $ref resolution (ImageTrustReport → Measurement)
REGISTRY_SCHEMAS = ["Measurement.json", "ImageTrustReport.json", "AgentImage.json", "ImagePromotionGate.json"]

PAIRS = [
    ("ImageTrustReport.json", "image_trust_report.os.json"),
    ("ImageTrustReport.json", "image_trust_report.agent.json"),
    ("AgentImage.json", "agent_image.json"),
    ("ImagePromotionGate.json", "image_promotion_gate.json"),
]

TRUST_REPORTS = ["image_trust_report.os.json", "image_trust_report.agent.json"]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_registry() -> Registry:
    resources = []
    for name in REGISTRY_SCHEMAS:
        doc = _load(ROOT / "schemas" / name)
        resources.append((doc["$id"], Resource.from_contents(doc)))
    return Registry().with_resources(resources)


def project_trust(checks: list[dict]) -> str:
    """Recompute the ok/sad/bad trust verdict from the measured checks.

    bad — a gate-eligible measurement recorded a failure (passed:false).
    ok  — every check is gate-eligible AND passed.
    sad — otherwise (a declared/derived/assumed or partly-unobserved check, none failed).
    """
    if any(c["passed"] is False and c["measurement"].get("gateEligible") is True for c in checks):
        return "bad"
    if all(c["passed"] is True and c["measurement"].get("gateEligible") is True for c in checks):
        return "ok"
    return "sad"


def main() -> int:
    registry = build_registry()
    checks: dict[str, bool] = {}

    for schema_name, example_name in PAIRS:
        schema = _load(ROOT / "schemas" / schema_name)
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema, registry=registry)
        validator.validate(_load(ROOT / "examples" / example_name))
        checks[example_name] = True

    # projection soundness
    reports_by_id: dict[str, dict] = {}
    for name in TRUST_REPORTS:
        report = _load(ROOT / "examples" / name)
        reports_by_id[report["id"]] = report
        recomputed = project_trust(report["checks"])
        if report["projectedTrust"] != recomputed:
            raise SystemExit(
                f"projection mismatch in {name}: recorded={report['projectedTrust']!r} "
                f"but project_trust()={recomputed!r}"
            )
        checks[f"projection:{name}"] = True

    # gate soundness — approved requires a backing report that projects ok
    gate = _load(ROOT / "examples" / "image_promotion_gate.json")
    if gate["decision"] == "approved":
        ref = gate.get("trustReportRef")
        report = reports_by_id.get(ref)
        if report is None:
            raise SystemExit(f"gate approved but trustReportRef {ref!r} is not a known ImageTrustReport")
        if report["projectedTrust"] != "ok":
            raise SystemExit(
                f"gate approved but referenced report {ref} projects {report['projectedTrust']!r}, not 'ok'"
            )
    checks["gate:image_promotion_gate.json"] = True

    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
