# Agent Machine / Model Carry Schema Catalog

Status: additive catalog slice

This catalog records the SourceOS projection schemas added for the Prophet Intelligence Foundry runtime path. It is intentionally narrower than the global `schemas/README.md` catalog so that fast-moving schema additions can be reviewed independently before the full catalog is regenerated.

| File | Type | URN prefix | Plane |
| --- | --- | --- | --- |
| `SourceOSModelCarryRef.json` | `SourceOSModelCarryRef` | `urn:srcos:model-carry-ref:` | SourceOS model carry |
| `InferenceProvider.json` | `InferenceProvider` | `urn:srcos:inference-provider:` | Agent Machine runtime |
| `ModelResidency.json` | `ModelResidency` | `urn:srcos:model-residency:` | Agent Machine runtime evidence |
| `PlacementFact.json` | `PlacementFact` | `urn:srcos:placement-fact:` | Placement / scheduling facts |
| `AgentMachineReceipt.json` | `AgentMachineReceipt` | `urn:srcos:agent-machine-receipt:` | Runtime receipts / evidence |

## Cross-repo authority

| Object | Authoritative producer | Primary consumer |
| --- | --- | --- |
| `SourceOSModelCarryRef` | `SourceOS-Linux/sourceos-model-carry` | `SocioProphet/model-router`, `SourceOS-Linux/agent-machine` |
| `InferenceProvider` | `SourceOS-Linux/agent-machine` | `SocioProphet/model-router`, `SocioProphet/agentplane` |
| `ModelResidency` | `SourceOS-Linux/agent-machine` | `SocioProphet/model-router`, `SocioProphet/policy-fabric` |
| `PlacementFact` | `SourceOS-Linux/agent-machine` | `SocioProphet/agentplane`, `SocioProphet/policy-fabric` |
| `AgentMachineReceipt` | `SourceOS-Linux/agent-machine` | `SocioProphet/agentplane`, `SocioProphet/model-governance-ledger` |

## Boundary rule

These schemas do not authorize runtime execution by themselves. Authorization remains a PolicyDecision / CapabilityToken concern. Agent Machine emits facts and receipts; AgentPlane owns run lifecycle; model-router owns routing; sourceos-model-carry owns approved carry references; model-governance-ledger owns release and promotion evidence.
