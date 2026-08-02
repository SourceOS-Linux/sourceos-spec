# Schema Catalog

This directory contains all 64 JSON Schema (draft 2020-12) files that make up the SourceOS/SociOS Typed Contracts specification.
This directory contains the JSON Schema (draft 2020-12) files that make up the SourceOS/SociOS Typed Contracts specification.

---

## Recent additions — Model Plane Provenance v0.1 (Tranche 7)

The governed-inference provenance layer atop the existing Agent Machine / Model Carry family (`InferenceProvider`, `ModelResidency`, `SourceOSModelCarryRef`, `ExternalModelProviderProfile`, `AgentMachineReceipt`, all reused, not restated):

| File | Type | URN prefix |
|------|------|-----------|
| `InferenceReceipt.json` | InferenceReceipt | `urn:srcos:inference-receipt:` |
| `EscalationDecision.json` | EscalationDecision | `urn:srcos:escalation-decision:` |
| `AdapterPromotionDecision.json` | AdapterPromotionDecision | `urn:srcos:adapter-promotion-decision:` |
| `ModelManifest.json` | ModelManifest | `urn:srcos:model-manifest:` |
| `ModelAdapterManifest.json` | ModelAdapterManifest | `urn:srcos:model-adapter-manifest:` |

These types make on-device inference auditable in the ways Apple Intelligence's silent loop does not:
- **`InferenceReceipt`** — the provenance primitive emitted for every completion: tier, content-addressed base/adapter/tokenizer digests, serving daemon, the data-residency class served under, and the escalation chain. Ledger-bound (a local-only ledger is not permitted, SEAM-011). Off-device receipts (`sovereign_cluster`/`external_permitted`) are schema-required to carry an authorizing lease and a non-empty escalation chain — possession of the output is not authorization for the crossing (SEAM-015).
- **`EscalationDecision`** — the governed record of a tier / data-residency boundary crossing. Fail-closed by construction: a `permitted` verdict is schema-impossible without an authorizing capability lease **and** a passing T0 sensitivity check; ∅-grant or an unanswered background consent prompt (`refusalReason: prompt-unanswered`) resolves to refusal, never a silent downgrade (SEAM-015). **Biometric hard boundary:** a crossing whose T0 sensitivity check flags a `biometric` category is schema-forced to `refused`/`biometric-boundary` — face/speaker embeddings never cross a tier boundary under any grant.
- **`AdapterPromotionDecision`** — adapter promotion as a human-governed decision, never an automatic OS update. Enumerates every contributing `OverrideEvent` (the property Apple's loop lacks), and a `promoted` verdict is schema-impossible without a verified signature, per-event training consent, all eval gates passing (including an adversarial-poisoning probe), a named human promoter, and a mandatory rollback target (SEAM-016, SEAM-017). Governs *model* (LoRA) adapters — distinct from `AdapterDescriptor` (connector/actuation adapters).
- **`ModelManifest` / `ModelAdapterManifest`** (T7-2) — the content-addressed *store* manifests sitting beside the weights. Distinct from `SourceOSModelCarryRef` (a governance/carry *reference* that points AT a manifest digest). A valid manifest is schema-impossible without signature info (SEAM-014) and — for the adapter — the `baseModelDigest` it binds to (SEAM-017, rejected on mismatch); both require an SPDX `license` so the estate's MIT/Apache-only rule is checkable before wiring. The adapter manifest is named `ModelAdapterManifest`, not `AdapterManifest`, to avoid colliding with `AdapterDescriptor` (connector adapters).

All three provenance types hash-chain the append-only ledger: `ledgerPrevHash` is required for any non-genesis entry (`ledgerSeq >= 1`), so an enumerated contribution list cannot be retroactively rewritten; the receipt also carries an optional `confidenceMethod` (the escalation trigger is self-reported — recording the method makes it auditable). A model-serving daemon is not a new agent class — it is a `system_core` host process (its `AgentPassport`) plus an `InferenceProvider` record, linked via `InferenceProvider.passportRef` (ADR-0017).

Validation: `ajv validate -s schemas/<Type>.json -d examples/<type>.json`. Canonical examples: `examples/inference-receipt.json`, `examples/escalation-decision.json`, `examples/escalation-decision.refused-biometric.json`, `examples/adapter-promotion-decision.json`, `examples/model-manifest.json`, `examples/model-adapter-manifest.json`. ADRs: `docs/adr/0015-model-plane-inference-provenance.md`, `docs/adr/0016-model-plane-store-manifests.md`, `docs/adr/0017-model-plane-provider-classification-and-hardening.md`.

---

## Recent additions — DeviceService Contract v0.1 (the southbound device plane, W8.7)

The southbound device abstraction — the estate's first — adds the following top-level schemas:

| File | Type | URN prefix |
|------|------|-----------|
| `DeviceProfile.json` | DeviceProfile | `urn:srcos:device-profile:` |
| `DeviceReading.json` | DeviceReading | `urn:srcos:device-reading:` |

These types support:
- **ONE southbound interface, N protocol drivers** (EdgeX Foundry's lesson): a driver speaks a protocol, it does not invent a vocabulary. `DeviceProfile` declares what a device IS — protocol, protocol binding, and the exact readings it produces with units, value types, operating ranges and protocol-native source addresses; `DeviceReading` is one observation against that declaration
- **the invariant the family exists for — a reading is ATTRIBUTABLE OR IT IS NOTHING.** `deviceRef`, `deviceProfileRef`, `profileDigest`, `metric`, `sourceAddress` and `unit` are all required, so every value resolves to the physical thing that produced it, the exact declared-capability revision it was admitted against, and the protocol-native channel it came off. The validator resolves all of them across the example set and additionally requires `provenanceLinks` to name the device and profile independently, so the attribution survives being read without the validator
- **digest-pinning against retroactive legalisation**: `DeviceProfile.definitionDigest` is recomputed by the validator from the profile's own `{deviceClass, protocol, metrics}` projection, and every reading pins it. Widening a range after the fact produces a new digest and orphans the readings it was meant to legalise instead of silently admitting them (the `UpdateHealthProbe` digest-pinned-gate construct, applied to metrology)
- **a closed quality vocabulary with typed absence**: `ok` / `degraded` / `stale` / `substituted` / `unavailable`, where `unavailable` is schema-bound to a null value plus a `NullAbsenceRecord` reference — the device plane reuses the existing 12-kind MPCC absence taxonomy rather than inventing a device-local one. Normative: `stale` and `substituted` are not `ok`, and `substituted` is not measured
- **simulated devices as a first-class, visibly-labelled member of the protocol taxonomy** (`protocol: "virtual"` ⇒ the `synthetic:simulated-device` label, enforced in both directions) — the `model-generated` admissibility rule applied to sensors
- `observedAt` → `receivedAt` → `wallTime` kept distinct, because `observedAt` → `receivedAt` is the southbound latency a twin's sync budget is actually spent on
- ontology typing at the granularity the estate can resolve: `kkoTypeRef` cites the vendored KKO upper ontology (169 verified terms), not the unvendored ~58k KBpedia reference-concept layer — a more specific-looking URI that resolves to nothing is the same silent-wrong in different clothing
- read-only at v0.1 (`access` closed to `"read"`): commanding a device is a world-changing effect and must travel the MPCC `EffectRequest` → `EffectDecision` lifecycle, not a widened enum

Distinct from `DeviceIdentity` (admission/attestation/trust for a SourceOS operator workstation — no metrology) and `TelemetryEvent` (an `AgentSession` diagnostic log event — no unit, range, quality or device); `DeviceProfile.identityRef` binds to the former rather than competing with it.

Validation: `make validate-device-service-examples` (schema conformance, tranche strictness bar, envelope parity against `ConversationEvent`, recomputed profile digests, cross-document attribution soundness, simulated-visibility, and twenty-one negative vectors under `fixtures/device-service/`). Normative notes: `specs/device-service-contract.md`. Reference implementation: `device-service` in `SocioProphet/prophet-platform` (`apps/device-service`).

---

## Recent additions — A/B Fallback Update Contract v0.1

The dual-slot update contract adds the following top-level schemas:

| File | Type | URN prefix |
|------|------|-----------|
| `UpdateSlot.json` | UpdateSlot | `urn:srcos:update-slot:` |
| `UpdateTransaction.json` | UpdateTransaction | `urn:srcos:update-transaction:` |
| `UpdateHealthProbe.json` | UpdateHealthProbe | `urn:srcos:update-health-probe:` |

These types support:
- the A/B slot model the estate had nowhere: two slots carrying the GPT attribute triple (`bootPriority`, `triesRemaining`, `successful`) that a priority-boot selector reads, with `role` (active/candidate) and `currentlyRunning` deliberately separate so the fallback slot stays describable during a trial boot
- **the invariant the family exists for — the currently-good slot is never overwritten by the update being applied.** Enforced by schema within a document (`UpdateTransaction`'s `not`/`anyOf` over the two illegal `(fromSlot, toSlot)` pairs; `UpdateSlot`'s `state: writing` ⇒ `role: candidate`), by schema on the settle path (`settledOnSlot` pinned to `fromSlot` on rollback/refusal), and across documents by the validator (`preservedPayloadDigest` still equals the active slot's `payloadDigest`)
- automatic rollback with a bounded attempt budget: `triesRemaining` is decremented by the bootloader *before* control transfers, so a payload that hangs before userspace still consumes an attempt; `refused` is terminal and is what ends the boot loop
- a digest-pinned promotion gate: `UpdateHealthProbe.definitionDigest` is recomputed by the validator from the probe's own check set, so a failing candidate cannot be promoted by weakening the gate it failed. Normative: promotion is evaluated in post-boot userspace only, an inconclusive probe is a `fail`, and a hardware+software watchdog pair is mandatory (two `contains` clauses) — software cannot fire through a wedged kernel, hardware cannot tell working from merely running

Validation: `make validate-ab-update-examples` (schema conformance, tranche strictness bar, recomputed probe digest, cross-document invariants, and fourteen negative vectors under `fixtures/ab-update/`). Normative notes: `specs/ab-fallback-update-contract.md`. Reference implementation: `AbUpdateMachine` in `sourceos-boot`.

---

## Recent additions — Knowledge Nugget + Semantic Action registry v0.1

The L2 content-grain and typed-action-registry contracts add the following top-level schemas:

| File | Type | URN prefix |
|------|------|-----------|
| `KnowledgeNugget.json` | KnowledgeNugget | `urn:srcos:knowledge-nugget:` |
| `SemanticAction.json` | SemanticAction | `urn:srcos:semantic-action:` |

These types support:
- the estate's L2 content grain: warrant-typed knowledge fragments (`direct-quote` / `computed` / `inferred` / `model-generated`) with content-addressed source spans (`sha256-` pinned), evidence refs, confidence, ontology type refs, and provenance chain links — generalizing the production IFM warrant-typed extraction. Normative: `model-generated` MUST stay visibly distinguishable downstream (admissibility discounting); `computed`/`inferred` must cite evidence (schema-enforced)
- the declarative typed-action registry for the NL→plan compiler: ontology-typed inputs/output, `subClassOf`/`instanceOf`/`sameAs` constraints (polymorphism via subsumption), executor binding, and a two-value effect posture (`none` | `effect-request`) — actions are side-effect-free at plan-search time, and world-changing execution defers to the MPCC `EffectRequest` → `EffectDecision` lifecycle (no direct-mutation vocabulary exists)
- `KnowledgeNugget.wallTime`/`logicalTime` carried verbatim from the `ConversationEvent` envelope, and `SemanticAction` slot types sharing the `kkoTypeRefs` URI vocabulary, so content grains bind directly as typed planner values

Validation: `make validate-knowledge-nugget-examples` and `make validate-semantic-action-examples` (envelope parity, warrant soundness, binding/purity invariants, and negative vectors under `fixtures/knowledge-nugget/` and `fixtures/semantic-action/`). Normative notes: `specs/knowledge-nugget-contract.md`, `specs/semantic-action-contract.md`.

---

## Recent additions — MPCC Event Contract v0.1 (conversation + trading event family)

The MPCC (multi-party conversation control) event contract adds the following top-level schemas:

| File | Type | URN prefix |
|------|------|-----------|
| `ConversationEvent.json` | ConversationEvent | `urn:srcos:conversation-event:` |
| `EffectRequest.json` | EffectRequest | `urn:srcos:effect:` |
| `EffectDecision.json` | EffectDecision | `urn:srcos:effect-decision:` |
| `EffectRecord.json` | EffectRecord | `urn:srcos:effect-record:` |
| `NullAbsenceRecord.json` | NullAbsenceRecord | `urn:srcos:null-absence:` |
| `MarketDataEvent.json` | MarketDataEvent | `urn:srcos:market-data-event:` |
| `OrderIntent.json` | OrderIntent | `urn:srcos:order-intent:` |
| `ExecutionReport.json` | ExecutionReport | `urn:srcos:execution-report:` |
| `PositionChange.json` | PositionChange | `urn:srcos:position-change:` |
| `ReconciliationRecord.json` | ReconciliationRecord | `urn:srcos:reconciliation-record:` |

These types support:
- the canonical 26-field conversation-fabric event (causal parents, authority context with delegation chain, visibility scope, requested/approved/actual effect references, modality, speech act)
- the requested → approved → actual → compensated effect lifecycle with idempotency keys (`EffectRequest` → `EffectDecision` → `EffectRecord`)
- a 12-kind null/absence taxonomy so distinct kinds of "nothing" are never conflated
- the real-time trading families (market data, order intent, execution report, position change, reconciliation) as profiles of the ConversationEvent envelope — one shared envelope vocabulary, with parity enforced by `tools/validate_mpcc_event_examples.py` (`make validate-mpcc-event-examples`)

Provenance: imported from SocioProphet/profit-mpcc (`schemas/*.schema.json`, `docs/canonical-event-schema.md`, `docs/effect-approval-semantics.md`, `docs/null-absence-taxonomy.md`, `docs/trading-event-families.md`) and hardened to the policy-integrity tranche-0001 strictness bar (`additionalProperties: false`, pinned `specVersion` const, anchored URN id patterns, mandatory idempotency keys). These are domain objects: on AsyncAPI channels they ride inside `EventEnvelope` rather than replacing it, and they reference `PolicyDecision` / `ExecutionDecision` / `SourceOSInteractionEvent` instead of duplicating them.

---

## Recent additions — SourceOS Interaction Substrate

The SourceOS interaction substrate adds the following top-level schema:

| File | Type | URN prefix |
|------|------|-----------|
| `SourceOSInteractionEvent.json` | SourceOSInteractionEvent | `urn:srcos:interaction-event:` |

This type supports governed noetic/chat/task lifecycle events shared by Noetica, AgentTerm, Matrix-facing operator flows, Superconscious task boundaries, AgentPlane evidence references, Memory Mesh context-pack handoffs, Agent Registry grant references, and Policy Fabric decisions.

---

## Recent additions — Release and build lifecycle

The release/build lifecycle slice adds the following top-level schemas:

| File | Type | URN prefix |
|------|------|-----------|
| `ReleaseSet.json` | ReleaseSet | `urn:srcos:release-set:` |
| `Fingerprint.json` | Fingerprint | `urn:srcos:fingerprint:` |
| `ConfigSource.json` | ConfigSource | `urn:srcos:config-source:` |
| `TokenDoor.json` | TokenDoor | `urn:srcos:token-door:` |
| `GitRefBuild.json` | GitRefBuild | `urn:srcos:git-ref-build:` |

These types support:
- canonical assignment of software + boot artifacts to target devices (`ReleaseSet`)
- point-in-time device state observation and compliance reporting (`Fingerprint`)
- typed configuration source references consumed by NLBoot and sourceos-boot (`ConfigSource`)
- token-gated access control gates for boot/provisioning phases (`TokenDoor`)
- build provenance records linking Git commits to release artifacts (`GitRefBuild`)

---

## Recent additions — Workstation Contract Family

The workstation contract family adds the following top-level schemas:

| File | Type | URN prefix |
|------|------|-----------|
| `LauncherAction.json` | LauncherAction | `urn:srcos:launcher-action:` |
| `LauncherProvider.json` | LauncherProvider | `urn:srcos:launcher-provider:` |
| `PackageManifest.json` | PackageManifest | `urn:srcos:package-manifest:` |
| `DesktopProfile.json` | DesktopProfile | `urn:srcos:desktop-profile:` |
| `WorkstationProfile.json` | WorkstationProfile | `urn:srcos:workstation-profile:` |

These types support:
- reproducible workstation profile descriptions
- typed launcher / command-bus surfaces
- layered package manifests for system, user, and toolbox lanes
- desktop posture capture for GNOME and adjacent shells
- alignment between Linux realization and the canonical contract layer

---

## Recent additions — Fog Layer

The FogVault / FogCompute contract family adds the following top-level schemas:

| File | Type | URN prefix |
|------|------|-----------|
| `ContentRef.json` | ContentRef | _(digest-based content reference)_ |
| `Offer.json` | Offer | `urn:srcos:offer:` |
| `ReplicationPolicy.json` | ReplicationPolicy | _(top-level policy object)_ |
| `SettlementEvent.json` | SettlementEvent | `urn:srcos:settlement:` |
| `Topic.json` | Topic | `urn:srcos:topic:` |
| `TopicEnvelope.json` | TopicEnvelope | `urn:srcos:topic-entry:` |
| `UsageReceipt.json` | UsageReceipt | `urn:srcos:receipt:usage:` |
| `WorkOrder.json` | WorkOrder | `urn:srcos:workorder:` |

These types support:
- append-only Merkle-log topics
- explicit replication/retention policy
- content-addressed storage references
- compute offers, work orders, receipts, and optional settlement mappings

---

## Quick reference

| File | Type | URN prefix |
|------|------|-----------|
| `AgentSession.json` | AgentSession | `urn:srcos:session:` |
| `Agreement.json` | Agreement | `urn:srcos:agreement:` |
| `AnnotationExport.json` | AnnotationExport | `urn:srcos:schema:AnnotationExport` |
| `ArtifactManifest.json` | ArtifactManifest | `urn:srcos:schema:ArtifactManifest` |
| `AppleSiliconAdapterEvidence.json` | AppleSiliconAdapterEvidence | `urn:srcos:as-adapter-evidence:` |
| `ArtifactCacheRecord.json` | ArtifactCacheRecord | `urn:srcos:artifact-cache:` |
| `AuthorityLink.json` | AuthorityLink | _(sub-object, no top-level id)_ |
| `BootProofRecord.json` | BootProofRecord | `urn:srcos:boot-proof:` |
| `CapabilityToken.json` | CapabilityToken | _(plain `tokenId` string)_ |
| `Comment.json` | Comment | `urn:srcos:comment:` |
| `CommentSignal.json` | CommentSignal | `urn:srcos:schema:CommentSignal` |
| `Community.json` | Community | `urn:srcos:community:` |
| `CompressionEvaluation.json` | CompressionEvaluation | `urn:srcos:compression-eval:` |
| `ConfigSource.json` | ConfigSource | `urn:srcos:config-source:` |
| `Connector.json` | Connector | `urn:srcos:connector:` |
| `ContentRef.json` | ContentRef | _(digest-based content reference)_ |
| `DataRef.json` | DataRef | _(sub-object, no top-level id)_ |
| `DataSphere.json` | DataSphere | `urn:srcos:sphere:` |
| `Dataset.json` | Dataset | `urn:srcos:dataset:` |
| `DeltaSurface.json` | DeltaSurface | `urn:srcos:delta-surface:` |
| `DesktopProfile.json` | DesktopProfile | `urn:srcos:desktop-profile:` |
| `EntityField.json` | EntityField | _(sub-object inside SchemaDefinition)_ |
| `EventEnvelope.json` | EventEnvelope | `urn:srcos:event:` |
| `Exception.json` | Exception | _(sub-object inside Policy)_ |
| `ExecutionDecision.json` | ExecutionDecision | `urn:srcos:exec-decision:` |
| `ExecutionSurface.json` | ExecutionSurface | _(sub-object inside AgentSession)_ |
| `ExperimentFlag.json` | ExperimentFlag | `urn:srcos:flag:` |
| `Field.json` | Field | `urn:srcos:field:` |
| `Fingerprint.json` | Fingerprint | `urn:srcos:fingerprint:` |
| `FrustrationSignal.json` | FrustrationSignal | `urn:srcos:frustration:` |
| `GitRefBuild.json` | GitRefBuild | `urn:srcos:git-ref-build:` |
| `GlossaryTerm.json` | GlossaryTerm | `urn:srcos:glossary:` |
| `LauncherAction.json` | LauncherAction | `urn:srcos:launcher-action:` |
| `LauncherProvider.json` | LauncherProvider | `urn:srcos:launcher-provider:` |
| `Link.json` | Link | _(sub-object, no id)_ |
| `MappingEvidence.json` | MappingEvidence | _(sub-object inside MappingSpec)_ |
| `MappingSpec.json` | MappingSpec | `urn:srcos:mapping:` |
| `MemoryEntry.json` | MemoryEntry | `urn:srcos:memory:` |
| `MirrorReceipt.json` | MirrorReceipt | `urn:srcos:schema:MirrorReceipt` |
| `NoetherDiagnostic.json` | NoetherDiagnostic | `urn:srcos:schema:NoetherDiagnostic` |
| `NLBootPlan.json` | NLBootPlan | `urn:srcos:nlboot-plan:` |
| `ObjectContext.json` | ObjectContext | _(sub-object, no id)_ |
| `ObjectSelector.json` | ObjectSelector | _(sub-object inside Policy scope)_ |
| `Obligation.json` | Obligation | _(sub-object, no id)_ |
| `Offer.json` | Offer | `urn:srcos:offer:` |
| `PackageManifest.json` | PackageManifest | `urn:srcos:package-manifest:` |
| `Party.json` | Party | `urn:srcos:party:` |
| `PdfValidationReport.json` | PdfValidationReport | `urn:srcos:schema:PdfValidationReport` |
| `PhysicalAsset.json` | PhysicalAsset | `urn:srcos:asset:` |
| `Policy.json` | Policy | `urn:srcos:policy:` |
| `PolicyBinding.json` | PolicyBinding | _(sub-object inside WorkflowSpec)_ |
| `PolicyCondition.json` | PolicyCondition | _(sub-object inside Rule)_ |
| `PolicyDecision.json` | PolicyDecision | `urn:srcos:decision:` |
| `ProfileStats.json` | ProfileStats | _(sub-object inside Field.quality)_ |
| `ProvenanceRecord.json` | ProvenanceRecord | `urn:srcos:prov:` |
| `PublishDecision.json` | PublishDecision | `urn:srcos:schema:PublishDecision` |
| `QualityMetric.json` | QualityMetric | _(sub-object inside Field.quality)_ |
| `Rating.json` | Rating | `urn:srcos:rating:` |
| `ReleaseManifest.json` | ReleaseManifest | `urn:srcos:release:` |
| `ReleaseReceipt.json` | ReleaseReceipt | `urn:srcos:release-receipt:` |
| `ReleaseSet.json` | ReleaseSet | `urn:srcos:release-set:` |
| `ReplicationPolicy.json` | ReplicationPolicy | _(top-level policy object)_ |
| `RolloutPolicy.json` | RolloutPolicy | `urn:srcos:rollout:` |
| `Rule.json` | Rule | _(sub-object inside Policy)_ |
| `RunRecord.json` | RunRecord | `urn:srcos:run:` |
| `RunReport.json` | RunReport | `urn:srcos:schema:RunReport` |
| `SchemaDefinition.json` | SchemaDefinition | `urn:srcos:schema:` |
| `SearchRouteDecision.json` | SearchRouteDecision | `urn:srcos:schema:SearchRouteDecision` |
| `SessionReceipt.json` | SessionReceipt | `urn:srcos:receipt:session:` |
| `SessionReview.json` | SessionReview | `urn:srcos:session-review:` |
| `SignedArtifact.json` | SignedArtifact | `urn:srcos:schema:SignedArtifact` |
| `SettlementEvent.json` | SettlementEvent | `urn:srcos:settlement:` |
| `SkillManifest.json` | SkillManifest | `urn:srcos:skill:` |
| `SourceOSInteractionEvent.json` | SourceOSInteractionEvent | `urn:srcos:interaction-event:` |
| `SubjectContext.json` | SubjectContext | _(sub-object, no id)_ |
| `SubjectSelector.json` | SubjectSelector | _(sub-object inside Policy scope)_ |
| `TagAssignment.json` | TagAssignment | _(sub-object inside Field/GlossaryTerm)_ |
| `TelemetryEvent.json` | TelemetryEvent | `urn:srcos:telemetry:` |
| `Topic.json` | Topic | `urn:srcos:topic:` |
| `TopicEnvelope.json` | TopicEnvelope | `urn:srcos:topic-entry:` |
| `TokenDoor.json` | TokenDoor | `urn:srcos:token-door:` |
| `Trigger.json` | Trigger | _(sub-object inside WorkflowSpec)_ |
| `TruthSurface.json` | TruthSurface | `urn:srcos:truth-surface:` |
| `UsageReceipt.json` | UsageReceipt | `urn:srcos:receipt:usage:` |
| `ValidValues.json` | ValidValues | _(sub-object inside EntityField)_ |
| `WorkflowEdge.json` | WorkflowEdge | _(sub-object inside WorkflowSpec)_ |
| `WorkflowNode.json` | WorkflowNode | _(sub-object inside WorkflowSpec)_ |
| `WorkflowSpec.json` | WorkflowSpec | `urn:srcos:workflow:` |
| `WorkloadSpec.json` | WorkloadSpec | `urn:srcos:workload:` |
| `WorkOrder.json` | WorkOrder | `urn:srcos:workorder:` |
| `WorkstationProfile.json` | WorkstationProfile | `urn:srcos:workstation-profile:` |

---

## Schema families

### Family 1 – Physical Assets

| Schema | Description |
|--------|-------------|
| `Connector` | A named, typed connection to a physical data store (S3, GCS, RDBMS, Kafka, …) |
| `PhysicalAsset` | A specific resource (table, bucket prefix, topic) reachable via a `Connector` |

### Family 2 – Glossary

| Schema | Description |
|--------|-------------|
| `GlossaryTerm` | A defined business term with synonyms, tags, and authority links |
| `AuthorityLink` | A pointer to an external controlled vocabulary entry (SNOMED, ISO, internal wiki) |

### Family 3 – Governance

| Schema | Description |
|--------|-------------|
| `Policy` | An access policy with subject/object/purpose scope, rules, obligations, and exceptions |
| `Rule` | A single `permit`/`deny` rule with an optional typed condition |
| `PolicyCondition` | A rule expression in `jsonlogic`, `cel`, `rego`, or `cedar` |
| `SubjectSelector` | A subject match clause in a Policy scope |
| `ObjectSelector` | An object match clause in a Policy scope |
| `PolicyDecision` | The immutable audit record of a `/v2/decisions/evaluate` call |
| `CapabilityToken` | A short-lived, signed access grant derived from a `PolicyDecision` |
| `Obligation` | A required action (`pre`/`post`/`runtime`) attached to a policy decision or token |
| `Exception` | A time-limited exemption from a Policy rule |
| `PolicyBinding` | Associates a Policy with a WorkflowSpec or SkillManifest |

### Family 4 – Collaboration

| Schema | Description |
|--------|-------------|
| `Comment` | A free-text annotation on any addressable object |
| `CommentSignal` | A reviewer or author signal payload exposing genuine/sarcasm/experience state |
| `Rating` | A 1–5 star rating on any addressable object |
| `Community` | A named group of subject URNs |

### Family 5 – Models / Schemas

| Schema | Description |
|--------|-------------|
| `SchemaDefinition` | A named, versioned logical schema composed of `EntityField`s |
| `EntityField` | A field descriptor inside a `SchemaDefinition` |
| `Field` | A fully annotated, quality-profiled field attached to a live `Dataset` |
| `TagAssignment` | A classification tag with confidence score, source provenance, and review record |
| `ValidValues` | Enumeration, numeric range, or regex constraint on a field |
| `QualityMetric` | A named quality dimension (completeness, validity, …) scored 0–1 |
| `ProfileStats` | Statistical profile of a column: row count, nulls, distinct values, top-N values |

### Family 6 – Agreements

| Schema | Description |
|--------|-------------|
| `Agreement` | A data-sharing agreement between one or more parties with terms and effective dates |
| `Party` | A named signatory (person, org, or service) with optional authority links |

### Workstation / Desktop

| Schema | Description |
|--------|-------------|
| `LauncherAction` | A typed launcher or command-bus action surfaced to workstation users/operators |
| `LauncherProvider` | A typed launcher or command-bus provider with routing scopes and invariants |
| `PackageManifest` | A layered workstation package manifest covering system, user, and toolbox layers |
| `DesktopProfile` | A typed desktop-environment posture including extensions, keybindings, and input/gesture lanes |
| `WorkstationProfile` | A top-level workstation profile tying package, desktop, launcher, and validation surfaces together |

### Execution / Provenance

| Schema | Description |
|--------|-------------|
| `Dataset` | A logical view of a `PhysicalAsset` with governance, schema, and lifecycle metadata |
| `DataRef` | A typed pointer to a dataset, asset, stream topic, or file |
| `DataSphere` | A bounded execution environment with zone, network, and storage controls |
| `WorkloadSpec` | A container, Spark job, function, or stream processor specification |
| `RunRecord` | The audit record of a single workload execution |
| `WorkflowSpec` | A DAG of `WorkflowNode`s connected by `WorkflowEdge`s |
| `WorkflowNode` | A single processing node in a `WorkflowSpec` |
| `WorkflowEdge` | A directed dependency edge between two `WorkflowNode` IDs |
| `Trigger` | How a workflow is activated: cron schedule, event, or manual |
| `ProvenanceRecord` | A W3C PROV-compatible record linking a run to its input/output entities |
| `CompressionEvaluation` | Artifact-versus-baseline evaluation record composed from content/data refs, estimator metrics, and governance/provenance references |
| `MappingSpec` | A field-to-field semantic mapping with multi-method confidence evidence |
| `MappingEvidence` | A single evidence item for a `MappingSpec` (label similarity, value overlap, …) |
| `EventEnvelope` | The universal wrapper for all AsyncAPI channel messages |
| `TruthSurface` | Signed truth summary emitted by a plane (system/user/agent/witness) |
| `DeltaSurface` | Signed diff between two TruthSurfaces with gate results |
| `SourceOSInteractionEvent` | Shared noetic/chat/task lifecycle event envelope for Noetica, AgentTerm, governance traces, task submission, and evidence handoff |
| `InferenceReceipt` | Model Plane (T7): per-completion provenance receipt — tier, model/adapter/tokenizer digests, residency class, escalation chain; ledger-bound (SEAM-011/015) |
| `EscalationDecision` | Model Plane (T7): governed tier/data-residency boundary crossing; fail-closed — `permitted` requires a lease and a passing T0 sensitivity check (SEAM-015) |
| `AdapterPromotionDecision` | Model Plane (T7): human-governed LoRA-adapter promotion; enumerates contributing override events; requires signature + consent + eval + rollback (SEAM-016/017) |

### Agent Plane

| Schema | Description |
|--------|-------------|
| `AgentSession` | A single autonomous agent session with role, mode, substrate, and execution surface |
| `ExecutionSurface` | Sandboxing, network, and filesystem constraints for an agent's environment |
| `ExecutionDecision` | An immutable record of an agent's allow/deny/ask/defer/rewrite decision |
| `SkillManifest` | A declared agent skill with activation rules, requirements, and policy bindings |
| `MemoryEntry` | A persistent agent memory of kind `rule`, `learned`, or `recap` |
| `SessionReceipt` | The final outcome record for a completed `AgentSession` |
| `SessionReview` | A post-session learning review linking to extracted memory entries |
| `TelemetryEvent` | A structured log event emitted during an agent session |
| `FrustrationSignal` | A behavioural signal indicating agent or user difficulty |

### Release / Experiments

| Schema | Description |
|--------|-------------|
| `ExperimentFlag` | A feature flag with lifecycle: off → shadow → internal → beta → on → retired |
| `RolloutPolicy` | Audience-based percentage rollout rules for an `ExperimentFlag` |
| `ReleaseReceipt` | A verified release record with artifact hashes and gate check results |

### Shell / Document / Publication

| Schema | Description |
|--------|-------------|
| `ArtifactManifest` | Canonical manifest for a derived shell/document artifact |
| `SignedArtifact` | Signature metadata associated with a signed artifact |
| `PdfValidationReport` | Validation report produced for a derived PDF artifact |
| `AnnotationExport` | Export bundle for PDF/HTML review annotations |
| `RunReport` | Publication-ready summary of a workflow or execution run |
| `NoetherDiagnostic` | Measured conservation or invariance reading for a declared model charge |
| `PublishDecision` | Publish-lane decision across knowledge/value/ecosystem openness |
| `MirrorReceipt` | Receipt showing artifact mirroring outcome for a downstream channel |
| `SearchRouteDecision` | Routing decision for scope-based shell search dispatch |
### Boot / NLBoot

| Schema | Description |
|--------|-------------|
| `NLBootPlan` | An NLBoot boot plan describing ordered stages, artifact refs, and verification policy for a device |
| `ArtifactCacheRecord` | A content-addressed cache entry for a locally-stored NLBoot artifact with origin, digest, and status |
| `BootProofRecord` | An immutable record proving boot integrity: plan ref, per-stage verdicts, and attestation evidence refs |
| `AppleSiliconAdapterEvidence` | Evidence from the Asahi-compatible Apple Silicon boot adapter: chip identity, security policy, and boot-chain hashes |

### Fog Layer

| Schema | Description |
|--------|-------------|
| `Topic` | An append-only topic contract for FogVault channels |
| `TopicEnvelope` | A typed append-only entry envelope for topic events and payloads |
| `ReplicationPolicy` | Replication, retention, and compaction policy for a fog topic |
| `ContentRef` | A content-addressed reference to blobs, chunks, or manifests |
| `Offer` | A FogCompute provider offer advertising resources and constraints |
| `WorkOrder` | A FogCompute request describing workload, inputs, outputs, and verification mode |
| `UsageReceipt` | A worker-emitted usage and output receipt for a completed work order |
| `SettlementEvent` | An optional settlement mapping from receipt to credits/tokens/backend |

---

## Validation

```bash
# Validate a single example against its schema
npx ajv-cli validate -s AgentSession.json -d ../examples/agentsession.json

# Validate all examples in bulk
for schema in *.json; do
  type=$(python3 -c "import json; d=json.load(open('$schema')); print(d.get('title',''))")
  example="../examples/$(echo $type | tr '[:upper:]' '[:lower:]').json"
  [ -f "$example" ] && npx ajv-cli validate -s "$schema" -d "$example" && echo "✓ $type"
done
```

---

## Versioning

Schema evolution follows [Semantic Versioning](https://semver.org/). See [CONTRIBUTING.md](../CONTRIBUTING.md#breaking-vs-additive-changes) for the full policy and [CHANGELOG.md](../CHANGELOG.md) for the history.

---

## Control-plane schema identity

The control-plane tranche under `schemas/control-plane/` contains legacy schemas imported with `$id` values under `socioprophet.org`.

Canonical wrappers with `schemas.srcos.ai/v2/...` `$id` values are provided as `schemas/control-plane/*.json` files that `allOf`-wrap the legacy `*.schema.json` files.

See `schemas/control-plane/README.md` for the definitive list.
