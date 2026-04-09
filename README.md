# SourceOS/SociOS Typed Contracts

**SourceOS/SociOS Typed Contracts** is the canonical, machine-readable specification for the SourceOS metadata governance platform and the SociOS agent plane. It defines the full set of JSON Schemas, an OpenAPI REST surface, an AsyncAPI event spine, and a JSON-LD / Hydra semantic overlay that together make up the "contract layer" every implementation component must satisfy.

> **Spec version:** `2.0.0` &nbsp;|&nbsp; **License:** see [LICENSE](LICENSE)

---

## Why this repository exists

A metadata governance platform can only unify data meaning, policy, provenance, and agent execution if every component agrees on the *shape* of the objects it exchanges.  This repository is that shared agreement.  Downstream consumers include:

- **API services** — scaffolded from `openapi.yaml` (metadata plane) and `openapi.agent-plane.patch.yaml` (agent plane).
- **Event consumers** — Kafka topics declared in `asyncapi.yaml` + `asyncapi.agent-plane.patch.yaml`.
- **Validators** — AJV (Node.js) or `jsonschema` (Python) loaded from `schemas/`.
- **Code generators** — TypeScript types via [quicktype](https://quicktype.io); Python models via [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator).
- **Semantic tooling** — JSON-LD context + Hydra API documentation in `semantic/`.

---

## Repository layout

```
sourceos-spec/
├── README.md                         # This file
├── ARCHITECTURE.md                   # Two-plane architecture, schema families, lifecycle
├── CONTRIBUTING.md                   # How to add / modify schemas and API specs
├── CHANGELOG.md                      # Spec version history
├── LICENSE
│
├── openapi.yaml                      # Metadata-plane REST API (v2)
├── openapi.agent-plane.patch.yaml    # Additive agent-plane REST endpoints
├── asyncapi.yaml                     # Metadata-plane event channels
├── asyncapi.agent-plane.patch.yaml   # Agent-plane event channels
│
├── schemas/                          # 54 JSON Schema (draft 2020-12) files
│   └── README.md                     # Schema catalog and URN patterns
│
├── examples/                         # Conforming example payloads (one per type)
│   └── README.md
│
├── semantic/                         # JSON-LD context + Hydra API documentation
│   └── README.md
│
└── docs/
    └── adr/                          # Architecture Decision Records
```

---

## Schema families

The 54 schemas are organised into six families that map directly to the Open Metadata Types taxonomy areas:

| # | Family | Key schemas |
|---|--------|-------------|
| 1 | **Physical Assets** | `Connector`, `PhysicalAsset` |
| 2 | **Glossary** | `GlossaryTerm`, `AuthorityLink` |
| 3 | **Governance** | `Policy`, `Rule`, `PolicyCondition`, `PolicyDecision`, `CapabilityToken`, `Obligation`, `Exception` |
| 4 | **Collaboration** | `Comment`, `Rating`, `Community` |
| 5 | **Models / Schemas** | `SchemaDefinition`, `EntityField`, `Field`, `ValidValues`, `TagAssignment`, `QualityMetric`, `ProfileStats` |
| 6 | **Agreements** | `Agreement`, `Party` |
| + | **Execution / Provenance** | `Dataset`, `RunRecord`, `WorkflowSpec`, `WorkflowNode`, `WorkflowEdge`, `WorkloadSpec`, `DataSphere`, `ProvenanceRecord`, `EventEnvelope`, `MappingSpec` |
| + | **Agent Plane** | `AgentSession`, `ExecutionDecision`, `ExecutionSurface`, `SkillManifest`, `MemoryEntry`, `SessionReceipt`, `SessionReview`, `TelemetryEvent`, `FrustrationSignal` |
| + | **Release / Experiments** | `ExperimentFlag`, `RolloutPolicy`, `ReleaseReceipt` |

---

## Quick start

### 1 — Validate a payload against a schema

```bash
# Node.js (AJV)
npm install ajv ajv-formats
node -e "
const Ajv = require('ajv/dist/2020');
const addFormats = require('ajv-formats');
const schema = require('./schemas/Dataset.json');
const example = require('./examples/dataset.json');
const ajv = new Ajv(); addFormats(ajv);
const valid = ajv.validate(schema, example);
console.log(valid ? 'VALID' : ajv.errorsText());
"

# Python (jsonschema)
pip install jsonschema
python -c "
import json, jsonschema
schema = json.load(open('schemas/Dataset.json'))
example = json.load(open('examples/dataset.json'))
jsonschema.validate(example, schema)
print('VALID')
"
```

### 2 — Generate TypeScript types

```bash
npm install -g quicktype
quicktype --src schemas/ --src-lang schema --lang typescript --out src/types/srcos.ts
```

### 3 — Generate Python Pydantic models

```bash
pip install datamodel-code-generator
datamodel-codegen --input schemas/ --input-file-type jsonschema --output models/
```

### 4 — Generate a FastAPI stub from the OpenAPI spec

```bash
pip install fastapi-code-generator
fastapi-codegen --input openapi.yaml --output app/
```

---

## Compatibility discipline

- **IDs** are stable URNs of the form `urn:srcos:<type>:<slug>`.
- **`specVersion`** follows [Semantic Versioning](https://semver.org/): additive changes are minor bumps; breaking changes increment the major version.
- All breaking changes are recorded in [CHANGELOG.md](CHANGELOG.md) and accompanied by an ADR in [docs/adr/](docs/adr/).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for schema authoring conventions, the URN naming guide, and the pull-request checklist.

