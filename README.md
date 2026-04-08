# SourceOS/SociOS Typed Contracts Specification (v2)

A machine-readable, implementation-ready specification for the SourceOS/SociOS platform's metadata plane and agent plane. The spec defines the full set of typed objects, REST API contracts, event-spine channels, and semantic overlays needed to govern, catalogue, and trace data assets and agentic workloads end-to-end.

## Contents

- [Why this exists](#why-this-exists)
- [Repository layout](#repository-layout)
- [Architecture overview](#architecture-overview)
- [Schema families](#schema-families)
- [Implementation path](#implementation-path)
- [Compatibility discipline](#compatibility-discipline)
- [Validation](#validation)
- [Contributing](#contributing)

---

## Why this exists

If a contract bundle does not cover agreements, glossary, physical assets, agent sessions, and execution decisions, the metadata plane cannot unify governance and meaning end-to-end. This specification closes that gap with a closed set of object families that map directly to the Open Metadata Types taxonomy:

| Area | Schema families |
|------|-----------------|
| Area 1 — Physical assets | `Connector`, `PhysicalAsset` |
| Area 2 — Glossary | `GlossaryTerm`, `AuthorityLink` |
| Area 3 — Governance | `Policy`, `Rule`, `PolicyCondition`, `PolicyDecision`, `CapabilityToken`, `Obligation`, `Exception` |
| Area 4 — Collaboration | `Comment`, `Rating`, `Community` |
| Area 5 — Models/Schemas | `SchemaDefinition`, `EntityField`, `ValidValues`, `Field`, `MappingSpec`, `MappingEvidence` |
| Area 6 — Agreements | `Agreement`, `Party` |
| Area 7 — Lineage | `RunRecord`, `ProvenanceRecord`, `WorkflowSpec`, `WorkflowNode`, `WorkflowEdge`, `WorkloadSpec`, `DataRef`, `DataSphere` |
| Area 8 — Agent Plane | `AgentSession`, `ExecutionDecision`, `ExecutionSurface`, `SkillManifest`, `MemoryEntry`, `SessionReceipt`, `SessionReview`, `TelemetryEvent`, `FrustrationSignal` |
| Cross-cutting | `EventEnvelope`, `TagAssignment`, `ExperimentFlag`, `RolloutPolicy`, `ReleaseReceipt`, `Link`, `ProfileStats`, `QualityMetric` |

---

## Repository layout

```
sourceos-spec/
├── README.md                          # This file
├── CONTRIBUTING.md                    # How to contribute
├── CHANGELOG.md                       # Version history
├── LICENSE                            # MIT licence
│
├── schemas/                           # 54 JSON Schema (draft 2020-12) files
│   ├── README.md                      # Per-family schema documentation
│   ├── AgentSession.json
│   ├── Agreement.json
│   └── ...                            # (all other schemas)
│
├── examples/                          # Concrete JSON example payloads (one per schema)
│   ├── agreement.json
│   ├── agent_session.json
│   └── ...
│
├── openapi.yaml                       # OpenAPI 3.0.3 — Metadata Plane endpoints
├── openapi.agent-plane.patch.yaml     # Additive OpenAPI patch — Agent Plane endpoints
├── asyncapi.yaml                      # AsyncAPI 2.6.0 — Metadata Plane event channels
├── asyncapi.agent-plane.patch.yaml    # Additive AsyncAPI patch — Agent Plane channels
│
├── semantic/
│   ├── context.jsonld                 # JSON-LD @context mapping all 54 schema types
│   └── hydra.jsonld                   # Hydra API documentation overlay
│
└── docs/
    └── adr/                           # Architecture Decision Records
        ├── 0001-json-schema-draft-2020-12.md
        ├── 0002-urn-id-scheme.md
        ├── 0003-generic-event-envelope.md
        ├── 0004-multi-language-policy-conditions.md
        └── 0005-additive-patch-pattern.md
```

---

## Architecture overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                        SourceOS Platform                             │
│                                                                      │
│  ┌─────────────────────────┐   ┌──────────────────────────────────┐  │
│  │     Metadata Plane      │   │          Agent Plane             │  │
│  │                         │   │                                  │  │
│  │  Datasets ──► Fields    │   │  AgentSession                    │  │
│  │  PhysicalAssets         │   │  ExecutionDecision               │  │
│  │  Connectors             │   │  SkillManifest                   │  │
│  │  Schemas ──► EntityField│   │  MemoryEntry                     │  │
│  │  GlossaryTerms          │   │  SessionReceipt                  │  │
│  │  Agreements             │   │  TelemetryEvent                  │  │
│  │  Policies ──► Decisions │   │  FrustrationSignal               │  │
│  │  CapabilityTokens       │   │                                  │  │
│  │  MappingSpecs           │   └─────────────┬────────────────────┘  │
│  │  WorkflowSpecs          │                 │                       │
│  │  RunRecords             │◄────────────────┘  (agent calls API)    │
│  │  ProvenanceRecords      │                                         │
│  │  Comments / Ratings     │                                         │
│  └───────────┬─────────────┘                                         │
│              │                                                       │
│              ▼                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                     Event Spine (Kafka)                         │ │
│  │  srcos.v2.dataset.events  srcos.v2.session.events  ...          │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

All objects share a common envelope:

```json
{
  "id":          "urn:srcos:<family>:<id>",
  "type":        "<SchemaName>",
  "specVersion": "2.0.0"
}
```

IDs are stable URNs. The `specVersion` field follows semver and controls compatibility guarantees (see [Compatibility discipline](#compatibility-discipline)).

---

## Schema families

See [`schemas/README.md`](./schemas/README.md) for the full per-family documentation including URN patterns, required fields, and cross-references.

---

## Implementation path

### 1. Schema validation
```bash
# Node.js (AJV)
npm install ajv ajv-formats
node -e "
const Ajv = require('ajv');
const schema = require('./schemas/Dataset.json');
const example = require('./examples/dataset.json');
const ajv = new Ajv({ strict: false });
const validate = ajv.compile(schema);
console.log(validate(example) ? 'valid' : validate.errors);
"

# Python (jsonschema)
pip install jsonschema
python -c "
import json, jsonschema
schema = json.load(open('schemas/Dataset.json'))
example = json.load(open('examples/dataset.json'))
jsonschema.validate(example, schema)
print('valid')
"
```

### 2. Code generation
```bash
# TypeScript types (quicktype)
npx quicktype --src schemas/Dataset.json --lang typescript --out src/types/Dataset.ts

# Python Pydantic models (datamodel-code-generator)
pip install datamodel-code-generator
datamodel-codegen --input schemas/Dataset.json --output models/dataset.py
```

### 3. API scaffolding
```bash
# FastAPI (openapi-python-client)
pip install openapi-python-client
openapi-python-client generate --path openapi.yaml

# Node/Express (openapi-generator)
npx @openapitools/openapi-generator-cli generate \
  -i openapi.yaml -g nodejs-express-server -o server/
```

### 4. Event spine
```bash
# Kafka topic setup (one topic per channel)
# See asyncapi.yaml for the full channel list
kafka-topics.sh --create --topic srcos.v2.dataset.events --partitions 3
kafka-topics.sh --create --topic srcos.v2.policy.events --partitions 3
# ...

# Validate event payloads against EventEnvelope.json at producer/consumer boundaries
```

---

## Compatibility discipline

| Change type | Version bump | Notes |
|---|---|---|
| Add optional property | Patch (`2.0.x`) | Existing records remain valid |
| Add required property | Major (`3.0.0`) | Breaking; increment `specVersion` on all records |
| Add new schema | Minor (`2.x.0`) | Backward compatible |
| Add enum value | Minor (`2.x.0`) | Consumers must handle unknown enum values |
| Remove/rename property | Major (`3.0.0`) | Breaking |
| Remove/rename schema | Major (`3.0.0`) | Breaking |

- All IDs are stable URNs and must never be reused.
- `specVersion` in each record must match the spec version it was written against.
- The agent-plane patch files (`*.agent-plane.patch.yaml`) are additive overlays and follow the same semver rules independently.

---

## Validation

A GitHub Actions workflow (`.github/workflows/validate.yml`) runs on every pull request and verifies:

1. All JSON schema files are syntactically valid.
2. All files in `examples/` validate against their corresponding schema.
3. `openapi.yaml` parses as valid OpenAPI 3.0.x.
4. `asyncapi.yaml` parses as valid AsyncAPI 2.x.

Run locally with:
```bash
# Install dependencies
npm install -g @stoplight/spectral-cli ajv-cli @asyncapi/cli

# Schema lint
spectral lint openapi.yaml

# Example validation (all examples against their schemas)
for f in examples/*.json; do
  type=$(jq -r '.type // empty' "$f")
  [ -n "$type" ] && ajv validate -s "schemas/${type}.json" -d "$f" && echo "$f: ok"
done
```

---

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for:
- How to propose new schemas or modify existing ones
- The review and merge process
- Schema design conventions (naming, URN patterns, `additionalProperties: false`)
- How to add examples and keep them in sync with schema changes

