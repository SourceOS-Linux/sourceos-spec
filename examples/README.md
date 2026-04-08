# Examples

This directory contains one conforming JSON example payload for each top-level schema type in the SourceOS/SociOS specification.

---

## What the examples show

The examples are designed to tell a coherent end-to-end story: a personal health dataset is catalogued, governed, transformed by an obfuscation workload, and released — all within an agent session.  They share cross-reference URNs so you can trace the full lifecycle:

```
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
| `dataset.json` | Dataset | Personal health observations dataset |
| `data_sphere.json` | DataSphere | The personal-curated execution environment |
| `policy_decision.json` | PolicyDecision | An `export` permit decision with an obfuscation obligation |
| `execution_decision.json` | ExecutionDecision | Agent allow-decision for a tool invocation |
| `experiment_flag.json` | ExperimentFlag | A feature flag for the new obfuscation algorithm |
| `event_envelope.json` | EventEnvelope | Event published when the run completes |
| `field.json` | Field | The `patient.dateOfBirth` field with PII tags and quality metrics |
| `frustration_signal.json` | FrustrationSignal | A frustration signal from a repeated-failure condition |
| `glossary.json` | GlossaryTerm | Glossary term for "Date of Birth" |
| `mapping.json` | MappingSpec | A field mapping between two dataset fields |
| `memory_entry.json` | MemoryEntry | A learned memory entry from an agent session |
| `policy.json` | Policy | Health export must be obfuscated |
| `provenance.json` | ProvenanceRecord | Provenance record for the obfuscation run |
| `rating.json` | Rating | A 5-star rating on the health observations dataset |
| `release_receipt.json` | ReleaseReceipt | Release receipt for spec version 2.0.0 |
| `rollout_policy.json` | RolloutPolicy | Rollout rules for the obfuscation experiment flag |
| `run.json` | RunRecord | The obfuscation workload run record |
| `schema.json` | SchemaDefinition | The schema for health observations |
| `session_receipt.json` | SessionReceipt | Receipt for the completed agent session |
| `session_review.json` | SessionReview | Post-session learning review |
| `skill_manifest.json` | SkillManifest | The obfuscation skill manifest |
| `telemetry_event.json` | TelemetryEvent | An informational telemetry event from the agent session |
| `capability_token.json` | CapabilityToken | Capability token for the export operation |
| `workflow_spec.json` | WorkflowSpec | The health-data obfuscation workflow |

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
  # Find matching schema (PascalCase title)
  python3 - <<EOF
import json, sys, glob
ex = json.load(open("$example"))
t = ex.get("type") or ex.get("title")
if t:
    f = f"schemas/{t}.json"
    print(f)
EOF
done
```

---

## Adding a new example

See [CONTRIBUTING.md](../CONTRIBUTING.md#writing-examples) for the full guide.  Key rules:
1. The filename must be the schema `title` lowercased, e.g. `AgentSession` → `agent_session.json`.
2. All required fields must be present and valid.
3. Use existing cross-reference URNs from this directory so the example set stays coherent.
4. Run `ajv validate` before committing.
