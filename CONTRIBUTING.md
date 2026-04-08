# Contributing to SourceOS/SociOS Typed Contracts

Thank you for contributing to the spec!  This guide covers the conventions you must follow so that every schema remains machine-readable, internally consistent, and backward-compatible.

---

## Table of contents

1. [Pre-requisites](#pre-requisites)
2. [Repository structure recap](#repository-structure-recap)
3. [Adding a new schema](#adding-a-new-schema)
4. [Modifying an existing schema](#modifying-an-existing-schema)
5. [URN naming guide](#urn-naming-guide)
6. [Updating the API specs](#updating-the-api-specs)
7. [Writing examples](#writing-examples)
8. [Pull-request checklist](#pull-request-checklist)
9. [Breaking vs additive changes](#breaking-vs-additive-changes)

---

## Pre-requisites

```bash
# Validate schemas and examples with AJV (Node ≥ 18)
npm install -g ajv-cli

# Validate OpenAPI spec
npm install -g @stoplight/spectral-cli

# Validate AsyncAPI spec
npm install -g @asyncapi/cli
```

---

## Repository structure recap

```
schemas/          JSON Schema (draft 2020-12) — one file per type
examples/         One conforming example JSON per schema type
openapi.yaml      Metadata-plane REST API
openapi.agent-plane.patch.yaml   Agent-plane additive REST patch
asyncapi.yaml     Metadata-plane event channels
asyncapi.agent-plane.patch.yaml  Agent-plane additive event channels
semantic/         JSON-LD context + Hydra API documentation
docs/adr/         Architecture Decision Records
```

---

## Adding a new schema

### 1 Create the schema file

Save it to `schemas/<TypeName>.json`.  The filename must be `PascalCase` and match the `title` field exactly.

**Required top-level fields:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.srcos.ai/v2/<TypeName>.json",
  "title": "<TypeName>",
  "description": "One-sentence description of what this object represents.",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "type", "specVersion", ...],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^urn:srcos:<type-slug>:",
      "description": "Stable URN identifier. Pattern: urn:srcos:<type-slug>:<local-id>"
    },
    "type": {
      "const": "<TypeName>",
      "description": "Discriminator constant — always \"<TypeName>\"."
    },
    "specVersion": {
      "type": "string",
      "description": "Spec version of this document, e.g. \"2.0.0\"."
    }
  }
}
```

**Rules:**
- Every property **must** have a `"description"` field (or a `$ref` that resolves to a described type).
- `"additionalProperties": false` is required on every object.
- Nullable fields use `"type": ["<base-type>", "null"]`.
- Timestamps use `"type": "string", "format": "date-time"`.
- All cross-object references use a URN `"pattern"` constraint that matches the target type's URN prefix.

### 2 Add the schema to the appropriate family

Update `schemas/README.md` — add a row to the correct family table.

### 3 Add a conforming example

Create `examples/<typename>.json` (lowercase filename).  The example must validate against the schema:

```bash
ajv validate -s schemas/<TypeName>.json -d examples/<typename>.json
```

### 4 Expose the type in the OpenAPI spec

Add a `POST /v2/<plural-path>` operation to `openapi.yaml` (metadata-plane types) or `openapi.agent-plane.patch.yaml` (agent-plane types).  Every operation **must** include `summary`, `description`, `tags`, and at minimum `200`, `400`, and `422` responses.

### 5 Add an AsyncAPI channel (if the type generates events)

Add the channel to `asyncapi.yaml` or `asyncapi.agent-plane.patch.yaml`.  Include a `description` on both the channel and the message.

### 6 Update the semantic context (if needed)

If the new type is a first-class domain concept (not a supporting sub-type), add it to `semantic/context.jsonld` and add a `hydra:supportedClass` entry to `semantic/hydra.jsonld`.

### 7 Write an ADR (if the design involves a non-obvious choice)

Create `docs/adr/NNN-<short-title>.md` using the template at `docs/adr/0000-template.md`.

---

## Modifying an existing schema

| Change type | Allowed? | Notes |
|-------------|----------|-------|
| Add optional property | ✅ Minor bump | Existing documents remain valid |
| Add required property | ⚠️ Major bump | Existing documents become invalid — must bump `specVersion` major and log in `CHANGELOG.md` + ADR |
| Remove property | ⚠️ Major bump | Same as above |
| Narrow a type (e.g. `string` → `enum`) | ⚠️ Major bump | |
| Widen a type (e.g. add enum value) | ✅ Minor bump | |
| Fix a `pattern` bug | ✅ Patch bump | |
| Change a `description` | ✅ No version bump | |

---

## URN naming guide

All stable identifiers follow the scheme `urn:srcos:<type-slug>:<local-id>`.

- **`type-slug`** is lowercase, hyphen-separated, and maps one-to-one to a schema title (see the full table in [ARCHITECTURE.md](ARCHITECTURE.md#4-urn-identity-scheme)).
- **`local-id`** is a URL-safe slug chosen by the producer.  It must be unique within the type namespace.  Recommended format: `[a-z0-9][a-z0-9_-]*`.
- Use existing URN prefixes — do **not** invent new slugs without updating `ARCHITECTURE.md` and this guide.

---

## Updating the API specs

- `openapi.yaml` and `openapi.agent-plane.patch.yaml` follow OpenAPI 3.0.3.
- All operations must have: `operationId` (camelCase verb + noun), `summary` (≤ 10 words), `description`, at least one `tags` entry, and response codes `200`, `400`, `401`, `403`, `422`.
- `asyncapi.yaml` and `asyncapi.agent-plane.patch.yaml` follow AsyncAPI 2.6.0.
- All channels must have a `description`.  All messages must have `name`, `title`, `summary`, and `description`.

Validate before committing:

```bash
spectral lint openapi.yaml
asyncapi validate asyncapi.yaml
rg -n '^(<{7}|={7}|>{7})' .github/PULL_REQUEST_TEMPLATE.md CHANGELOG.md CONTRIBUTING.md README.md asyncapi.agent-plane.patch.yaml asyncapi.yaml examples/community.json examples/rating.json openapi.agent-plane.patch.yaml openapi.yaml schemas/AgentSession.json schemas/Agreement.json schemas/AuthorityLink.json schemas/CapabilityToken.json schemas/Comment.json schemas/Community.json schemas/Connector.json schemas/DataRef.json schemas/DataSphere.json schemas/Dataset.json schemas/EntityField.json schemas/EventEnvelope.json schemas/Exception.json schemas/ExecutionDecision.json schemas/ExecutionSurface.json
```

---

## Writing examples

- One file per schema type, saved as `examples/<typename>.json` (all-lowercase filename matching the schema `title` lowercased).
- The example must be a **complete**, valid document — all required fields present.
- Use the shared cross-reference URNs already established in other examples (e.g. `urn:srcos:dataset:health_obs`) so the example set tells a coherent end-to-end story.
- Validate the example before committing:

```bash
ajv validate -s schemas/<TypeName>.json -d examples/<typename>.json
```

---

## Pull-request checklist

The PR template will remind you, but here is the complete list:

- [ ] Schema file created/updated in `schemas/`
- [ ] `"description"` present on schema and all properties
- [ ] `"additionalProperties": false` on all object types
- [ ] Example file created/updated in `examples/` and passes AJV validation
- [ ] `schemas/README.md` updated (schema family table)
- [ ] `openapi.yaml` or patch updated with full operation metadata
- [ ] `asyncapi.yaml` or patch updated with channel/message descriptions
- [ ] `CHANGELOG.md` updated
- [ ] ADR created in `docs/adr/` if design rationale is non-obvious
- [ ] `semantic/context.jsonld` and `hydra.jsonld` updated for first-class types
- [ ] `specVersion` bumped if required (see [Breaking vs additive changes](#breaking-vs-additive-changes))
- [ ] No Git merge conflict markers remain in touched files

---

## Breaking vs additive changes

A **breaking change** is any change that can cause a previously valid document to become invalid, or a previously invalid document to become valid in an unexpected way.  Breaking changes:

1. Must bump the `specVersion` major version in the affected schema(s).
2. Must be documented in `CHANGELOG.md` under a new `## [X.0.0]` heading.
3. Must have a corresponding ADR in `docs/adr/`.
4. Should include a migration guide in the ADR.

An **additive change** (new optional field, new enum value, new endpoint) bumps the minor version only.

A **bug fix** (pattern correction, description improvement) bumps the patch version only.
