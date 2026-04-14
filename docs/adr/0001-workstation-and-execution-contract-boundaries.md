# ADR 0001 — Workstation and Execution Contract Boundaries

**Date:** 2026-04-14  
**Status:** `Proposed`

---

## Context

SourceOS has two related but distinct needs:

1. A canonical typed contract layer for the execution fabric: agent sessions, execution decisions, telemetry, provenance, release receipts, and policy-bound execution surfaces.
2. A reproducible workstation profile for developer/operator environments on GNOME/CoreOS/Silverblue-derived systems, including package manifests, desktop defaults, launcher actions, and input remapping.

Recent design work also clarified additional execution-layer concepts that are not yet first-class types in this repository:

- **Run Capsule** — immutable, signed record of one agent execution, including inputs, outputs, tool calls, decisions, and ledger state.
- **Agent Contract** — declarative description of an agent’s tools, policies, deployment profiles, and audit requirements.

The risk is that workstation/profile work lands as ad hoc shell scripts while execution-fabric work lands separately, producing drift between:

- what an agent is declared to be allowed to do,
- what the workstation exposes as launcher/actions/tools,
- and what the audit/provenance layer records.

## Decision

We will treat both execution-fabric objects and workstation-profile objects as first-class typed contracts in `sourceos-spec`, but we will phase them differently.

### Phase 1 — ADR + RFC first

Before adding schemas, we record the architectural boundary:

- **Execution contracts** define what an agent/session/run may do and what must be recorded.
- **Workstation contracts** define what a workstation profile installs, configures, and exposes to users/operators.

### Phase 2 — Additive schema families

We will add the following types as additive contracts once field definitions stabilize:

#### Execution-facing types

- `RunCapsule`
- `AgentContract`

#### Workstation-facing types

- `WorkstationProfile`
- `PackageManifest`
- `DesktopProfile`
- `LauncherAction`
- `LauncherProvider`

### Contract boundary rule

Workstation-facing types must not redefine execution/audit semantics already owned by execution-facing contracts.

Specifically:

- `WorkstationProfile` may reference `AgentContract`, but does not embed policy logic in an incompatible form.
- `LauncherAction` may reference execution surfaces/capabilities, but audit/provenance requirements remain owned by execution contracts such as `RunCapsule`, `ExecutionDecision`, and related receipts.
- Desktop/launcher affordances are a presentation/configuration layer over the canonical capability and audit plane, not a parallel authority system.

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Keep workstation profile work only in build/config repos with no typed contract | Rejected because it creates drift and weakens policy/audit interoperability |
| Add all new schemas immediately | Rejected because the field model is not yet stable enough and would likely cause churn |
| Keep execution contracts in one repo and workstation contracts in a separate spec repo | Rejected because the contract boundary between launcher/desktop actions and audited execution would become harder to govern |

## Consequences

### Positive

- Keeps `sourceos-spec` as the canonical contract home for both audited execution and workstation profile semantics.
- Prevents launcher/desktop integrations from becoming undocumented side channels.
- Provides a clean path for GNOME/Albert/Kinto/Fusuma integration to reference the same capability and audit model as the broader SourceOS execution fabric.
- Allows build/config repos in `SociOS-Linux` to remain implementation-focused while `SourceOS-Linux/sourceos-spec` remains contract-focused.

### Negative

- Introduces more schema surface area that will need careful versioning and examples.
- Requires discipline to avoid over-modeling early design details.
- Forces workstation profile work to meet the same compatibility rigor as the rest of the contract layer.

## References

- `SourceOS-Linux/sourceos-spec/README.md`
- `SourceOS-Linux/sourceos-spec/CONTRIBUTING.md`
- `SociOS-Linux/enhancements/workstation/sourceos_workstation_profile_v0.md`
