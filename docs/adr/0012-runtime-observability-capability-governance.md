# ADR-0012: Runtime observability and capability governance contracts

## Status

Accepted for review.

## Context

SourceOS needs a shared contract layer for runtime capability state, browser assistance sessions, terminal workspace classification, session-event recovery, and runtime installation provenance.

The motivating design issue is cross-plane drift: configuration, UI, runtime, server, plugin, policy, schema, and transport planes can disagree about whether a capability is available or effective. Without typed evidence records, downstream components can only infer state from logs.

## Decision

Add an additive runtime observability contract family:

| Schema | Purpose |
|---|---|
| `CapabilityLedger` | Records effective capability state after cross-plane reconciliation. |
| `BrowserAutomationReceipt` | Records visible, owned, scoped, policy-governed browser assistance sessions. |
| `GitWorkspaceState` | Records typed Git/workspace classification before passive or requested Git operations. |
| `OrphanEventReceipt` | Records recovery or quarantine for lifecycle events without immediate session attachment. |
| `RuntimeInstallReceipt` | Records runtime manifest resolution, artifact verification, install lifecycle state, and compact log mode. |

These contracts complement existing `SessionReceipt`, `AgentMachineReceipt`, `PolicyDecision`, `TelemetryEvent`, release, and provenance records.

## Design constraints

1. Effective capability state must be reconciled, not locally asserted.
2. Browser assistance sessions must have visible ownership and revocation state.
3. Terminal Git discovery must classify expected negative states without misleading warning noise.
4. Lifecycle events without immediate session attachment must enter a typed recovery or quarantine path.
5. Runtime installation must record manifest and artifact evidence while keeping ordinary logs compact.
6. Examples must carry evidence references, policy-decision references, stable URN prefixes, and parseable timestamps.

## Validation

The repository adds `tools/validate_runtime_observability_examples.py` and wires it into `make validate` through `validate-runtime-observability-examples`.

The validator checks schema conformance plus evidence-discipline invariants:

- unique example IDs
- required URN prefixes
- non-empty `evidenceRefs`
- required `policyDecisionRef`
- timestamp parseability
- no raw path storage in `GitWorkspaceState`
- browser-session timestamp ordering
- orphan-event recovery/quarantine consistency
- compact runtime-install log mode in the canonical example

## Downstream ownership

| Downstream repo | Contract responsibility |
|---|---|
| `SourceOS-Linux/sourceos-shell` | Emit and surface `CapabilityLedger` entries. |
| `SourceOS-Linux/BearBrowser` | Emit `BrowserAutomationReceipt` entries and expose visible session controls. |
| `SourceOS-Linux/agent-term` | Emit `GitWorkspaceState` entries and enforce severity discipline. |
| `SocioProphet/sociosphere` | Emit `OrphanEventReceipt` entries and implement event recovery/quarantine. |
| Agent Machine / runtime installer lane | Emit `RuntimeInstallReceipt` entries. |

## Consequences

Positive:

- Makes capability drift detectable and reviewable.
- Gives downstream repos concrete schema targets.
- Improves log quality by using compact receipt references.
- Provides a path for cross-repo validation before downstream runtime implementation.

Costs:

- Adds five new schemas and examples.
- Requires downstream emitters and validators to adopt the contract family.
- Requires future schema evolution discipline as implementations mature.

## Related issues

- Parent spec: `SourceOS-Linux/sourceos-spec#99`
- Browser implementation: `SourceOS-Linux/BearBrowser#25`
- Terminal implementation: `SourceOS-Linux/agent-term#39`
- Shell implementation: `SourceOS-Linux/sourceos-shell#12`
- Sociosphere implementation: `SocioProphet/sociosphere#283`
