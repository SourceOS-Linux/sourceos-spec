# Changelog

All notable changes to the SourceOS/SociOS Typed Contracts specification are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
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
