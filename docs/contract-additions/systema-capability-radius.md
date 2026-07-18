# Systema: Capability Radius Mapping to SourceOS Typed Contracts

## What Systema defines

Systema's `capability_radius_profile.yaml` models the bounded scope within which an agent or component may exercise capabilities: a spatial/contextual radius beyond which capability requests are automatically denied, regardless of individual capability grants.

## Existing SourceOS/SociOS coverage

| Systema concept | SourceOS/SociOS schema | Key fields |
|---|---|---|
| Agent capability scope bound | `AgentCapabilityLease` | `scopedCapabilities`, `contextConstraints`, `expiresAt` |
| Session-scoped capability | `AgentSession` | `grantRefs`, `scopeRef` |
| Component-level radius | `CapabilityContract` | `declaredCapabilities[].fallback` |
| Runtime enforcement | `CapabilityGrantState` | `capabilityStates[].decision` |
| Policy-governed radius | `ExecutionDecision` | `verdict`, `policyRef`, `scopeRef` |
| Radius violation evidence | `LocalReasoningFailure.failureClass: policy-inference-bypass` | suppresses out-of-radius mutation |

## Gap: radius boundary document

Systema's radius profile is a named, versioned, reusable boundary document. The closest match is `CapabilityPolicy`, which governs a set of grant rules. A Systema radius profile maps directly to a `CapabilityPolicy` with a `radiusScope` annotation — no new schema required.

## Mapping rules

1. Systema `capability_radius.scope` → `AgentCapabilityLease.contextConstraints` (agent) or `CapabilityContract.declaredCapabilities` (component).
2. Systema radius violation → `CapabilityGrantState.capabilityStates[].decision: denied` + `policyRuleRef` pointing to the radius policy + emit `LocalReasoningFailure.failureClass: policy-inference-bypass` with `suppressMutation: true`.
3. Systema radius expiry → `AgentCapabilityLease.expiresAt`; post-expiry attempts → `CapabilityGrantState.decision: unavailable`.
4. Cross-device radius extension → requires new `AgentCapabilityLease` with `grantRefs` from the target device's policy fabric; no ambient inheritance.

## No new schemas required

Systema capability-radius semantics are fully covered by `AgentCapabilityLease`, `CapabilityContract`, `CapabilityGrantState`, `CapabilityPolicy`, `ExecutionDecision`, and `LocalReasoningFailure`.
