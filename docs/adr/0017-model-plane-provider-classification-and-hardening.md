# ADR-0017: Model Plane provider classification + review-hardening (Tranche 7)

**Date:** 2026-08-02  
**Status:** `Accepted`

---

## Context

Two open items from ADR-0015 / the Model Plane design review:

1. **T7-5 / #243** — the spec (§VIII) proposed adding a sixth `AgentPassport.agent_class`, `inference_provider`. But the estate already models inference providers as the separate `InferenceProvider` object, and `AgentPassport`'s five-class model (ADR-0014) is enforced as *exactly five* by `tools/validate_agent_passport_examples.py`.
2. **Design-review findings** with a schema-expressible fix: the ledger is the trust anchor for every provenance claim but `ledgerSeq` alone did not bind entry N to N-1 (finding #4); and the biometric boundary was described but not enforced at the escalation contract (finding #7).

## Decision

**#243 — do NOT add a sixth `agent_class`.** A model-serving daemon (`inferenced`, `visiond`, `embeddingd`, `distilld`) is a host process classified by its `AgentPassport` (typically `system_core` for a platform daemon) **and** described operationally by an `InferenceProvider` record (trust posture, network requirement, modalities). The two compose. To make the composition concrete, add an optional `InferenceProvider.passportRef` (`urn:srcos:agent-passport:` URN) linking the operational provider to its host-process classification. This keeps the five-class model intact and honors the estate's deliberate separate-object modeling.

**Review-hardening (schema teeth, verified both ways):**
- **Ledger hash-chain (finding #4):** on `InferenceReceipt`, `EscalationDecision`, and `AdapterPromotionDecision`, any non-genesis entry (`ledgerSeq >= 1`) must carry a non-null `ledgerPrevHash`. `ledgerSeq: 0` (genesis) is exempt. The append-only ledger is now hash-chained, so an enumerated contribution list cannot be retroactively rewritten.
- **Biometric hard boundary (finding #7):** on `EscalationDecision`, if the T0 `sensitivityCheck.sensitiveCategories` contains `biometric`, the crossing is schema-forced to `verdict: refused` with `refusalReason: biometric-boundary`. A `permitted` crossing carrying a biometric category is now schema-invalid — face/speaker embeddings cannot cross a tier boundary under any grant.

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Add `inference_provider` as a 6th `agent_class` | Breaks the `EXPECTED_CLASSES` "exactly five" invariant + ADR-0014; duplicates governance already carried by `InferenceProvider` + Model Plane receipts/leases. |
| Leave provider↔passport link implicit | Then "compose, don't add a class" is unenforceable/untraceable; the optional `passportRef` makes it explicit without a breaking change. |
| Make `ledgerPrevHash` always required | Breaks a legitimate genesis (`seq: 0`) entry; `>= 1` is the correct condition. |
| Enforce biometric boundary only in SHACL/impl | The escalation contract is exactly where the crossing decision lives; a schema gate is the earliest, cheapest refusal. |

## Consequences

- Positive: #243 resolved without a core-ontology break; two review findings closed as contract-enforced teeth.
- Positive: `passportRef` gives ontogenesis/agent-machine a typed link from an operational provider to its host passport.
- Follow-up (non-schema findings, filed separately): confidence self-report/router-vs-confidence contradiction (spec §II/§VII text), served==receipt emission reconciliation (workstation-contracts T7-19), trust concentration in T0 and the boundary-crossing incentive gradient (spec/ADR discussion), and the cross-document `sensitiveCategories`-completeness guarantee (ontogenesis SHACL T7-8). Schema `if/then` cannot express these.

## References

- SourceOS Model Plane — Architecture Specification v0.1, §II, §VII, §VIII
- ADR-0014 (five-class AgentPassport), ADR-0015 (inference-provenance schemas)
- Issue #243 (this decision); epic #241
- Changed: `schemas/InferenceProvider.json` (+`passportRef`), `schemas/InferenceReceipt.json`, `schemas/EscalationDecision.json`, `schemas/AdapterPromotionDecision.json`
