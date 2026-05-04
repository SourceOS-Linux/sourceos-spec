# Agent Machine and Model Carry Contract Additions — May 2026

Status: Draft additive contract family

## Purpose

This contract addition projects the Prophet Intelligence Foundry runtime path into SourceOS/SociOS typed contracts. It gives `SourceOS-Linux/agent-machine`, `SourceOS-Linux/sourceos-model-carry`, `SocioProphet/model-router`, `SocioProphet/agentplane`, and `SocioProphet/policy-fabric` a common schema vocabulary for local model references, inference provider capability, model residency, placement facts, and runtime receipts.

## Added schemas

| Schema | Purpose | URN prefix |
| --- | --- | --- |
| `SourceOSModelCarryRef` | Approved on-device reference to a governed model or model-service profile carried by SourceOS without embedding mutable model state. | `urn:srcos:model-carry-ref:` |
| `InferenceProvider` | Backend-neutral local, clustered, or governed remote inference provider description. | `urn:srcos:inference-provider:` |
| `ModelResidency` | Point-in-time evidence that a governed model reference is unavailable, cached, loaded, warm, pinned, evictable, or failed on an Agent Machine. | `urn:srcos:model-residency:` |
| `PlacementFact` | Machine-local scheduling and policy fact for model, agent, cache, isolation, and runtime placement decisions. | `urn:srcos:placement-fact:` |
| `AgentMachineReceipt` | Runtime evidence emitted by Agent Machine after probing, placement, execution, cache reuse, model load/unload, or policy-mediated side-effect handling. | `urn:srcos:agent-machine-receipt:` |

## Boundary rules

1. `SourceOSModelCarryRef` is reference-only governance metadata. It must not embed mutable model weights or adapters into SourceOS images.
2. `InferenceProvider` describes serving capability. It must not authorize use by itself.
3. `ModelResidency` is observed state. It is not a release decision and not a routing policy.
4. `PlacementFact` informs scheduling and policy. It must not replace PolicyDecision, CapabilityToken, or AgentPlane run evidence.
5. `AgentMachineReceipt` proves runtime events. It must not replace AgentPlane RunCapsule, model-governance-ledger release evidence, or Sociosphere workspace state.

## Integration path

```text
functional-model-surfaces
→ model-governance-ledger
→ model-router
→ sourceos-model-carry
→ agent-machine
→ agentplane
→ sociosphere / SourceOS operator surfaces
```

## Validation posture

Each schema has a conforming lowercase example under `examples/`. The examples are intentionally narrow and represent an M2 Asahi/local llama.cpp-style path without requiring a real model download, model execution, network call, or runtime mutation.

## Non-goals

- No model weights.
- No training data.
- No runtime implementation.
- No new boot behavior.
- No authorization grant beyond existing `PolicyDecision` and `CapabilityToken` concepts.
- No replacement for AgentPlane run capsules or model-governance-ledger release decisions.
