# ADR 0001 — Agentic Mesh Access and Workspace Contract Expansion

**Date:** 2026-04-14  
**Status:** `Proposed`

---

## Context

`SourceOS-Linux/sourceos-spec` already defines the canonical machine-readable contract layer for SourceOS/SociOS with a two-plane model: a metadata plane and an agent plane. The current agent-plane family already includes session, execution-decision, execution-surface, skill, memory, receipt, telemetry, and review objects.

That is necessary but no longer sufficient for the operating model now being aligned across SourceOS, agentplane, CloudShell/fog execution, Nocalhost-style remote development, and the broader SocioProphet standards stack.

The missing contract families are the ones required to model:

- local-first but globally reachable mesh routing
- governed operator remote shell access
- governed HTTP/service tunnel access
- developer workspaces and sync relationships
- approval, delegation, and break-glass posture
- proof-bearing evidence bundles and replay/export surfaces
- Git-backed desired-state and boot/recovery lifecycle artifacts
- placement decisions across local workstation, private cluster, fog, and optional burst cloud
- world-model claims, conflicts, and reconciliation outcomes emitted from operational activity

If these objects are left in runtime repos or prose-only standards repos, the contract authority will fragment. If they are forced into transport repositories, protocol concerns and product-surface semantics will be conflated. If they are placed in legacy distro/UI repositories, SourceOS loses a clean machine-readable spine.

---

## Decision

`SourceOS-Linux/sourceos-spec` remains the canonical owner for the machine-readable contract layer of the SourceOS/SociOS agentic mesh operating model.

The repository should add the following new first-class object families, in phased additive work:

### Access / route / session family

- `MeshRoute`
- `RemoteSession`
- `SessionRecording`
- `TunnelLease`
- `ApprovalRequest`
- `DelegationGrant`

### Workspace / developer execution family

- `DevSpace`
- `DevSync`

### Evidence / lifecycle / placement family

- `EvidenceBundle`
- `ProofPack`
- `ConfigSource`
- `ReleaseSet`
- `BootReleaseSet`
- `PlacementDecision`

### Knowledge reconciliation family

- `WorldStateClaim`
- `ConflictSet`
- `ReconciliationDecision`

These object families should be treated as additive extensions of the existing two-plane model rather than as a separate third specification. They should be published through the same core surfaces this repository already owns:

- JSON Schemas in `schemas/`
- OpenAPI base or agent-plane patch fragments, as appropriate
- AsyncAPI base or agent-plane patch fragments, as appropriate
- semantic context updates for first-class types
- example payloads and cross-object URN references

The repository boundary is explicit:

- `SourceOS-Linux/sourceos-spec` owns machine-readable object definitions and API/event contracts.
- `SocioProphet/socioprophet-agent-standards` owns normative profile, conformance, and behavioral standards.
- `SocioProphet/prophet-platform-standards` owns deployment, GitOps, RBAC, observability, and platform implementation standards.
- `SocioProphet/socioprophet-standards-storage` owns event/storage/measurement/compliance standards for these artifacts.
- `SocioProphet/socioprophet-standards-knowledge` owns knowledge/provenance/reconciliation semantics above the base contract layer.
- `SocioProphet/agentplane` owns runtime execution, placement, run, evidence-emission, and replay implementation.
- `SocioProphet/sociosphere` owns workspace manifest/lock/orchestration concerns, not downstream feature semantics.
- `SocioProphet/TriTRPC` owns transport and fixture semantics, not product-surface object ownership.

---

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Put the new object families directly into runtime repositories such as `agentplane` or `cloudshell-fog` | Rejected because runtime repos would become de facto schema authorities, causing duplicated contracts and drift. |
| Put the new object families only in standards/prose repositories | Rejected because the SourceOS operating model needs machine-readable contracts, not prose-only declarations. |
| Treat the new access/workspace model as a transport concern owned by `TriTRPC` | Rejected because transport and routing frames are not the same thing as operator sessions, tunnel leases, workspaces, or proof bundles. |
| Place the work in `SociOS-Linux` | Rejected because the current `SociOS-Linux` inventory is not the canonical SourceOS contract/spec spine. |
| Create a separate contract repository just for mesh access and workspaces | Rejected because that would fragment the existing two-plane contract authority and force downstream repos to stitch multiple specification roots together. |

---

## Consequences

### Positive

- SourceOS keeps a single machine-readable contract authority.
- Operator access, developer workspaces, release/boot artifacts, and knowledge reconciliation can all reference the same URN and API/event conventions.
- Downstream runtime and standards repos can consume a stable contract family instead of redefining object shapes.
- The local-first / fog / cloud placement story becomes part of the spec rather than an implementation accident.

### Negative

- The repository scope broadens and will require careful staging to avoid an oversized one-shot schema drop.
- Several downstream repos will need follow-on updates once the first object families land.
- The distinction between metadata-plane and agent-plane ownership must stay explicit so the contract layer does not become a dumping ground.

### Required follow-on

The next changes should be phased:

1. add the access / route / session family
2. add workspace objects and sync posture
3. add evidence / release / boot / placement objects
4. add reconciliation objects and semantic overlay links
5. update downstream standards and runtime repos to consume the canonical objects

---

## References

- `SourceOS-Linux/sourceos-spec`
- `SocioProphet/socioprophet-agent-standards`
- `SocioProphet/prophet-platform-standards`
- `SocioProphet/socioprophet-standards-storage`
- `SocioProphet/socioprophet-standards-knowledge`
- `SocioProphet/agentplane`
- `SocioProphet/sociosphere`
- `SocioProphet/TriTRPC`
