# Changelog

All notable changes to the SourceOS/SociOS Typed Contracts Specification are documented here.

This file follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) conventions. The project uses [semantic versioning](https://semver.org/).

---

## [Unreleased]

### Added
- `description` fields on all 54 schemas (top-level and all properties).
- 41 new example files covering every schema type (`examples/agent_session.json`, `examples/workflow_spec.json`, etc.).
- Comprehensive `README.md` with architecture diagram, repository layout, implementation guide, and validation instructions.
- Rewrote `schemas/README.md` to document all 54 schemas with URN patterns, required fields, and enum values.
- `CONTRIBUTING.md` with schema design conventions, URN naming rules, PR process, and versioning policy.
- `CHANGELOG.md` (this file).
- `docs/adr/` directory with five Architecture Decision Records:
  - ADR-0001: Use JSON Schema draft 2020-12
  - ADR-0002: Stable URN identifier scheme
  - ADR-0003: Generic EventEnvelope for all channels
  - ADR-0004: Multi-language policy conditions
  - ADR-0005: Additive patch pattern for the agent plane
- `.github/workflows/validate.yml` CI workflow for schema lint and example validation.
- `.github/PULL_REQUEST_TEMPLATE.md` proper PR template.

### Changed
- Reconciled long-lived branch drift across documentation, API contracts, examples, and schema artifacts to unblock merge-to-`main` conflict resolution (no contract-level semantic changes).
- `openapi.yaml` — added `info.description`, `info.contact`, `info.license`, `components/responses` (BadRequest, Unauthorized, Forbidden, NotFound, InternalServerError), `GET` and `DELETE` operations for all resources, operation `summary` and `description` strings, and 4xx/5xx responses on all endpoints.
- `openapi.agent-plane.patch.yaml` — added operation summaries, descriptions, `GET` operations for sessions, skills, and memory, and error responses.
- `asyncapi.yaml` — added `info.description`, `info.contact`, `info.license`, `subscribe` directions for all channels, channel `description` and `operationId` values, and five new channels for `agreement`, `connector`, `provenance`, `schema`, and `token` events.
- `asyncapi.agent-plane.patch.yaml` — added channel descriptions, `subscribe` directions, and `operationId` values.
- `semantic/context.jsonld` — expanded from 7 to 54 type mappings.
- `semantic/hydra.jsonld` — expanded from 2 to 21 `hydra:supportedClass` entries covering all API-accessible resources.

### Removed
- `.IMPORT_SOURCE.txt` — internal import artifact removed from the repository.
- `pulls/1.json` — test fixture artifact removed from the repository.

---

## [2.0.0] — 2025-12-24

### Added
- Full v2 schema set: `Agreement`, `GlossaryTerm`, `Connector`, `PhysicalAsset`, `SchemaDefinition`, `ProvenanceRecord`, `Comment`, `Rating`, `Community`.
- `PolicyCondition` with declared language (`jsonlogic`, `cel`, `rego`, `cedar`) replacing untyped condition objects.
- Agent Plane schema family: `AgentSession`, `ExecutionDecision`, `ExecutionSurface`, `SkillManifest`, `MemoryEntry`, `SessionReceipt`, `SessionReview`, `TelemetryEvent`, `FrustrationSignal`.
- Feature-flag schemas: `ExperimentFlag`, `RolloutPolicy`.
- Release tracking: `ReleaseReceipt`.
- Semantic overlay: `semantic/context.jsonld` and `semantic/hydra.jsonld`.
- Additive patch pattern: `openapi.agent-plane.patch.yaml` and `asyncapi.agent-plane.patch.yaml`.
- `Dataset` now explicitly references `assetRef`, `schemaRef`, and `governance.agreements` (no implicit physical fields).

### Changed
- `Dataset.governance` upgraded to include `agreements` and `usageDefinitions` arrays.
- All schemas enforce `additionalProperties: false`.
- IDs standardised to `urn:srcos:…` URN scheme.

---

## [1.0.0] — 2025-06-01 _(initial)_

### Added
- Initial schema set: `Dataset`, `Field`, `Policy`, `PolicyDecision`, `CapabilityToken`, `RunRecord`, `WorkflowSpec`, `WorkflowNode`, `WorkflowEdge`, `WorkloadSpec`, `DataRef`, `DataSphere`.
- `openapi.yaml` with metadata plane endpoints.
- `asyncapi.yaml` with dataset, policy, run, mapping, and glossary channels.
