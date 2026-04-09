# Architecture

This document describes the structural design of the SourceOS/SociOS Typed Contracts specification: the two-plane model, schema families, the governance lifecycle, and the URN identity scheme.

---

## 1 Two-plane model

The specification is split into two composable planes, each with its own OpenAPI patch file and AsyncAPI patch file.

```
┌──────────────────────────────────────────────────────────────┐
│                    METADATA PLANE                            │
│  openapi.yaml  ·  asyncapi.yaml                              │
│                                                              │
│  Physical assets  →  Datasets  →  Fields  →  Glossary        │
│  Policies / Decisions / Tokens / Obligations                 │
│  Workflows / Runs / Provenance                               │
│  Collaboration (Comments, Ratings, Communities)              │
│  Agreements                                                  │
└──────────────────────┬───────────────────────────────────────┘
                       │ references via URNs
┌──────────────────────▼───────────────────────────────────────┐
│                     AGENT PLANE                              │
│  openapi.agent-plane.patch.yaml  ·  asyncapi.agent-plane.patch.yaml │
│                                                              │
│  AgentSessions  →  ExecutionDecisions  →  SessionReceipts    │
│  SkillManifests  ·  MemoryEntries  ·  TelemetryEvents        │
│  FrustrationSignals  ·  SessionReviews                       │
└──────────────────────────────────────────────────────────────┘
```

**Metadata plane** (`openapi.yaml` / `asyncapi.yaml`): manages cataloguing, governance, and execution of data workloads. It is the source of truth for what data exists, who may access it, and what happened to it.

**Agent plane** (`openapi.agent-plane.patch.yaml` / `asyncapi.agent-plane.patch.yaml`): manages autonomous agent sessions that operate *on* the metadata plane. An agent session records which skills and memories it used, every `ExecutionDecision` it made, and its outcome via a `SessionReceipt`.

The patch files are **additive fragments**, not standalone specs. An implementation merges each patch into the base spec at deploy time.

---

## 2 Schema families

### Family 1 – Physical Assets
Describes where data physically lives.

| Schema | Purpose |
|--------|---------|
| `Connector` | A named, typed connection (S3, GCS, RDBMS, Kafka, …) |
| `PhysicalAsset` | A specific resource reachable through a `Connector` |

### Family 2 – Glossary
Shared business vocabulary anchored to external authority systems.

| Schema | Purpose |
|--------|---------|
| `GlossaryTerm` | A defined term with synonyms and classification tags |
| `AuthorityLink` | A pointer to an external controlled vocabulary (e.g. SNOMED, ISO) |

### Family 3 – Governance
The policy engine: evaluates access requests and issues short-lived capability tokens.

| Schema | Purpose |
|--------|---------|
| `Policy` | A named access policy with subjects, objects, purposes, rules, and obligations |
| `Rule` | A single `permit`/`deny` rule with an optional `PolicyCondition` |
| `PolicyCondition` | A rule expression in one of four languages: `jsonlogic`, `cel`, `rego`, `cedar` |
| `SubjectSelector` / `ObjectSelector` | Match clauses for subjects and objects in a `Policy` scope |
| `PolicyDecision` | The immutable audit record of an `/evaluate` call |
| `CapabilityToken` | A short-lived, signed access grant derived from a `PolicyDecision` |
| `Obligation` | An action that must be performed before (`pre`), after (`post`), or during (`runtime`) an operation |
| `Exception` | A time-limited exemption attached to a `Policy` |
| `PolicyBinding` | Associates a `Policy` with a `WorkflowSpec` or `SkillManifest` |

### Family 4 – Collaboration
Human feedback attached to any addressable object.

| Schema | Purpose |
|--------|---------|
| `Comment` | A free-text annotation on any object identified by a URN |
| `Rating` | A 1–5 integer rating on any object |
| `Community` | A named group of subject URNs |

### Family 5 – Models / Schemas
The logical view of data: types, constraints, tags, and quality.

| Schema | Purpose |
|--------|---------|
| `SchemaDefinition` | A named, versioned schema composed of `EntityField`s |
| `EntityField` | A field descriptor inside a `SchemaDefinition` |
| `Field` | A fully annotated, quality-profiled field attached to a live `Dataset` |
| `TagAssignment` | A classification tag with confidence, source, and review provenance |
| `ValidValues` | Enumeration, range, or regex constraint on a field |
| `QualityMetric` | A named quality dimension (completeness, validity, …) with a 0–1 score |
| `ProfileStats` | Statistical profile of a column (row count, nulls, distinct values, top-N) |

