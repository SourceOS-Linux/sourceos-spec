# ADR-0001 Appendix A — Reuse map + schema plan (B¹¹ / Δ / incidents)

**Date:** 2026-04-14  
**Status:** Proposed (appendix to ADR-0001)

---

## Purpose

ADR-0001 establishes the decision to add TruthSurface (B¹¹) and DeltaSurface (Δ) and to standardize incident semantics. This appendix makes the decision *actionable* by:

1) specifying a reuse-first mapping onto existing contracts already present in this repo, and  
2) enumerating the minimal net-new schema files + examples required for v0 portability.

---

## Reuse-first mapping

| Capability we need | Reuse (existing contracts / patterns) | Net-new (v0) |
|---|---|---|
| Signed “truth summary” per plane | Reuse **URN + `type` discriminator + `specVersion`** conventions (e.g., `TelemetryEvent`). Reuse existing evidence references (PolicyDecision/CapabilityToken/RunRecord/ProvenanceRecord) as *refs*, not embedded duplicates. | `schemas/TruthSurface.json` + `examples/truth-surface.sample.json` |
| Typed diff between two truth summaries | Reuse existing “risk + evidence + human approval” posture expressed in `policies/skills/default-policy-pack.rego` as the canonical gate style; DeltaSurface records the gate results, it does not *re-decide* policy. | `schemas/DeltaSurface.json` + `examples/delta-surface.sample.json` |
| Incident semantics (Freeze/Fork/Kill) | Reuse control-plane event structure conventions: `event_id`, `event_name`, `occurred_at`, `actor`, `run`, `refs`, `payload` as in the existing skill execution lifecycle schema and samples. | `schemas/control-plane/incident-events.schema.json` + `examples/control-plane/incident.freeze.sample.json` |
| Frontier / PBAC egress authorization | Reuse `CapabilityToken` as the short-lived signed grant primitive. Treat frontier/network constraints as a profile extension (additive) aligned to the existing governance lifecycle (decision → token). | v0: represent frontier intent + result refs in TruthSurface/DeltaSurface. v1: add an additive `frontier` block to `CapabilityToken.scope` (separate ADR if needed). |

---

## Schema plan (v0)

New schema files added in this PR branch:

1) `schemas/TruthSurface.json`
2) `schemas/DeltaSurface.json`
3) `schemas/control-plane/incident-events.schema.json`

New example payloads added in this PR branch:

1) `examples/truth-surface.sample.json`
2) `examples/delta-surface.sample.json`
3) `examples/control-plane/incident.freeze.sample.json`

---

## Non-goals for v0

- No OpenAPI/AsyncAPI surface changes yet (schemas stabilize first).
- No in-place `CapabilityToken` extension yet (we keep the profile extension as a documented plan until agreed).
- No enforcement logic (belongs in the substrate repo).

---

## Follow-on steps (expected)

1) Add OpenAPI/AsyncAPI patch entries for TruthSurface/DeltaSurface publishing endpoints + event channels.
2) Add conformance fixtures in workstation-contracts (schema validation + golden examples).
3) Implement substrate emitters/enforcers in SociOS-Linux/SourceOS (services + nftables + incident executor).

