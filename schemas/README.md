# Schema Documentation

This document covers all 54 JSON Schema files in this directory, grouped by platform area. Every schema targets [JSON Schema draft 2020-12](https://json-schema.org/draft/2020-12/schema) and enforces `additionalProperties: false`.

## Common fields

All top-level (first-class) objects share these fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | ✅ | Stable URN (see [URN patterns](#urn-patterns)). |
| `type` | `const` | ✅ | Discriminator matching the schema name (e.g., `"Dataset"`). |
| `specVersion` | `string` | ✅ | Semver of the SourceOS spec this record conforms to (e.g., `"2.0.0"`). |

---

## URN patterns

| Object type | URN pattern |
|---|---|
| Agreement | `urn:srcos:agreement:<id>` |
| AgentSession | `urn:srcos:session:<id>` |
| CapabilityToken | `tok_<id>` (opaque) |
| Comment | `urn:srcos:comment:<id>` |
| Community | `urn:srcos:community:<id>` |
| Connector | `urn:srcos:connector:<id>` |
| Dataset | `urn:srcos:dataset:<id>` |
| ExecutionDecision | `urn:srcos:exec:decision:<id>` |
| ExperimentFlag | `urn:srcos:flag:<id>` |
| Field | `urn:srcos:field:<id>` |
| FrustrationSignal | `urn:srcos:signal:<id>` |
| GlossaryTerm | `urn:srcos:glossary:<id>` |
| MappingSpec | `urn:srcos:mapping:<id>` |
| MemoryEntry | `urn:srcos:memory:<id>` |
| Party | `urn:srcos:party:<id>` |
| PhysicalAsset | `urn:srcos:asset:<id>` |
| Policy | `urn:srcos:policy:<id>` |
| PolicyDecision | `urn:srcos:decision:<id>` |
| ProvenanceRecord | `urn:srcos:prov:<id>` |
| Rating | `urn:srcos:rating:<id>` |
| ReleaseReceipt | `urn:srcos:receipt:release:<id>` |
| RolloutPolicy | `urn:srcos:rollout:<id>` |
| RunRecord | `urn:srcos:run:<id>` |
| SchemaDefinition | `urn:srcos:schema:<id>` |
| SessionReceipt | `urn:srcos:receipt:session:<id>` |
| SessionReview | `urn:srcos:review:<id>` |
| SkillManifest | `urn:srcos:skill:<id>` |
| TagAssignment | _(embedded; no top-level URN)_ |
| TelemetryEvent | `urn:srcos:telemetry:<id>` |
| WorkflowSpec | `urn:srcos:workflow:<id>` |
| WorkloadSpec | `urn:srcos:workload:<id>` |

---

## Area 1 — Physical Assets

### Connector
**File:** `Connector.json` | **Example:** [`../examples/connector.json`](../examples/connector.json)

Describes a storage or compute connection point (S3, GCS, RDBMS, Kafka, etc.).

Required: `id`, `type`, `specVersion`, `name`, `kind`, `config`

`kind` enum: `s3 | gcs | azureBlob | rdbms | kafka | filesystem | httpApi | lakehouse`

### PhysicalAsset
**File:** `PhysicalAsset.json` | **Example:** [`../examples/asset.json`](../examples/asset.json)

A physical storage location reached via a Connector. Datasets reference PhysicalAssets via `assetRef`.

Required: `id`, `type`, `specVersion`, `assetKind`, `connectorId`, `location`

`assetKind` enum: `objectStore | rdbms | stream | file | api | lakehouse`

---

## Area 2 — Glossary

### GlossaryTerm
**File:** `GlossaryTerm.json` | **Example:** [`../examples/glossary.json`](../examples/glossary.json)

A canonical business term with definition, synonyms, semantic tags, and authority links.

Required: `id`, `type`, `specVersion`, `name`, `definition`

### AuthorityLink
**File:** `AuthorityLink.json` | **Example:** [`../examples/authority_link.json`](../examples/authority_link.json)

A reference to an external authority system (LDAP, Wikidata, SNOMED, etc.) corroborating an entity's identity or classification.

Required: `system`, `value`

---

## Area 3 — Governance

### Policy
**File:** `Policy.json` | **Example:** [`../examples/policy.json`](../examples/policy.json)

A rule set that evaluates subject–object–purpose triples. Contains `rules` (permit/deny clauses), `obligations`, and optional `exceptions`.

Required: `id`, `type`, `specVersion`, `name`, `scope`, `rules`, `obligations`

### Rule
**File:** `Rule.json` | **Example:** [`../examples/rule.json`](../examples/rule.json)

A single permit-or-deny clause within a Policy. Guards via an optional `PolicyCondition`.

Required: `effect`, `operations`

`effect` enum: `permit | deny`

### PolicyCondition
**File:** `PolicyCondition.json` | **Example:** [`../examples/policy_condition.json`](../examples/policy_condition.json)

An expression in a named policy language guarding a Rule's effect.

Required: `language`, `expr`

`language` enum: `jsonlogic | cel | rego | cedar`

### PolicyDecision
**File:** `PolicyDecision.json` | **Example:** [`../examples/decision.json`](../examples/decision.json)

The immutable, SHA-256-signed result of evaluating a Policy. Clients must verify `decisionHash` before acting.

Required: `id`, `type`, `specVersion`, `decision`, `policyId`, `inputs`, `issuedAt`, `expiresAt`, `decisionHash`

`decision` enum: `permit | deny | permitWithObligations`

### CapabilityToken
**File:** `CapabilityToken.json` | **Example:** [`../examples/token.json`](../examples/token.json)

A short-lived signed token granting scoped access. Issued by `POST /v2/tokens/issue` from a PolicyDecision. Referenced in RunRecords.

Required: `tokenId`, `subject`, `scope`, `purpose`, `decisionRef`, `exp`, `signature`

### Obligation
**File:** `Obligation.json` | **Example:** [`../examples/obligation.json`](../examples/obligation.json)

An enforceable action (obfuscation, logging, etc.) attached to a permit.

Required: `name`, `when`

`name` enum: `obfuscate_before_export | log_access | retain_provenance | mask_fields | aggregate_only | attest_container`

`when` enum: `pre | post | runtime`

### Exception
**File:** `Exception.json` | **Example:** [`../examples/exception.json`](../examples/exception.json)

A named override that permits an otherwise-denied action, with optional expiry.

Required: `name`, `reason`

### SubjectContext / SubjectSelector
**Files:** `SubjectContext.json`, `SubjectSelector.json` | **Examples:** [`../examples/subject_context.json`](../examples/subject_context.json), [`../examples/subject_selector.json`](../examples/subject_selector.json)

`SubjectContext` is the requestor side of a policy evaluation. `SubjectSelector` is the scope predicate in a Policy.

### ObjectContext / ObjectSelector
**Files:** `ObjectContext.json`, `ObjectSelector.json` | **Examples:** [`../examples/object_context.json`](../examples/object_context.json), [`../examples/object_selector.json`](../examples/object_selector.json)

`ObjectContext` is the target resource in a policy evaluation. `ObjectSelector` is the scope predicate in a Policy.

`objectType` enum: `dataset | field | asset | run | provenance | schema | agreement | any`

### PolicyBinding
**File:** `PolicyBinding.json` | **Example:** [`../examples/policy_binding.json`](../examples/policy_binding.json)

Associates a Policy with a specific WorkflowNode or workload.

Required: `policyId`, `appliesTo`

---

## Area 4 — Collaboration

### Comment
**File:** `Comment.json` | **Example:** [`../examples/comment.json`](../examples/comment.json)

A human annotation attached to any addressable object. Append-only.

Required: `id`, `type`, `specVersion`, `targetId`, `author`, `createdAt`, `body`

### Rating
**File:** `Rating.json` | **Example:** [`../examples/rating.json`](../examples/rating.json)

A numeric quality rating (1–5) for any addressable object.

Required: `id`, `type`, `specVersion`, `targetId`, `rater`, `createdAt`, `value`

### Community
**File:** `Community.json` | **Example:** [`../examples/community.json`](../examples/community.json)

A named group of subjects sharing governance or data interests.

Required: `id`, `type`, `specVersion`, `name`

---

## Area 5 — Models & Schemas

### SchemaDefinition
**File:** `SchemaDefinition.json` | **Example:** [`../examples/schema.json`](../examples/schema.json)

A logical schema composed of typed EntityFields. Datasets reference schemas via `schemaRef`.

Required: `id`, `type`, `specVersion`, `name`, `fields`

### EntityField
**File:** `EntityField.json` | **Example:** [`../examples/entity_field.json`](../examples/entity_field.json)

A single named field within a SchemaDefinition with type, nullability, and constraints.

Required: `name`, `dataType`

### ValidValues
**File:** `ValidValues.json` | **Example:** [`../examples/valid_values.json`](../examples/valid_values.json)

Acceptable-value constraint: enumeration, numeric range, or regex.

Required: `kind`, `values`

`kind` enum: `enumeration | range | regex`

### Field
**File:** `Field.json` | **Example:** [`../examples/field.json`](../examples/field.json)

A catalogued column in a Dataset (richer than EntityField: includes quality profile and semantic tags).

Required: `id`, `type`, `specVersion`, `datasetId`, `path`, `dataType`, `semantics`, `quality`

### TagAssignment
**File:** `TagAssignment.json` | **Example:** [`../examples/tag_assignment.json`](../examples/tag_assignment.json)

A classification tag applied to a field or glossary term with curation state and confidence score.

Required: `tag`, `state`, `confidence`, `source`

`state` enum: `inferred | curated | rejected`

### ProfileStats
**File:** `ProfileStats.json` | **Example:** [`../examples/profile_stats.json`](../examples/profile_stats.json)

Statistical summary of a field's data distribution.

Required: `rowCount`, `nullCount`

### QualityMetric
**File:** `QualityMetric.json` | **Example:** [`../examples/quality_metric.json`](../examples/quality_metric.json)

A named quality dimension score (completeness, validity, uniqueness, consistency, timeliness).

Required: `name`, `value`

### MappingSpec
**File:** `MappingSpec.json` | **Example:** [`../examples/mapping.json`](../examples/mapping.json)

A proposed or curated semantic mapping between two fields across datasets.

Required: `id`, `type`, `specVersion`, `from`, `to`, `confidence`, `evidence`, `state`

`state` enum: `proposed | curated | rejected`

### MappingEvidence
**File:** `MappingEvidence.json` | **Example:** [`../examples/mapping_evidence.json`](../examples/mapping_evidence.json)

A single piece of evidence supporting a MappingSpec.

Required: `method`, `score`

`method` enum: `labelExact | labelStringSim | valueCosine | valueContainment | kvOverlap | ontologyAnchor | blocking`

---

## Area 6 — Agreements

### Agreement
**File:** `Agreement.json` | **Example:** [`../examples/agreement.json`](../examples/agreement.json)

A data usage agreement specifying license, restrictions, retention, and jurisdiction.

Required: `id`, `type`, `specVersion`, `title`, `parties`, `terms`, `effective`

### Party
**File:** `Party.json` | **Example:** [`../examples/party.json`](../examples/party.json)

A participant in an Agreement (person, org, or service).

Required: `partyId`, `name`, `kind`

`kind` enum: `person | org | service`

---

## Area 7 — Lineage

### Dataset
**File:** `Dataset.json` | **Example:** [`../examples/dataset.json`](../examples/dataset.json)

A logical data collection backed by a PhysicalAsset, with governance and lifecycle metadata.

Required: `id`, `type`, `specVersion`, `name`, `assetRef`, `schemaRef`, `governance`, `lifecycle`

### RunRecord
**File:** `RunRecord.json` | **Example:** [`../examples/run.json`](../examples/run.json)

A record of a workload execution within a DataSphere.

Required: `id`, `type`, `specVersion`, `workload`, `sphere`, `inputs`, `outputs`, `tokenRef`, `status`, `time`

`status` enum: `started | succeeded | failed | aborted`

### ProvenanceRecord
**File:** `ProvenanceRecord.json` | **Example:** [`../examples/provenance.json`](../examples/provenance.json)

A PROV-compatible lineage record linking an activity to its agent and input/output entities.

Required: `id`, `type`, `specVersion`, `activity`, `agent`, `entities`, `createdAt`

### WorkflowSpec
**File:** `WorkflowSpec.json` | **Example:** [`../examples/workflow_spec.json`](../examples/workflow_spec.json)

A DAG of WorkflowNodes and WorkflowEdges defining a multi-step pipeline.

Required: `id`, `type`, `specVersion`, `name`, `nodes`, `edges`

### WorkflowNode
**File:** `WorkflowNode.json` | **Example:** [`../examples/workflow_node.json`](../examples/workflow_node.json)

A single computation step in a WorkflowSpec DAG.

Required: `nodeId`, `workload`, `inputs`, `outputs`

### WorkflowEdge
**File:** `WorkflowEdge.json` | **Example:** [`../examples/workflow_edge.json`](../examples/workflow_edge.json)

A directed dependency between two WorkflowNodes.

Required: `from`, `to`

### WorkloadSpec
**File:** `WorkloadSpec.json` | **Example:** [`../examples/workload_spec.json`](../examples/workload_spec.json)

The specification of an executable unit (container, Spark job, function, stream processor).

Required: `workloadId`, `kind`, `image`, `entrypoint`

`kind` enum: `sparkJob | container | function | streamProcessor`

### DataRef
**File:** `DataRef.json` | **Example:** [`../examples/data_ref.json`](../examples/data_ref.json)

A typed reference to a data entity with optional field-path scoping.

Required: `refType`, `id`

`refType` enum: `dataset | asset | streamTopic | file`

### DataSphere
**File:** `DataSphere.json` | **Example:** [`../examples/data_sphere.json`](../examples/data_sphere.json)

A logical isolation boundary for workload execution.

Required: `sphereId`, `name`, `boundary`, `controls`

### Trigger
**File:** `Trigger.json` | **Example:** [`../examples/trigger.json`](../examples/trigger.json)

A workflow activation specification (schedule, event, or manual).

Required: `kind`

`kind` enum: `schedule | event | manual`

---

## Area 8 — Agent Plane

### AgentSession
**File:** `AgentSession.json` | **Example:** [`../examples/agent_session.json`](../examples/agent_session.json)

A record of a single agent task-execution session.

Required: `id`, `type`, `specVersion`, `role`, `status`, `mode`, `workspaceRef`, `substrate`, `surface`, `skillRefs`, `memoryRefs`, `decisionRefs`, `time`

`role` enum: `main | explorer | planner | executor | reviewer | auditor | reverser | custom`

`status` enum: `created | waiting | running | paused | completed | failed | canceled | merged | reversed`

`mode` enum: `plan | ask | execute | review`

`substrate` enum: `local | remote-local | cloud | background | event-pushed | ci`

### ExecutionDecision
**File:** `ExecutionDecision.json` | **Example:** [`../examples/execution_decision.json`](../examples/execution_decision.json)

A real-time agent execution decision record.

Required: `id`, `type`, `specVersion`, `sessionRef`, `decision`, `reason`, `issuedAt`, `decisionHash`

`decision` enum: `allow | deny | ask | defer | rewrite`

### ExecutionSurface
**File:** `ExecutionSurface.json` | **Example:** [`../examples/execution_surface.json`](../examples/execution_surface.json)

Execution-environment constraints for an agent session (sandbox, network, paths).

Required: `pty`, `workdir`, `background`, `reviewOnly`, `worktreeStrategy`, `sandboxMode`, `networkMode`, `egressAllowlist`, `elevated`

`sandboxMode` enum: `none | user | container | vm | browser-sandbox`

`networkMode` enum: `none | allowlist | full`

### SkillManifest
**File:** `SkillManifest.json` | **Example:** [`../examples/skill_manifest.json`](../examples/skill_manifest.json)

A machine-readable descriptor for an agent skill.

Required: `id`, `type`, `specVersion`, `name`, `version`, `entryDoc`, `description`, `activationRules`, `requires`, `policyBindings`, `artifactOutputs`, `reviewMode`, `allowShellExecution`

### MemoryEntry
**File:** `MemoryEntry.json` | **Example:** [`../examples/memory_entry.json`](../examples/memory_entry.json)

A durable knowledge entry in the agent memory store.

Required: `id`, `type`, `specVersion`, `kind`, `namespace`, `key`, `payloadRef`, `citationRefs`, `scope`, `freshness`

`kind` enum: `rule | learned | recap`

### SessionReceipt
**File:** `SessionReceipt.json` | **Example:** [`../examples/session_receipt.json`](../examples/session_receipt.json)

A summary produced at the close of an agent session.

Required: `id`, `type`, `specVersion`, `sessionRef`, `status`, `artifactRefs`, `decisionRefs`, `gateResults`, `capturedAt`

`status` enum: `success | failure | paused | deferred | canceled`

### SessionReview
**File:** `SessionReview.json` | **Example:** [`../examples/session_review.json`](../examples/session_review.json)

A post-session retrospective linking session outcomes to learned memory entries.

Required: `id`, `type`, `specVersion`, `sessionRef`, `summaryRef`, `learnedMemoryRefs`, `reviewedAt`

### TelemetryEvent
**File:** `TelemetryEvent.json` | **Example:** [`../examples/telemetry_event.json`](../examples/telemetry_event.json)

A structured telemetry event from an agent session.

Required: `id`, `type`, `specVersion`, `sessionRef`, `eventType`, `capturedAt`

`severity` enum: `debug | info | warn | error`

### FrustrationSignal
**File:** `FrustrationSignal.json` | **Example:** [`../examples/frustration_signal.json`](../examples/frustration_signal.json)

A negative user-experience signal observed during a session.

Required: `id`, `type`, `specVersion`, `sessionRef`, `signal`, `capturedAt`

`signal` enum: `strong-negative-language | cancel | repeated-failure | tool-loop | user-interrupt`

---

## Cross-cutting schemas

### EventEnvelope
**File:** `EventEnvelope.json` | **Example:** [`../examples/event_envelope.json`](../examples/event_envelope.json)

Generic wrapper for all platform events. All AsyncAPI channels use this schema.

Required: `eventId`, `eventType`, `specVersion`, `occurredAt`, `actor`, `objectId`, `payload`

### Link
**File:** `Link.json` | **Example:** [`../examples/link.json`](../examples/link.json)

A typed hyperlink following HATEOAS conventions.

Required: `rel`, `href`

### ExperimentFlag
**File:** `ExperimentFlag.json` | **Example:** [`../examples/experiment_flag.json`](../examples/experiment_flag.json)

A named feature flag with lifecycle state.

Required: `id`, `type`, `specVersion`, `name`, `state`

`state` enum: `off | shadow | internal | beta | on | retired`

### RolloutPolicy
**File:** `RolloutPolicy.json` | **Example:** [`../examples/rollout_policy.json`](../examples/rollout_policy.json)

A rule set controlling incremental rollout of an ExperimentFlag.

Required: `id`, `type`, `specVersion`, `flagRef`, `rules`

### ReleaseReceipt
**File:** `ReleaseReceipt.json` | **Example:** [`../examples/release_receipt.json`](../examples/release_receipt.json)

A verification record for a release target.

Required: `id`, `type`, `specVersion`, `releaseTarget`, `verifiedAt`, `status`

`status` enum: `verified | failed | partial`