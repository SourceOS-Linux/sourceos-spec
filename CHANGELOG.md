# Changelog

All notable changes to the SourceOS/SociOS Typed Contracts specification are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- A/B fallback update contract v0.1 (TRUST FABRIC W9.2): `UpdateSlot` (one of exactly two slots, carrying the GPT priority-boot attribute triple `bootPriority`/`triesRemaining`/`successful`, the installed payload digest, and a deliberate `role` vs `currentlyRunning` split so the fallback slot stays describable during a trial boot), `UpdateTransaction` (one apply attempt: write target, pinned probe, per-attempt boot record naming where each failure fell back to, terminal `promoted`/`rolled-back`/`refused` outcome with a closed `rollbackReason` set), and `UpdateHealthProbe` (the digest-pinned promotion gate: non-empty check set with at least one blocking check, mandatory hardware+software watchdog pair enforced by two `contains` clauses, `evaluatedIn` closed to post-boot userspace, `onProbeUnavailable` closed to `fail`). **Normative invariant — the currently-good slot is never overwritten by the update being applied** — enforced three ways: by schema within a document (a top-level `not`/`anyOf` enumerating the two illegal `(fromSlot, toSlot)` pairs, plus `UpdateSlot`'s `state: writing` ⇒ `role: candidate`), by schema on the settle path (four if/then clauses pinning `settledOnSlot` to `fromSlot` on rollback/refusal and to `toSlot` on promotion), and across documents by the validator (a settled transaction's `preservedPayloadDigest` still equals the active slot's `payloadDigest`). The attempt budget follows the GPT attribute — decremented by the bootloader *before* control transfers, so a payload that hangs before userspace still consumes an attempt — and `refused` is terminal, which is what ends the boot loop. Includes a refused-update and a promoted-update example set telling two coherent end-to-end stories, fourteen negative conformance vectors (`fixtures/ab-update/conformance.json`), a `validate-ab-update-examples` target whose probe-digest check is *recomputed* rather than read back, and a normative spec note (`specs/ab-fallback-update-contract.md`). Reference implementation: `AbUpdateMachine` in `sourceos-boot`.
- `make validate` now also runs the duplicate schema `$id` guardrail, which previously ran only in CI — a local run could not reproduce the check that gates the PR.
- KnowledgeNugget contract v0.1 (the estate's L2 content grain): warrant-typed knowledge fragments generalizing the production IFM warrant-typed extraction — content-addressed source spans (`docRef` + span + `sha256-` content hash), a closed four-kind warrant taxonomy (`direct-quote`/`computed`/`inferred`/`model-generated`) with evidence refs and confidence, ontology type refs (`kkoTypeRefs`), normalized `canonicalPayload`, typed provenance chain links, and `wallTime`/`logicalTime` carried verbatim from the MPCC `ConversationEvent` envelope (parity machine-enforced). Normative: `model-generated` nuggets MUST stay visibly distinguishable downstream (admissibility discounting), and `computed`/`inferred` warrants must cite evidence (schema-enforced). Includes direct-quote and model-generated examples, negative conformance vectors (`fixtures/knowledge-nugget/conformance.json`), a `validate-knowledge-nugget-examples` target, and a normative spec note (`specs/knowledge-nugget-contract.md`).
- SemanticAction contract v0.1 (the declarative typed-action registry for the NL→plan compiler): ontology-typed inputs and output (KKO concept URIs recommended, shared with `KnowledgeNugget.kkoTypeRefs`), a closed constraint taxonomy (`subClassOf`/`instanceOf`/`sameAs` — polymorphism via subsumption), executor binding, registry metadata (owner + deprecated), and a two-value effect posture: actions are side-effect-free at plan-search time, and `sideEffects: "effect-request"` declares the executor emits an MPCC `EffectRequest` and defers to an `EffectDecision` rather than acting directly — no direct-mutation vocabulary exists (validator-pinned). Includes pure-lookup and effect-request examples, negative conformance vectors (`fixtures/semantic-action/conformance.json`), a `validate-semantic-action-examples` target, and a normative spec note (`specs/semantic-action-contract.md`).
- MPCC event contract v0.1 (conversation + trading event family): `ConversationEvent` (the canonical 26-field conversation-fabric event — causal parents, authority context with delegation chain, visibility scope, requested/approved/actual effect references, modality, speech act), `EffectRequest` / `EffectDecision` / `EffectRecord` (the requested → approved → actual → compensated effect lifecycle with idempotency keys, referencing `PolicyDecision` / `ExecutionDecision` rather than duplicating them), `NullAbsenceRecord` (12-kind null/absence taxonomy), and the trading families `MarketDataEvent`, `OrderIntent`, `ExecutionReport`, `PositionChange`, `ReconciliationRecord` as profiles of the ConversationEvent envelope (one shared envelope vocabulary; parity machine-enforced). Includes canonical examples telling one end-to-end governed trade story, negative conformance vectors (`fixtures/mpcc-event-contract/conformance.json`), a `validate-mpcc-event-examples` target, and a normative spec note (`specs/mpcc-event-contract.md`). Provenance: SocioProphet/profit-mpcc, hardened to the policy-integrity tranche-0001 strictness bar.
- Epistemic Assay contracts: `ReasoningAssay` (a typed verdict on a claim over five orthogonal axes — method, binding, verifier, agreement, authority — whose `ok`/`sad`/`bad` `projectedState` is a render-time projection, not a stored scalar) and `AssayStandard` (a verifier's measured, versioned reliability — the calibration reference every assay must point at). Includes canonical `ok`/`sad`/`bad` examples, ADR (`docs/adr/ADR-epistemic-assay-verdict-v0-1.md`), and a `validate-reasoning-examples` target that also enforces projection soundness (recomputes `assay()` from the stored axes and fails on drift) and retroactively brings the existing reasoning family under `make validate`.
- `ReasoningReceipt.assay` (optional) — the reserved receipt landing spot for the Assay: a render-time, run-level epistemic summary that references its run's `ReasoningAssay` records by URN (`assayRefs`) and surfaces the projected `overallState`, weakest-link `binding`, verifier `calibrationRef`, per-state `counts`, and `projectedAt`. A cache of the referenced verdicts, not authoritative over them — re-projectable when an `AssayStandard` improves. Backward-compatible (optional field). The assay's `authority` axis continues to mirror `EventEnvelope.actor`/`integrity`, so the envelope needs no structural change.
- Onboarding control-plane contract family: `WorkspaceScope`, `TrustMode`, `CapabilityPack`, `ConnectorActionScope`, `AutomationTemplate`, and `OnboardingReceipt`, with canonical first-run examples, semantic vocabulary seed, ADR, and `validate-onboarding-examples` validation target.
- `ReasoningEvent.controlFlow` (optional) + a reserved control-flow `eventType` vocabulary (`reasoning.tool.called` / `reasoning.decision.branched` / `reasoning.subrun.spawned` / `reasoning.subrun.joined` / `reasoning.run.completed`) so emitters can carry a run's operational control flow for downstream narration-fidelity verification (SP-TRACE-CFR). Backward-compatible; operational structure only (no raw reasoning). See `docs/reasoning-control-flow-events.md` and `examples/reasoning_event_control_flow.json`.
- SourceOS interaction substrate top-level index and README discovery links for `SourceOSInteractionEvent`, generated TypeScript/Python artifacts, and the Noetica → Superconscious → AgentPlane → AgentTerm reference flow.
- Runtime observability and capability governance contracts: `CapabilityLedger`, `BrowserAutomationReceipt`, `GitWorkspaceState`, `OrphanEventReceipt`, and `RuntimeInstallReceipt` with canonical examples, validation wiring (`tools/validate_runtime_observability_examples.py`), a contract catalog, and ADR-0012.
- Reasoning run contracts: `ReasoningRun`, `ReasoningEvent`, `ReasoningReceipt`, `ReasoningReplayPlan`, and `ReasoningBenchmark` with canonical examples and a contract-additions note for the Superconscious reference loop.
- Agent Machine / Model Carry schemas: `SourceOSModelCarryRef`, `InferenceProvider`, `ModelResidency`, `PlacementFact`, and `AgentMachineReceipt` with canonical examples and a contract-additions placement note.
- NLBoot object schemas: `NLBootPlan`, `ArtifactCacheRecord`, `BootProofRecord`, `AppleSiliconAdapterEvidence` with canonical examples and validation (`tools/validate_nlboot_examples.py`)
- Compression Commons: `CompressionEvaluation` schema and canonical example (`examples/compressionevaluation.json`)
- Truth Plane: `TruthSurface` and `DeltaSurface` schemas + canonical examples (`examples/truth_surface.json`, `examples/delta_surface.json`)
- Control-plane: `IncidentEvent` schema for incident lifecycle events
- Control-plane: canonical wrapper `$id` model for legacy schemas (`schemas/control-plane/*.json` wrappers)
- Truth Plane: OpenAPI/AsyncAPI patch fragments (`openapi.truth-plane.patch.yaml`, `asyncapi.truth-plane.patch.yaml`)
- CI/spec integrity: schema identity guardrails (duplicate `$id` detection + control-plane wrapper `$id` resolution tests)
- `description` fields on all 54 schemas and all properties (non-breaking documentation improvement)
- `ARCHITECTURE.md` — two-plane architecture, schema families, governance lifecycle, URN table
- `CONTRIBUTING.md` — schema authoring conventions, URN naming guide, PR checklist
- `docs/adr/` — Architecture Decision Records for key design choices
- `examples/README.md` — guide to the example payloads
- `semantic/README.md` — guide to the JSON-LD and Hydra overlays
- Expanded `semantic/context.jsonld` to cover all 54 schema types
- Expanded `semantic/hydra.jsonld` to cover all API resource classes
- OpenAPI: `summary`, `description`, `tags`, security scheme, and error responses (`400`, `401`, `403`, `422`) on every operation
- AsyncAPI: channel and message `description` fields; Kafka `bindings` on every channel
- Missing `examples/` files for all agent-plane and supporting schemas

### Changed
- `README.md` rewritten as a proper project introduction with repo layout, schema family table, quick-start commands, and contribution links
- `schemas/README.md` corrected: URN patterns now match actual schema `pattern` constraints; example JSON replaced with accurate, AJV-validated payloads; all six schema families documented
- `.github/PULL_REQUEST_TEMPLATE.md` expanded to a full structured PR checklist

### Fixed
- `schemas/README.md` used `urn:sourceos:` prefix — corrected to `urn:srcos:` throughout
- Resolved cross-branch merge conflicts across core docs/specs/examples and agent-plane schemas to restore a clean, mergeable branch state

---

## [2.0.0] — 2025-12-24

### Added
- `Agreement` and `Party` schemas (Area 6: Agreements)
- `GlossaryTerm` and `AuthorityLink` schemas (Area 2: Glossary)
- `Connector` and `PhysicalAsset` schemas (Area 1: Physical Assets)
- `SchemaDefinition`, `EntityField`, `ValidValues` schemas (Area 5: Models/Schemas)
- `ProvenanceRecord` schema with W3C PROV-compatible entity roles
- `Comment`, `Rating`, `Community` schemas (Area 4: Collaboration)
- `PolicyCondition` with typed expression language (`jsonlogic`, `cel`, `rego`, `cedar`)
- `MappingSpec` and `MappingEvidence` schemas for field-to-field lineage
- `TagAssignment` with confidence, source provenance, and review record
- Agent-plane schemas: `AgentSession`, `ExecutionDecision`, `ExecutionSurface`, `SkillManifest`, `MemoryEntry`, `SessionReceipt`, `SessionReview`, `TelemetryEvent`, `FrustrationSignal`
- Release/experiment schemas: `ExperimentFlag`, `RolloutPolicy`, `ReleaseReceipt`
- Hydra/JSON-LD semantic overlay (`semantic/context.jsonld`, `semantic/hydra.jsonld`)
- Agent-plane OpenAPI patch (`openapi.agent-plane.patch.yaml`)
- Agent-plane AsyncAPI patch (`asyncapi.agent-plane.patch.yaml`)

### Changed
- `Dataset` now requires explicit `assetRef` and `schemaRef` URN references (previously physical storage was implicit)
- `Policy` rules upgraded from a flat structure to `Rule` + `PolicyCondition` with a declared `language` field
- All IDs changed from opaque strings to `urn:srcos:` URNs with enforced `pattern` constraints

### Removed
- Implicit physical fields from `Dataset` (replaced by `PhysicalAsset` + `Connector` references)

---

## [1.0.0] — (initial, pre-repository)

Initial typed contract set covering:
- `Dataset`, `Field`, `Policy`, `PolicyDecision`, `CapabilityToken`
- `RunRecord`, `WorkflowSpec`, `WorkflowNode`, `WorkflowEdge`, `WorkloadSpec`
- `DataSphere`, `DataRef`, `Obligation`, `SubjectContext`, `ObjectContext`
- `EventEnvelope`, `Link`
