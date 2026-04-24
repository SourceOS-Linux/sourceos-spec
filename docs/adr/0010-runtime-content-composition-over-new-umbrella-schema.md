# ADR-0010: runtime/content composition over a new umbrella schema

Date: 2026-04-24  
Status: Proposed

## Context

Recent architecture work across the workspace introduced useful language around phase-relative orchestration, governed execution posture, content-addressed curation, and deployment envelopes.

However, the SourceOS typed-contract layer already contains most of the primitives needed to express that model:

- `WorkloadSpec`
- `DataSphere`
- `ExecutionSurface`
- `ExecutionDecision`
- `RunRecord`
- `ContentRef`
- control-plane tranche wrappers for isolation/release posture where required

Creating a new umbrella schema that re-declares those fields would introduce a rival constitutional surface, increase duplication, and make it harder for downstream repos to know which type family is canonical.

## Decision

For runtime/content/orchestration alignment, this repository will prefer **composition from existing schema families** over creating a new top-level umbrella schema.

The rule is:

1. First express the concern using existing typed contracts and references.
2. If a true gap remains, add the smallest additive schema necessary.
3. Any additive schema must reference existing types rather than re-declaring their fields.
4. Vendor-specific names such as OpenShift, Giant Swarm, Docker, Podman, or Kubernetes should remain realization/adaptation concerns unless a generic contract cannot express the required semantics.

### Composition guidance

- Runnable unit identity and entrypoint → `WorkloadSpec`
- Execution boundary / trust posture → `DataSphere` and `ExecutionSurface`
- Allow/deny/ask/defer/rewrite control → `ExecutionDecision`
- Run/evidence linkage → `RunRecord`
- Content-addressed input/output references → `ContentRef`
- Release/isolation control-plane posture → control-plane tranche wrappers where appropriate

## Consequences

### Positive

- Preserves a single canonical contract layer.
- Keeps downstream repos aligned on existing `schemas.srcos.ai/v2/...` identities.
- Avoids needless field duplication and version drift.
- Keeps orchestrator/vendor names out of the stable schema identity unless truly necessary.

### Negative

- Some higher-level concepts may be less immediately convenient to describe in one document.
- Composition may require better guidance notes or examples for downstream implementers.
- If a real gap exists, we still need disciplined additive work rather than pretending composition solves everything.

## References

- Issue: #51
- Workspace placement anchor: SocioProphet/sociosphere#158
- Workspace codification PR: SocioProphet/sociosphere#159
