# Examples

This directory contains one conforming JSON example payload for each top-level schema type in the SourceOS/SociOS specification.

---

## What the examples show

The examples are designed to tell a coherent end-to-end story: a personal health dataset is catalogued, governed, transformed by an obfuscation workload, and released — all within an agent session. They share cross-reference URNs so you can trace the full lifecycle:

```text
connector.json       ──► asset.json
                              │
                              ▼
                          dataset.json  ──► schema.json
                              │               │
                              │               ▼
                              │            field.json
                              │
                          policy.json
                              │
                              ▼
                          policy_decision.json  ──► capability_token.json
                              │
                              ▼
                           run.json  ──► provenance.json
                              │
                              ▼
                           event_envelope.json

glossary.json  ◄──  field.json (glossaryTerms)
mapping.json   ──►  dataset.json (from/to)
comment.json   ──►  mapping.json (targetId)
agreement.json ◄──  dataset.json (governance.agreements)

agent_session.json  ──►  execution_decision.json  ──►  session_receipt.json
                                                          │
                                                          ▼
                                                   session_review.json
```

---

## Recent additions — Fog Layer examples

The fog example set illustrates the new FogVault / FogCompute contract family:

| File | Schema type | Description |
|------|------------|-------------|
| `content_ref.json` | ContentRef | Content-addressed reference for fog blobs / manifests |
| `topic.json` | Topic | FogVault topic definition with replication and encryption metadata |
| `topic_envelope.json` | TopicEnvelope | Append-only topic entry envelope with integrity and encryption metadata |
| `replication_policy.json` | ReplicationPolicy | Replica / ack / retention / compaction policy example |
| `offer.json` | Offer | FogCompute provider offer advertising local resources |
| `workorder.json` | WorkOrder | FogCompute request with image, inputs, outputs, and verification mode |
| `usage_receipt.json` | UsageReceipt | Worker-emitted execution receipt with metered resource usage |
| `settlement_event.json` | SettlementEvent | Optional mapping from receipt to settlement backend / credits |

---

## File index

| File | Schema type | Description |
|------|------------|-------------|
| `agreement.json` | Agreement | Default personal-data agreement |
| `agent_session.json` | AgentSession | An executor session running the obfuscation workflow |
| `asset.json` | PhysicalAsset | Lakehouse asset for curated health observations |
| `capability_token.json` | CapabilityToken | Access token scoped to the health dataset export operation |
| `comment.json` | Comment | A review note on a field mapping |
| `community.json` | Community | The data-governance team community |
| `connector.json` | Connector | A local S3 connector |
| `content_ref.json` | ContentRef | Content-addressed reference for fog blobs / manifests |
| `dataset.json` | Dataset | Personal health observations dataset |
| `data_sphere.json` | DataSphere | The personal-curated execution environment |
| `execution_decision.json` | ExecutionDecision | Agent allow-decision for a tool invocation |
| `event_envelope.json` | EventEnvelope | Event published when the run completes |
| `experiment_flag.json` | ExperimentFlag | A feature flag for the new obfuscation algorithm |
| `field.json` | Field | The `patient.dateOfBirth` field with PII tags and quality metrics |
| `frustration_signal.json` | FrustrationSignal | A frustration signal from a repeated-failure condition |
| `glossary.json` | GlossaryTerm | Glossary term for "Date of Birth" |
| `mapping.json` | MappingSpec | A field mapping between two dataset fields |
| `memory_entry.json` | MemoryEntry | A learned memory entry from an agent session |
| `offer.json` | Offer | FogCompute provider offer |
| `policy.json` | Policy | Health export must be obfuscated |
| `policy_decision.json` | PolicyDecision | An `export` permit decision with an obfuscation obligation |
| `provenance.json` | ProvenanceRecord | Provenance record for the obfuscation run |
| `rating.json` | Rating | A 5-star rating on the health observations dataset |
| `release_receipt.json` | ReleaseReceipt | Release receipt for spec version 2.0.0 |
| `replication_policy.json` | ReplicationPolicy | Fog topic replication/retention policy example |
| `rollout_policy.json` | RolloutPolicy | Rollout rules for the obfuscation experiment flag |
| `run.json` | RunRecord | The obfuscation workload run record |
| `schema.json` | SchemaDefinition | The schema for health observations |
| `session_receipt.json` | SessionReceipt | Receipt for the completed agent session |
| `session_review.json` | SessionReview | Post-session learning review |
| `settlement_event.json` | SettlementEvent | Optional receipt-to-settlement mapping |
| `skill_manifest.json` | SkillManifest | The obfuscation skill manifest |
| `telemetry_event.json` | TelemetryEvent | An informational telemetry event from the agent session |
| `topic.json` | Topic | FogVault topic definition |
| `topic_envelope.json` | TopicEnvelope | FogVault append-only entry envelope |
| `workflow_spec.json` | WorkflowSpec | The health-data obfuscation workflow |
| `workorder.json` | WorkOrder | FogCompute work order |
| `usage_receipt.json` | UsageReceipt | FogCompute execution receipt |

---

## Validating examples

```bash
# Install AJV CLI
npm install -g ajv-cli

# Validate a single example
ajv validate -s ../schemas/Dataset.json -d dataset.json

# Validate all examples
cd ..
for example in examples/*.json; do
  name=$(basename "$example" .json)
  python3 - <<EOF
import json
ex = json.load(open("$example"))
t = ex.get("type") or ex.get("title")
if t:
    print(f"schemas/{t}.json")
EOF
done
```

---

## Adding a new example

See [CONTRIBUTING.md](../CONTRIBUTING.md#writing-examples) for the full guide. Key rules:
1. The filename should match the schema title in the repository’s naming convention.
2. All required fields must be present and valid.
3. Use coherent cross-reference URNs where possible so the example set stays navigable.
4. Run `ajv validate` before committing.
