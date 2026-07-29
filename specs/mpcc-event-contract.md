# MPCC Event Contract v0.1 — conversation + trading event family

Status: v0.1.0 (normative for the schemas listed below)
Provenance: SocioProphet/profit-mpcc, hardened to the policy-integrity tranche-0001 strictness bar.
Validation: `make validate-mpcc-event-examples` (tools/validate_mpcc_event_examples.py).

## 1. Scope

This contract lands the MPCC (multi-party conversation control) event fabric as
SourceOS typed contracts:

| Schema | Source in profit-mpcc |
|--------|----------------------|
| `ConversationEvent` | `schemas/event.schema.json` + `docs/canonical-event-schema.md` |
| `EffectRequest` | `schemas/effect-request.schema.json` + tranche-0001 `effect.schema.snapshot.json` |
| `EffectDecision` | `schemas/approval-event.schema.json` + tranche-0001 `decision.schema.snapshot.json` |
| `EffectRecord` | `schemas/effect-record.schema.json` + tranche-0001 `effect.schema.snapshot.json` |
| `NullAbsenceRecord` | `schemas/null-absence.schema.json` + `docs/null-absence-taxonomy.md` |
| `MarketDataEvent` | `schemas/market-data-event.schema.json` |
| `OrderIntent` | `schemas/order-intent-event.schema.json` |
| `ExecutionReport` | `schemas/execution-report-event.schema.json` |
| `PositionChange` | `schemas/position-change-event.schema.json` |
| `ReconciliationRecord` | `schemas/reconciliation-event.schema.json` |

The profit-mpcc drafts were deliberately loose (`additionalProperties: true`,
untyped sub-objects, free version strings). This landing hardens every schema to
the bar set by profit-mpcc's own strictest export, the policy-integrity
tranche-0001 snapshots:

- `"additionalProperties": false` on every object;
- `specVersion` pinned to the const `0.1.0` (per-family contract version, in the
  style of the in-repo `*.v1.1.json` control-plane contracts);
- anchored `urn:srcos:` id patterns per type;
- mandatory `idempotencyKey` on every side-effecting stage;
- required fields limited to those required by the source drafts, the tranche
  snapshots, or a stated invariant.

## 2. One envelope, not two

**Decision: the trading events are structural profiles of the ConversationEvent
envelope, with parity machine-enforced.**

`ConversationEvent` defines the single MPCC envelope vocabulary — `specVersion`,
`actorRef`, `workspaceRef`, `branchRef`, `visibilityScope`, `wallTime`,
`logicalTime`, `causalParents`, `traceContext`, `provenanceLinks`,
`policyLabels`, `riskLabels` (plus the shared `authorityContext` block). Every
trading schema carries these properties with byte-identical sub-schemas;
`tools/validate_mpcc_event_examples.py` fails the build if any profile drifts.
Required-ness may vary per family (e.g. `actorRef` is required on
`ConversationEvent` and `OrderIntent` but optional on venue-originated
`MarketDataEvent`); the vocabulary may not.

Why structural profiles rather than `allOf` composition: this repo requires
`"additionalProperties": false` on every object (CONTRIBUTING.md), which is
incompatible with `allOf`-based envelope reuse in draft 2020-12 unless every
profile switches to `unevaluatedProperties` — a construct used nowhere in the
v2 family. Self-contained strict files match both the house style and the
tranche-0001 snapshots; the parity check makes "one envelope" an enforced
invariant instead of a copy-paste hope.

Relation to the existing `EventEnvelope`: no competition. `EventEnvelope` is
the AsyncAPI **wire wrapper**; MPCC events are **domain objects** that ride in
its `payload`. Cross-family causality uses `causalParents` (any
`urn:srcos:` event URN), so market data can cause intents, intents cause
reports, and so on, without a second envelope vocabulary.

## 3. Effect lifecycle invariants (normative)

`EffectRequest` (proposal) → `EffectDecision` (authority) → `EffectRecord`
(execution reality) → compensation (appended history):

1. A requested effect is a proposal only — not permission, not execution, not
   evidence that anything happened.
2. `approvedEffects` must be a subset of `requestedEffects` modulo explicit
   policy rewriting; the decision carries the **exact** approved effect shape
   (`approvedEffect`), which may be a policy-narrowed rewrite of the request.
3. Every `EffectRecord` must ground its authority in an explicit
   `effectDecisionRef` or a first-class `autonomousPolicyRef` — enforced
   structurally by `anyOf`. No record may claim execution beyond delegated
   authority.
4. Denial, deferral, expiration, and revocation are distinct decision states and
   must never be conflated.
5. Every side-effecting path is idempotent under `idempotencyKey`; the record's
   key must equal its request's key (validator-enforced across the examples).
6. Compensation appends history (`compensationRefs`); it never erases the
   original effect record.
7. `causalParents` must never point forward in logical time.

## 4. Null / absence taxonomy

`NullAbsenceRecord` types twelve materially different kinds of "nothing"
(`no_event_observed` … `explicit_noop`) so merge logic, provenance, policy, and
effect handling never conflate them. Working invariants: `no_event_observed` is
not `empty_payload`; `transport_failure` is not `intentional_silence`;
`refusal` is not `abstention`. The taxonomy is closed at v0.1 (enum-enforced);
widening it is a minor contract bump.

## 5. Overlap decisions (spec-first conformance)

| Existing contract | Decision |
|-------------------|----------|
| `EventEnvelope` | Kept as the wire wrapper; MPCC events are payload-plane domain objects (§2). |
| `SourceOSInteractionEvent` | Surface/interaction telemetry stays there; `ConversationEvent` is the durable fabric record and bridges by reference via `interactionEventRefs`. |
| `PolicyDecision` | Not duplicated; `EffectDecision.policyDecisionRefs` references it as the policy-evaluation basis. |
| `ExecutionDecision` | Not duplicated; `EffectDecision.executionDecisionRef` references it when an agent-session gate participated. |
| `runtime-effect-decision.v1.1` | Distinct concern (control-plane event-pipeline dispatch); untouched. |
| `SettlementEvent` | Distinct concern (FogCompute usage-receipt settlement); `ReconciliationRecord` covers post-trade reconciliation including `settlement-window` scope. |
| `Topic` | `ConversationEvent.topics` may carry `urn:srcos:topic:` URNs where the fog-layer Topic applies. |

## 6. Versioning

The family versions as one contract, pinned by the `specVersion` const `0.1.0`.
Additive optional fields or widened enums bump the minor; anything that can
invalidate an existing document bumps the major, with CHANGELOG + ADR per
CONTRIBUTING.md.

## 7. Known gaps (deliberate, v0.1)

- No OpenAPI/AsyncAPI operations or semantic-context mappings yet (matches how
  recent contract families landed; wiring follows once names have settled).
- `claims` / `entities` are free-form stable references; typed claim/entity
  contracts are future work.
- `workspaceRef` / `branchRef` are free-form pending adoption of the
  profit-mpcc branch-id contract.
- The signal-event and approval-event trading families beyond the effect
  lifecycle (docs/trading-event-families.md §2, §4) are not yet landed.
