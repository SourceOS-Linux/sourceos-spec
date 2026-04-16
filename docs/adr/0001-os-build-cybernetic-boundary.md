# ADR-0001: OS build / cybernetic boundary contracts

**Date:** 2026-04-14  
**Status:** Proposed

---

## Context

The typed contract canon currently models metadata, governance, execution, provenance, agent sessions, release receipts, and related domain objects, but it does not yet expose a first-class boundary between:

1. immutable host image identity,
2. mutable install-time or enrollment-time node assignment, and
3. runtime cybernetic identity and control semantics.

Without this separation, downstream repos risk mixing environment, topology, runtime service identity, and control-loop meaning into image identity or installer state.

## Decision

Introduce three additive schema types:

- `OSImage`
- `NodeBinding`
- `CyberneticAssignment`

These contracts formalize the plane boundary as follows:

- `OSImage` owns immutable substrate identity, host ABI, boot/update posture, os-release identity, OCI metadata, and provenance references.
- `NodeBinding` owns install-time and enrollment-time mutable assignment such as topology, fleet, update ring, installer profile, registry mirrors, and bootstrap trust roots.
- `CyberneticAssignment` owns runtime service identity, deployment environment projection, policy refs, graph relations, and control objectives.

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Encode environment and runtime role directly in image naming | Pollutes immutable image identity and makes shared-image reuse brittle. |
| Put binding and cybernetic semantics into installer-only contracts | Loses a shared cross-repo canonical object model and makes runtime enforcement harder. |
| Keep the seam purely documentary with no schema types | Fails to make the boundary machine-checkable for downstream validation and release gating. |

## Consequences

Positive:

- gives downstream build, policy, runtime, and deployment repos a single canonical seam;
- enables validation rules that reject cybernetic leakage into immutable image metadata;
- supports additive rollout through existing SemVer and ADR discipline.

Negative:

- requires follow-on updates to schema catalog documentation, OpenAPI/AsyncAPI surfaces, semantic overlays, and changelog entries;
- introduces new URN namespaces that must be carried consistently in examples and downstream imports.

## References

- `docs/specs/canon.os-build.v1.md`
- `schemas/OSImage.json`
- `schemas/NodeBinding.json`
- `schemas/CyberneticAssignment.json`
