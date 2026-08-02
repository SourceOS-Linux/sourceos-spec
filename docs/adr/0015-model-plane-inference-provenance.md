# ADR-0015: Model Plane inference-provenance schemas (Tranche 7)

**Date:** 2026-08-02  
**Status:** `Proposed`

---

## Context

The SourceOS Model Plane spec (SP-SESSION-DOSSIER-20260609, "Tiered On-Device Intelligence with Governed Distillation") introduces Tranche 7 and calls for six sourceos-spec artifacts (T7-1..T7-6): `InferenceReceipt`, `ModelManifest`, `AdapterManifest`, `EscalationDecision`, `AdapterPromotionDecision`, and the addition of an `inference_provider` value to `AgentPassport.agent_class`.

The spec was drafted 2026-06-09 as pre-implementation. Since then the estate has landed an **Agent Machine / Model Carry** family that already covers a substantial part of the intended surface:

- `InferenceProvider` — inference providers modelled as a **separate typed object** (providerClass, endpointMode, executionProfile, `trustPosture`, `supportedModalities`, `requiresNetwork`), *not* as an `AgentPassport` class.
- `ModelResidency` — the spec's `ModelResidencyEvent` (residency state, cache tier, quantization).
- `SourceOSModelCarryRef` — the governed model/adapter reference (`carryPolicy`, `cachePolicy`, `mutableModelState: false`, router/governance refs).
- `ExternalModelProviderProfile` — the T4 external-frontier egress-governance surface (`promptEgressDefault`, `allowTrainingUse`, `promptHashOnly`).
- `AdapterDescriptor` — a **connector/actuation** adapter (api/cli/sdk/event/file), a different sense of "adapter" than a LoRA model adapter.

Authoring the T7 schemas naïvely would fork these canonical types. This ADR records what was added, what was reused, and what was deliberately deferred.

## Decision

Add three new schemas that sit **atop** the existing Model Carry family and reference it rather than restate it:

1. `InferenceReceipt` (T7-1) — the per-completion provenance primitive. References `InferenceProvider`, `ModelResidency`, `SourceOSModelCarryRef`. SEAM-015 teeth: any off-device (`sovereign_cluster`/`external_permitted`) receipt is schema-required to carry an authorizing `capabilityLeaseRef` and a non-empty `escalationChain`; an `on_device_only` receipt cannot have been escalated.
2. `EscalationDecision` (T7-3) — the governed tier / data-residency boundary crossing. SEAM-015 teeth: `verdict: permitted` is schema-impossible without a `capabilityLeaseRef` **and** `sensitivityCheck.result: pass`; a T4 crossing must name an `ExternalModelProviderProfile`; a refusal must state a `refusalReason` (including `prompt-unanswered`, the fail-closed resolution for non-interactive workloads).
3. `AdapterPromotionDecision` (T7-4) — governed LoRA-adapter promotion. SEAM-016/017 teeth: `verdict: promoted` is schema-impossible without `signatureVerified: true`, `allEventsConsented: true`, a named `promotedBy`, all `evalGates` passing (including `adversarialProbePassed`), and it always requires a `rollbackTargetDigest`.

Grant references use the existing `urn:srcos:lease:` (AgentCapabilityLease) prefix, not the spec's illustrative `urn:srcos:grant:`, which does not exist in the estate.

All three carry an optional `ledgerPrevHash` (append-only-ledger hash-chaining) and the receipt carries an optional `confidenceMethod`, both introduced from the design review as low-risk additive hardening.

**Deferred, pending decision (tracked as issues, not authored here):**

- **T7-2 `ModelManifest` / `AdapterManifest`** — a content-addressed store manifest overlaps `SourceOSModelCarryRef`, and "AdapterManifest" collides in name with `AdapterDescriptor`. Needs a decision on whether these are new types or extensions of the carry-ref, and a disambiguated name (e.g. `ModelAdapterManifest`).
- **T7-5 add `inference_provider` to `AgentPassport.agent_class`** — the estate already models inference providers as the separate `InferenceProvider` object, which appears to be a deliberate choice that keeps the five-class host-process model intact. Adding a sixth class is a core-ontology change (it breaks `tools/validate_agent_passport_examples.py` `EXPECTED_CLASSES` and touches ADR-0014's five-class model). This is Michael's call, not a mechanical widening.

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Author all six T7 schemas verbatim from the spec | Would fork `SourceOSModelCarryRef` / `InferenceProvider` / `ModelResidency` and collide `AdapterManifest` with `AdapterDescriptor` — stranded duplicates. |
| Add `inference_provider` to `AgentPassport` now | The separate `InferenceProvider` object is an apparent deliberate resolution; a sixth host-process class is a core-ontology decision that deserves explicit sign-off. |
| Fold provenance into `AgentMachineReceipt` | `AgentMachineReceipt` records machine-runtime events (probe/placement/model-load); per-completion inference provenance with escalation chains and confidence is a distinct concern. |
| Mint a new `urn:srcos:grant:` prefix per the spec text | The estate's grant primitive is `AgentCapabilityLease` (`urn:srcos:lease:`); a new prefix would fork the capability model. |

## Consequences

- Positive: the three headline properties the Model Plane claims over Apple Intelligence — visible inference provenance, consent-gated escalation, enumerable/governed distillation — are now schema-enforced with `if/then` teeth verified to fire both ways, and reuse the existing Model Carry vocabulary.
- Positive: the schema-level gates encode the design-review findings (∅-grant ⇒ no crossing; signature ≠ safety, so eval gates are also required; fail-closed background escalation; ledger tamper-evidence and confidence-method as optional hardening).
- Negative / follow-up: schema `if/then` cannot express the cross-document invariants (served-count == receipt-count reconciliation; ledger hash-chain continuity; base-model-digest match between promotion and adapter manifest; biometric-never-crosses-the-socket). These are delegated to ontogenesis SHACL (T7-8) and workstation-contracts conformance (T7-19) and are called out there.
- Negative: `ModelManifest`/`AdapterManifest` and the `inference_provider` class remain open, so Tranche 7 is not complete with this change.

## References

- SourceOS Model Plane — Architecture Specification v0.1 (2026-06-09), §VII–§X, §XIV
- ADR-0014 — Agent System domain (the five-class `AgentPassport` model)
- Reused: `schemas/InferenceProvider.json`, `schemas/ModelResidency.json`, `schemas/SourceOSModelCarryRef.json`, `schemas/ExternalModelProviderProfile.json`, `schemas/AgentMachineReceipt.json`
- SEAM-011 (non-local ledger), SEAM-014..017 (Model Plane seam registry, source-os T7-20)
