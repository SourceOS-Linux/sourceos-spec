# ADR-0001 — Truth Surfaces (B¹¹) + Δ-Surfaces + Incident Semantics

**Date:** 2026-04-14  
**Status:** Proposed

---

## Context

We need a *portable, machine-verifiable* way to represent “what is true right now” about:

- the immutable substrate (host integrity and policy posture),
- the controlled user space (governed meaning and intent),
- the agent space (bounded execution and decisions), and
- the witness/replication posture (what was attested externally).

In practice, the system already carries many of these primitives:

- The **two-plane contract model** (metadata plane + agent plane) and additive patch strategy (`openapi*.yaml`, `asyncapi*.yaml`).
- A **short-lived signed grant** primitive (`schemas/CapabilityToken.json`) derived from policy decisions.
- A **control-plane event lifecycle** style (e.g., `schemas/control-plane/skill-execution-events.schema.json`) and a default skill policy pack (`policies/skills/default-policy-pack.rego`).
- A concrete *mesh skill* example that already encodes deterministic plans, evidence requirements, and Cairn refs (`examples/control-plane/mesh-skill.checkout-validate.yaml`).

What is missing is a canonical “truth object” that can be:

1) generated deterministically,  
2) signed and Merkle-addressed,  
3) compared across time and planes (Δ), and  
4) gated/promoted with explicit thresholds and evidence requirements.

We also need incident semantics that are explicit and replayable (Freeze → Fork → Kill) rather than implicit operational folklore.

## Decision

### 1) Add two new contract types (schema family) to `sourceos-spec`

We introduce **TruthSurface** (B¹¹) and **DeltaSurface** (Δ) as first-class contract objects, published alongside the existing schema families.

- **TruthSurface (B¹¹)**: a signed, Merkle-addressed summary for a given plane (`sealed/system`, `controlled/user`, `open/agent`, `witness/twin`).
- **DeltaSurface (Δ)**: a signed diff between two TruthSurfaces with:
  - semantic drift metrics,
  - runtime drift metrics,
  - governance deltas,
  - a promotion recommendation + gate results.

These new types must compose cleanly with existing primitives (TelemetryEvent, ExecutionDecision, PolicyDecision/CapabilityToken, ProvenanceRecord) rather than replacing them.

### 2) Represent “PBAC tickets” as a CapabilityToken profile, not a new token class

Off-box / frontier egress authorization is expressed as a **CapabilityToken** profile extension:

- add network scope constraints (e.g., `frontier_hops`, `targets`, `egress_class`) as structured fields,
- keep the existing governance flow (evaluate → decision → issue token),
- ensure tokens remain short-lived and auditable.

This prevents parallel token taxonomies.

### 3) Standardize incident semantics as contract-level events

We define incident semantics as a small set of event types aligned with the existing control-plane event lifecycle style:

- `incident.freeze`
- `incident.fork`
- `incident.kill`

Each event MUST carry:
- actor context (human/agent/service),
- run/trace linkage (when applicable),
- refs to evidence bundles and pre/post Cairn anchors,
- status progression compatible with existing control-plane conventions.

### 4) Promotion gates are contract-level, evidence-first

Promotion of a surface (or a claim derived from it) requires explicit gate checks:

- evidence bundle completeness (required evidence list satisfied),
- risk threshold checks,
- approval rules (e.g., human approval required for certain classes),
- semantic coherence thresholds,
- runtime integrity thresholds.

We explicitly reuse the posture already present in `policies/skills/default-policy-pack.rego` (risk gating, human approval requirement, evidence requirement checking) as the canonical style baseline.

### 5) Keep enforcement out of this repository

`sourceos-spec` defines **what** a surface/token/event is.
Enforcement remains the responsibility of the substrate and runtime implementations (e.g., `SociOS-Linux/SourceOS`).

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Put truth surfaces directly in the substrate repo only | Breaks the “canonical contract registry” role of this repo; makes portability and interoperability harder. |
| Create a new standalone “truth-surface spec” repo | Fragments the spec; duplicates identity/versioning discipline; increases coordination overhead. |
| Use only existing TelemetryEvent/ExecutionDecision structures | Those are necessary components but not sufficient as a signed, Merkle-addressed *summary surface* with promotion gating and Δ comparison. |

## Consequences

Positive:
- A single canonical contract for truth, drift, and gating across planes.
- Enables conformance fixtures and independent validators (e.g., workstation lanes).
- Allows implementations to evolve while remaining interoperable (schemas, OpenAPI, AsyncAPI, JSON-LD).

Negative:
- Adds schema surface area that must be versioned and maintained.
- Requires a clear reuse map to prevent duplication with existing agent-plane primitives.

## References

- `ARCHITECTURE.md` — two-plane model and patch-file composition strategy.
- `schemas/CapabilityToken.json` — existing short-lived signed grant primitive.
- `schemas/control-plane/skill-execution-events.schema.json` — lifecycle event conventions.
- `policies/skills/default-policy-pack.rego` — baseline risk/evidence/approval gating style.
- `examples/control-plane/mesh-skill.checkout-validate.yaml` — deterministic plan + evidence requirements + Cairn refs.
- `examples/control-plane/skill.evidence.attached.sample.json` — concrete event sample for evidence attachment.
