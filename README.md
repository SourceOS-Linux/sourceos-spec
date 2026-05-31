# SourceOS/SociOS Typed Contracts

**SourceOS/SociOS Typed Contracts** is the canonical, machine-readable specification for the SourceOS metadata governance platform and the SociOS agent plane. It defines the full set of JSON Schemas, additive OpenAPI / AsyncAPI patch fragments, and a JSON-LD / Hydra semantic overlay that together make up the "contract layer" every implementation component must satisfy.

> **Spec version:** `2.0.0` &nbsp;|&nbsp; **License:** see [LICENSE](LICENSE)

---

## Why this repository exists

A metadata governance platform can only unify data meaning, policy, provenance, and agent execution if every component agrees on the *shape* of the objects it exchanges. This repository is that shared agreement. Downstream consumers include:

- **API services** — scaffolded from `openapi.yaml` plus additive patch fragments such as `openapi.agent-plane.patch.yaml` and `openapi.fog.patch.yaml`.
- **Event consumers** — Kafka topics declared in `asyncapi.yaml` plus additive channel fragments such as `asyncapi.agent-plane.patch.yaml` and `asyncapi.fog.patch.yaml`.
- **Validators** — AJV (Node.js) or `jsonschema` (Python) loaded from `schemas/`.
- **Code generators** — TypeScript types via [quicktype](https://quicktype.io); Python models via [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator).
- **Semantic tooling** — JSON-LD context + Hydra API documentation in `semantic/`, including additive vocabulary seeds such as `semantic/fog-vocabulary.jsonld`.
- **SVF workspace discovery** — SourceOS contract validation Plans declared in `svf/` for Sociosphere selection and advisory validation routing.

---

## Repository layout

```text
sourceos-spec/
├── README.md                         # This file
├── ARCHITECTURE.md                   # Two-plane architecture, schema families, lifecycle
├── CONTRIBUTING.md                   # How to add / modify schemas and API specs
├── CHANGELOG.md                      # Spec version history
├── LICENSE
│
├── openapi.yaml                      # Metadata-plane REST API (v2)
├── openapi.agent-plane.patch.yaml    # Additive agent-plane REST endpoints
├── openapi.fog.patch.yaml            # Additive fog-layer REST endpoints
├── asyncapi.yaml                     # Metadata-plane event channels
├── asyncapi.agent-plane.patch.yaml   # Agent-plane event channels
├── asyncapi.fog.patch.yaml           # Fog-layer event channels
│
├── schemas/                          # Top-level JSON Schema files (draft 2020-12)
│   └── README.md                     # Schema catalog and URN patterns
│
├── examples/                         # Conforming example payloads (one per type)
│   └── README.md
│
├── semantic/                         # JSON-LD context + Hydra API documentation
│   ├── README.md
│   └── fog-vocabulary.jsonld         # Additive fog vocabulary seed
│
├── svf/                              # Sovereign Validation Fabric contract declarations
│   └── sourceos-contract-validation-basic.json
│
└── docs/
    ├── architecture/                 # Architecture specs and system models
    ├── security/                     # Threat models and security requirements
    ├── specs/                        # Contract-level specs outside schema files
    ├── integration/                  # Cross-repository estate integration maps
    ├── adr/                          # Architecture Decision Records
    ├── contract-additions/           # Discoverability notes for additive families
    └── SVF-OS-VALIDATION-PROFILES.md # SVF OS validation profile doctrine
```

---

## Agentic graph foundation

The local-first agentic graph foundation extends the existing contract layer so SourceOS and SociOS components share one governed model for workspace state, sync, agents, memory, policy, terminals, browsers, relays, and audit.

Start here:

- [Local-First Agentic Graph Architecture](docs/architecture/local-first-agentic-graph.md)
- [Agentic Sync Threat Model](docs/security/agentic-sync-threat-model.md)
- [Sync Engine Registry Specification](docs/specs/sync-engine-registry.md)
- [SourceChannel Bridge Contract](docs/specs/sourcechannel.md)
- [Estate Integration Repo Map](docs/integration/repo-map.md)
- [SVF OS Validation Profiles](docs/SVF-OS-VALIDATION-PROFILES.md)

New machine-readable contracts:

- `schemas/SourceOSRepoManifest.json`
- `schemas/SyncEngineManifest.json`
- `schemas/SourceChannelEnvelope.json`
- `schemas/SourceGraphWrite.json`
- `schemas/AgentCapabilityLease.json`
- `schemas/AuditEvent.json`
- `svf/sourceos-contract-validation-basic.json`

---

## SourceOS interaction substrate

The SourceOS interaction substrate defines the governed noetic/chat/task event path shared by Noetica, AgentTerm, Superconscious, and AgentPlane.

Start here:

- [SourceOS Interaction Substrate Catalog](docs/contract-additions/sourceos-interaction-catalog.md)
- [SourceOS Interaction Reference Flow](docs/contract-additions/sourceos-interaction-reference-flow.md)
- [SourceOS Interaction Top-Level Index](docs/contract-additions/sourceos-interaction-top-level-index.md)
- `schemas/SourceOSInteractionEvent.json`
- `examples/interaction-flow/noetica-superconscious-agentplane-agentterm.flow.json`

Validate locally:

```bash
python tools/validate_sourceos_interaction_examples.py
python tools/generate_sourceos_interaction_types.py --check
python tools/validate_interaction_flow_reference.py
```

---

## Schema families

The schemas are organised into domain-oriented families that map to the SourceOS / SociOS contract surface:

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
| + | **Fog Layer** | `Topic`, `TopicEnvelope`, `ReplicationPolicy`, `ContentRef`, `Offer`, `WorkOrder`, `UsageReceipt`, `SettlementEvent` |
| + | **Agentic Graph Foundation** | `SourceOSRepoManifest`, `SyncEngineManifest`, `SourceChannelEnvelope`, `SourceGraphWrite`, `AgentCapabilityLease`, `AuditEvent` |
| + | **Interaction Substrate** | `SourceOSInteractionEvent` |

---

## SVF validation lane

The SourceOS SVF lane declares advisory validation over the existing SourceOS contract/example checks. It does not build an OS image, validate bootability, sign artifacts, publish releases, deploy updates, or certify hardware compatibility.

Validate locally:

```bash
make validate-svf-contracts
```

`make validate` includes this lane.

Relevant files:

- `docs/SVF-OS-VALIDATION-PROFILES.md`
- `svf/sourceos-contract-validation-basic.json`
- `tools/validate_svf_contracts.py`

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