### Family 6 – Agreements
Legal and operational data-sharing agreements.

| Schema | Purpose |
|--------|---------|
| `Agreement` | A data-sharing agreement between one or more parties |
| `Party` | A named signatory (person, org, or service) with optional authority links |

### Execution / Provenance family
Tracks *what ran*, *with what inputs*, and *what was produced*.

| Schema | Purpose |
|--------|---------|
| `Dataset` | A logical view of a `PhysicalAsset` with governance and lifecycle metadata |
| `DataRef` | A typed pointer to a dataset, asset, stream topic, or file |
| `WorkloadSpec` | A container, Spark job, function, or stream processor to execute |
| `DataSphere` | A bounded execution environment with network and storage controls |
| `RunRecord` | The audit record of a single workload execution |
| `WorkflowSpec` | A directed acyclic graph of `WorkflowNode`s connected by `WorkflowEdge`s |
| `WorkflowNode` | A single node in a `WorkflowSpec`, wrapping a `WorkloadSpec` |
| `WorkflowEdge` | A directed edge between two `WorkflowNode` IDs |
| `Trigger` | How a workflow is activated: schedule (cron), event, or manual |
| `ProvenanceRecord` | A W3C PROV-compatible record linking a `RunRecord` to its input/output entities |
| `MappingSpec` | A field-to-field mapping with multi-method confidence evidence |
| `MappingEvidence` | A single piece of evidence for a `MappingSpec` (label similarity, value overlap, …) |
| `EventEnvelope` | The universal event wrapper for all AsyncAPI channel messages |

### Agent Plane family
Manages autonomous agent sessions and their decisions.

| Schema | Purpose |
|--------|---------|
| `AgentSession` | A single autonomous agent session with role, mode, substrate, and surface |
| `ExecutionSurface` | The sandboxing, network, and filesystem constraints of an agent's environment |
| `ExecutionDecision` | An immutable record of an agent's allow/deny/ask/defer/rewrite decision |
| `SkillManifest` | A declared skill with activation rules, requirements, and policy bindings |
| `MemoryEntry` | A persistent agent memory of kind `rule`, `learned`, or `recap` |
| `SessionReceipt` | The final outcome record for an `AgentSession` |
| `SessionReview` | A post-session learning review linking to extracted memory entries |
| `TelemetryEvent` | A structured log event from within an agent session |
| `FrustrationSignal` | A behavioural signal indicating agent or user difficulty |

### Release / Experiments family

| Schema | Purpose |
|--------|---------|
| `ExperimentFlag` | A feature flag with lifecycle states: off → shadow → internal → beta → on → retired |
| `RolloutPolicy` | Audience-based rollout rules for an `ExperimentFlag` |
| `ReleaseReceipt` | A verified release record with artifact hashes and gate results |

---

## 3 Governance lifecycle

A complete governance-gated data access follows this sequence:

```
User / Service
    │
    │  POST /v2/decisions/evaluate
    │  { subject, object, purpose }
    ▼
PolicyDecision  ──────────────► CapabilityToken  (POST /v2/tokens/issue)
    │
    │  obligations attached
    ▼
RunRecord  ──────────────────────────────────────► ProvenanceRecord
    │
    │  references CapabilityToken + PolicyDecision
    ▼
EventEnvelope  (srcos.v2.run.events)
```

1. The caller sends a policy evaluation request to `/v2/decisions/evaluate`.
2. The engine matches the request against all applicable `Policy` documents and returns a `PolicyDecision` (permit / deny / permitWithObligations).
3. If permitted, the caller calls `/v2/tokens/issue` to receive a `CapabilityToken` that is scoped to the approved datasets, fields, and operations.
4. The workload executes inside a `DataSphere`, referencing the `CapabilityToken`.
5. The `RunRecord` is stored at `/v2/runs` and a `ProvenanceRecord` at `/v2/provenance`.
6. Both events are published to the appropriate AsyncAPI channels.

---

## 4 URN identity scheme

Every top-level object carries a stable `id` field that is a URN of the form:

```
urn:srcos:<type-slug>:<local-id>
```

