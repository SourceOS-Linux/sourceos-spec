# ADR 9000: UMA Pistis ecosystem placement and lane split

- Status: Accepted
- Date: 2026-04-14

## Context

The SourceOS/SociOS repos already separate substrate, typed contracts, execution lanes, integration assembly, and opt-in automation. New local-first platform work introduced a human-readable naming layer (UMA Pistis, MICHAEL, PHAROS, PRAXIS, etc.) and an explicit requirement to preserve repo boundaries rather than collapse all work into one place.

At the same time, the build/control stack needs a clear split:

- Argo / Tekton for orchestration, pipeline execution, and GitOps-facing lane control
- Foreman / Katello for provisioning, content, repositories, promotion, and image/package lifecycle management

## Decision

1. The named UMA Pistis concepts are documented in `docs/UMA_PISTIS_PANTHEON_REGISTRY.md` as the human-readable mapping layer.
2. Machine-readable objects for those concepts must land first in `sourceos-spec` when they become normative contracts.
3. Runtime/integration behavior belongs in `agentos-spine`; immutable Linux posture belongs in `source-os`; lane validation and conformance belong in `workstation-contracts`; optional automation belongs in `socios`.
4. Argo / Tekton and Foreman / Katello are treated as complementary stack layers, not substitute choices.

## Consequences

### Positive

- New platform vocabulary can be discussed and aligned upstream before full schema work lands.
- Future contract additions have an explicit placement rule.
- The build/content stack is described without confusing execution lanes with content promotion.

### Negative

- The registry adds one more docs layer that must be kept aligned with schemas.
- Follow-on PRs are still required before these concepts become machine-enforced.

## Follow-on work

- Add MICHAEL, PRAXIS, ASHAMAAT, PHAROS/ARIADNE, IANUS, Codex, Kairos, and Shiloh contracts as additive schema/API changes.
- Add workstation-contracts documentation clarifying Argo/Tekton lane execution versus Foreman/Katello content/provisioning.
- Add agentos-spine docs explaining where CloudHaven / workspace composition belongs relative to these contracts.
