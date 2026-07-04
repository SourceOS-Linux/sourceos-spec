# ADR-0009 Appendix A — Reuse map + schema plan (B¹¹ / Δ)

**Date:** 2026-04-14  
**Status:** Accepted (appendix to ADR-0009)

---

## Purpose

This appendix makes ADR-0009 actionable by:

1) specifying a reuse-first mapping onto existing contracts already present in this repo, and  
2) enumerating the minimal net-new schema files + examples required for v0 portability.

---

## Reuse-first mapping

| Capability we need | Reuse (existing contracts / patterns) | Net-new (v0) |
|---|---|---|
| Signed “truth summary” per plane | Reuse **URN + `type` discriminator + `specVersion`** conventions (e.g., `TelemetryEvent`). Reuse existing evidence references (PolicyDecision/CapabilityToken/RunRecord/ProvenanceRecord) as *refs*, not embedded duplicates. | `schemas/TruthSurface.json` + `examples/truth_surface.json` |
| Typed diff between two truth summaries | Reuse existing “risk + evidence + human approval” posture expressed in `policies/skills/default-policy-pack.rego` as the canonical gate style; DeltaSurface records the gate results, it does not *re-decide* policy. | `schemas/DeltaSurface.json` + `examples/delta_surface.json` |
| Incident semantics (Freeze/Fork/Kill) | Reuse control-plane event structure conventions: `event_id`, `event_name`, `occurred_at`, `actor`, `run`, `refs`, `payload` as in the existing skill execution lifecycle schema and samples. | `schemas/control-plane/IncidentEvent.json` (canonical wrapper) + `schemas/control-plane/incident-events.schema.json` (legacy) + `examples/control-plane/incident.freeze.sample.json` |

---

## Schema plan (v0)

New schema files:

1) `schemas/TruthSurface.json`
2) `schemas/DeltaSurface.json`
3) `schemas/control-plane/IncidentEvent.json` (canonical wrapper)

Legacy schema retained for compatibility:

- `schemas/control-plane/incident-events.schema.json`

New example payloads:

1) `examples/truth_surface.json`
2) `examples/delta_surface.json`
3) `examples/control-plane/incident.freeze.sample.json`

---

## Notes

- OpenAPI/AsyncAPI patch fragments exist as additive files (`openapi.truth-plane.patch.yaml`, `asyncapi.truth-plane.patch.yaml`).
- Enforcement belongs in substrate/runtime repos; this repo defines contract shapes.