| Type | URN prefix | Example |
|------|-----------|---------|
| Connector | `urn:srcos:connector:` | `urn:srcos:connector:local_s3` |
| PhysicalAsset | `urn:srcos:asset:` | `urn:srcos:asset:lake_curated_health` |
| Dataset | `urn:srcos:dataset:` | `urn:srcos:dataset:health_obs` |
| Field | `urn:srcos:field:` | `urn:srcos:field:dob` |
| SchemaDefinition | `urn:srcos:schema:` | `urn:srcos:schema:health_obs_v1` |
| GlossaryTerm | `urn:srcos:glossary:` | `urn:srcos:glossary:dob` |
| Agreement | `urn:srcos:agreement:` | `urn:srcos:agreement:default` |
| Party | `urn:srcos:party:` | `urn:srcos:party:self` |
| Policy | `urn:srcos:policy:` | `urn:srcos:policy:export_health_restricted` |
| PolicyDecision | `urn:srcos:decision:` | `urn:srcos:decision:aa11bb22` |
| CapabilityToken | _(plain string `tokenId`)_ | `tok_123` |
| RunRecord | `urn:srcos:run:` | `urn:srcos:run:77cc88dd` |
| ProvenanceRecord | `urn:srcos:prov:` | `urn:srcos:prov:001` |
| WorkflowSpec | `urn:srcos:workflow:` | `urn:srcos:workflow:etl_v1` |
| WorkloadSpec | `urn:srcos:workload:` | `urn:srcos:workload:obfuscator_v1` |
| DataSphere | `urn:srcos:sphere:` | `urn:srcos:sphere:personal_curated` |
| MappingSpec | `urn:srcos:mapping:` | `urn:srcos:mapping:001` |
| Comment | `urn:srcos:comment:` | `urn:srcos:comment:001` |
| Rating | `urn:srcos:rating:` | `urn:srcos:rating:001` |
| Community | `urn:srcos:community:` | `urn:srcos:community:data-team` |
| EventEnvelope | `urn:srcos:event:` | `urn:srcos:event:001` |
| AgentSession | `urn:srcos:session:` | `urn:srcos:session:s001` |
| ExecutionDecision | `urn:srcos:exec-decision:` | `urn:srcos:exec-decision:ed001` |
| SkillManifest | `urn:srcos:skill:` | `urn:srcos:skill:pdf-reader` |
| MemoryEntry | `urn:srcos:memory:` | `urn:srcos:memory:m001` |
| SessionReceipt | `urn:srcos:receipt:session:` | `urn:srcos:receipt:session:r001` |
| SessionReview | `urn:srcos:session-review:` | `urn:srcos:session-review:sr001` |
| TelemetryEvent | `urn:srcos:telemetry:` | `urn:srcos:telemetry:t001` |
| FrustrationSignal | `urn:srcos:frustration:` | `urn:srcos:frustration:f001` |
| ExperimentFlag | `urn:srcos:flag:` | `urn:srcos:flag:new-ui` |
| RolloutPolicy | `urn:srcos:rollout:` | `urn:srcos:rollout:rp001` |
| ReleaseReceipt | `urn:srcos:release-receipt:` | `urn:srcos:release-receipt:v2.0.0` |

`local-id` is a URL-safe slug chosen by the producer.  It must be unique within its type namespace.

---

## 5 Patch-file composition model

The agent-plane functionality is delivered as two patch files rather than folded into the base specs.  This keeps the metadata-plane spec self-contained for implementations that do not need the agent plane.

At runtime, merge the patches into the base specs before serving or generating code:

```bash
# OpenAPI merge example (using openapi-merge-cli)
npx openapi-merge-cli \
  --config merge-config.yaml  # inputs: openapi.yaml + openapi.agent-plane.patch.yaml

# AsyncAPI merge (using asyncapi-bundler)
npx @asyncapi/bundler asyncapi.yaml asyncapi.agent-plane.patch.yaml -o asyncapi.merged.yaml
```

The patches are **additive only** — they never override or delete paths from the base spec.

---

## 6 Semantic overlay

`semantic/context.jsonld` provides a JSON-LD `@context` that maps schema type names to stable IRIs under `https://schemas.srcos.ai/v2/`.

`semantic/hydra.jsonld` provides a `hydra:ApiDocumentation` fragment that can be merged with the JSON-LD context to make the REST API self-describing.

See [semantic/README.md](semantic/README.md) for usage details.
