# Systema: Membrane Boundary Mapping to SourceOS Typed Contracts

## What Systema defines

Systema's `membrane_boundary_profile.yaml` defines isolation boundaries between system zones: what may cross a membrane (data, events, capability grants), under what conditions, and what evidence is required to authorize a crossing.

## Existing SourceOS/SociOS coverage

| Systema concept | SourceOS/SociOS schema | Key fields |
|---|---|---|
| Capability crossing authorization | `CapabilityContract` + `CapabilityGrantState` | `declaredCapabilities`, `decision`, `grantSource` |
| Policy-governed event admission | `ExecutionDecision` | `policyRef`, `verdict`, `rationale` |
| Component isolation boundary | `CapabilityContract.minimumBootPhase` | phase-gating before crossing |
| Sandboxed child process limits | `CapabilityGrantState.capabilityStates[].grantSource: broker` | broker-mediated crossing |
| Cross-device sync admission | `SyncConflictRecord` + `SyncCycleReceipt` | governed crossing record |
| Agent capability radius | `AgentCapabilityLease` | `scopedCapabilities`, `expiresAt`, `revokedAt` |

## Gap: membrane crossing event record

Systema's membrane boundary profile can emit a crossing event with a before/after zone label that has no direct match in current schemas. Additive resolution: `SourceChannelEnvelope.channelPolicy` already captures routing authorization; a `membraneCrossingRef` annotation on `EventEnvelope` (optional string) can link to the governing `CapabilityGrantState` or `ExecutionDecision` without a new schema.

## Mapping rules

1. Systema membrane `denied` crossing → `CapabilityGrantState.capabilityStates[].decision: denied` + emit `DiagnosticStormRecord` if repeated.
2. Systema membrane `admitted` crossing → `CapabilityGrantState.capabilityStates[].decision: granted`, reference `ExecutionDecision` as policyRuleRef.
3. Agent membrane crossings → `AgentCapabilityLease` governs; Systema capability-radius is the outer bound.
4. Boot-phase membrane → `CapabilityContract.minimumBootPhase` enforced by `BootSessionPhaseState`.

## No new schemas required

All membrane boundary semantics are expressible through `CapabilityContract`, `CapabilityGrantState`, `ExecutionDecision`, `AgentCapabilityLease`, `BootSessionPhaseState`, `SourceChannelEnvelope`, and `DiagnosticStormRecord`.
