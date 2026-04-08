# Schema Catalog

This directory contains all 54 JSON Schema (draft 2020-12) files that make up the SourceOS/SociOS Typed Contracts specification.

---

## Quick reference

| File | Type | URN prefix |
|------|------|-----------|
| `AgentSession.json` | AgentSession | `urn:srcos:session:` |
| `Agreement.json` | Agreement | `urn:srcos:agreement:` |
| `AuthorityLink.json` | AuthorityLink | _(sub-object, no top-level id)_ |
| `CapabilityToken.json` | CapabilityToken | _(plain `tokenId` string)_ |
| `Comment.json` | Comment | `urn:srcos:comment:` |
| `Community.json` | Community | `urn:srcos:community:` |
| `Connector.json` | Connector | `urn:srcos:connector:` |
| `DataRef.json` | DataRef | _(sub-object, no top-level id)_ |
| `DataSphere.json` | DataSphere | `urn:srcos:sphere:` |
| `Dataset.json` | Dataset | `urn:srcos:dataset:` |
| `EntityField.json` | EntityField | _(sub-object inside SchemaDefinition)_ |
| `EventEnvelope.json` | EventEnvelope | `urn:srcos:event:` |
| `Exception.json` | Exception | _(sub-object inside Policy)_ |
| `ExecutionDecision.json` | ExecutionDecision | `urn:srcos:exec-decision:` |
| `ExecutionSurface.json` | ExecutionSurface | _(sub-object inside AgentSession)_ |
| `ExperimentFlag.json` | ExperimentFlag | `urn:srcos:flag:` |
| `Field.json` | Field | `urn:srcos:field:` |
| `FrustrationSignal.json` | FrustrationSignal | `urn:srcos:frustration:` |
| `GlossaryTerm.json` | GlossaryTerm | `urn:srcos:glossary:` |
| `Link.json` | Link | _(sub-object, no id)_ |
| `MappingEvidence.json` | MappingEvidence | _(sub-object inside MappingSpec)_ |
| `MappingSpec.json` | MappingSpec | `urn:srcos:mapping:` |
| `MemoryEntry.json` | MemoryEntry | `urn:srcos:memory:` |
| `ObjectContext.json` | ObjectContext | _(sub-object, no id)_ |
| `ObjectSelector.json` | ObjectSelector | _(sub-object inside Policy scope)_ |
| `Obligation.json` | Obligation | _(sub-object, no id)_ |
| `Party.json` | Party | `urn:srcos:party:` |
| `PhysicalAsset.json` | PhysicalAsset | `urn:srcos:asset:` |
| `Policy.json` | Policy | `urn:srcos:policy:` |
| `PolicyBinding.json` | PolicyBinding | _(sub-object inside WorkflowSpec)_ |
| `PolicyCondition.json` | PolicyCondition | _(sub-object inside Rule)_ |
| `PolicyDecision.json` | PolicyDecision | `urn:srcos:decision:` |
| `ProfileStats.json` | ProfileStats | _(sub-object inside Field.quality)_ |
| `ProvenanceRecord.json` | ProvenanceRecord | `urn:srcos:prov:` |
| `QualityMetric.json` | QualityMetric | _(sub-object inside Field.quality)_ |
| `Rating.json` | Rating | `urn:srcos:rating:` |
| `ReleaseReceipt.json` | ReleaseReceipt | `urn:srcos:release-receipt:` |
| `RolloutPolicy.json` | RolloutPolicy | `urn:srcos:rollout:` |
| `Rule.json` | Rule | _(sub-object inside Policy)_ |
| `RunRecord.json` | RunRecord | `urn:srcos:run:` |
| `SchemaDefinition.json` | SchemaDefinition | `urn:srcos:schema:` |
| `SessionReceipt.json` | SessionReceipt | `urn:srcos:receipt:session:` |
| `SessionReview.json` | SessionReview | `urn:srcos:session-review:` |
| `SkillManifest.json` | SkillManifest | `urn:srcos:skill:` |
| `SubjectContext.json` | SubjectContext | _(sub-object, no id)_ |
| `SubjectSelector.json` | SubjectSelector | _(sub-object inside Policy scope)_ |
| `TagAssignment.json` | TagAssignment | _(sub-object inside Field/GlossaryTerm)_ |
| `TelemetryEvent.json` | TelemetryEvent | `urn:srcos:telemetry:` |
| `Trigger.json` | Trigger | _(sub-object inside WorkflowSpec)_ |
| `ValidValues.json` | ValidValues | _(sub-object inside EntityField)_ |
| `WorkflowEdge.json` | WorkflowEdge | _(sub-object inside WorkflowSpec)_ |
| `WorkflowNode.json` | WorkflowNode | _(sub-object inside WorkflowSpec)_ |
| `WorkflowSpec.json` | WorkflowSpec | `urn:srcos:workflow:` |
| `WorkloadSpec.json` | WorkloadSpec | `urn:srcos:workload:` |

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
| `Rating` | A 1–5 star rating on any addressable object |
| `Community` | A named group of subject URNs |

### Family 5 – Models / Schemas

| Schema | Description |
|--------|-------------|
| `SchemaDefinition` | A named, versioned logical schema composed of `EntityField`s |
| `EntityField` | A field descriptor inside a `SchemaDefinition` |
| `Field` | A fully annotated, quality-profiled field attached to a live `Dataset` |
| `TagAssignment` | A classification tag with confidence score, source, and review record |
| `ValidValues` | Enumeration, numeric range, or regex constraint on a field |
| `QualityMetric` | A named quality dimension (completeness, validity, …) scored 0–1 |
| `ProfileStats` | Statistical profile of a column: row count, nulls, distinct values, top-N values |

### Family 6 – Agreements

| Schema | Description |
|--------|-------------|
| `Agreement` | A data-sharing agreement between one or more parties with terms and effective dates |
| `Party` | A named signatory (person, org, or service) with optional authority links |

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
| `MappingSpec` | A field-to-field semantic mapping with multi-method confidence evidence |
| `MappingEvidence` | A single evidence item for a `MappingSpec` (label similarity, value overlap, …) |
| `EventEnvelope` | The universal wrapper for all AsyncAPI channel messages |

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

Schema evolution follows [Semantic Versioning](https://semver.org/).  See [CONTRIBUTING.md](../CONTRIBUTING.md#breaking-vs-additive-changes) for the full policy and [CHANGELOG.md](../CHANGELOG.md) for the history.
