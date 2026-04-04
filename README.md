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
