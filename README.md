# SourceOS/SociOS Typed Contracts Starter Kit (v2)

This revision closes the biggest implementability gaps from v1:
- Adds Agreement + Glossary + Connector/Asset + SchemaDefinition + Provenance + Collaboration objects
- Upgrades policy conditions to a typed `PolicyCondition` with a declared language (jsonlogic/cel/rego/cedar)
- Adds a minimal Hydra/JSON-LD semantic overlay (semantic/context.jsonld + semantic/hydra.jsonld)
- Upgrades Dataset to reference Asset + Schema + Agreements explicitly (no implicit physical fields)

## Topology position

- **Role:** canonical typed-contract, JSON-LD, and shared vocabulary lane for SourceOS / AgentOS.
- **Connects to:**
  - `SociOS-Linux/agentos-spine` — Linux-side integration/workspace spine that consumes and routes these contracts
  - `SociOS-Linux/workstation-contracts` — workstation/CI specialization and conformance lane
  - `SociOS-Linux/SourceOS` — immutable substrate that should consume typed policy and artifact semantics
  - `SociOS-Linux/socios` — opt-in automation layer that should reference, not redefine, these contracts
  - `SocioProphet/sociosphere` — platform workspace controller that may mirror or reuse shared contract vocabulary
  - `SocioProphet/socioprophet` and `SociOS-Linux/socioslinux-web` — public documentation surfaces that explain these contracts downstream
- **Not this repo:**
  - workspace controller
  - image builder
  - public docs site
  - opt-in automation plane
- **Semantic direction:** this repo should become the canonical home for shared repo ontology, JSON-LD contexts, and vocabulary definitions that other repos publish by reference.

## Why this matters
If a contract bundle does not cover agreements, glossary, and asset connectors, the metadata plane cannot unify governance and meaning end-to-end.
We now have a closed set of object families that directly correspond to the Open Metadata Types taxonomy areas:
- Area 1: Physical assets -> Connector, PhysicalAsset
- Area 2: Glossary -> GlossaryTerm
- Area 3: Governance -> Policy/Decision/Token/Obligations
- Area 4: Collaboration -> Comment/Rating/Community
- Area 5: Models/Schemas -> SchemaDefinition, EntityField, ValidValues
- Area 6: Agreements -> Agreement, Party

## Minimal implementation path (practical)
1) Schema validation: AJV (Node) or jsonschema (Python).
2) Codegen: TypeScript types (quicktype) or Python models (datamodel-code-generator for Pydantic).
3) API service: OpenAPI -> FastAPI scaffold.
4) Event spine: AsyncAPI -> Kafka topics with schema validation at the producer/consumer boundaries.

## Compatibility discipline
- IDs are stable URNs; specVersion is semver.
- Additive changes should remain backward compatible; breaking changes increment major.
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

