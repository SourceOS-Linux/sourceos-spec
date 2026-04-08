# Contributing to SourceOS Spec

Thank you for contributing to the SourceOS/SociOS Typed Contracts Specification.

## Contents

- [What lives in this repo](#what-lives-in-this-repo)
- [Before you open a PR](#before-you-open-a-pr)
- [Schema design conventions](#schema-design-conventions)
- [URN naming conventions](#urn-naming-conventions)
- [Adding a new schema](#adding-a-new-schema)
- [Modifying an existing schema](#modifying-an-existing-schema)
- [Adding or updating examples](#adding-or-updating-examples)
- [API and event-spine changes](#api-and-event-spine-changes)
- [Semantic overlay changes](#semantic-overlay-changes)
- [Review process](#review-process)
- [Versioning policy](#versioning-policy)

---

## What lives in this repo

This repository is a **specification**, not an implementation. Changes here define the contract that all SourceOS implementations must conform to. Think carefully before making breaking changes — they require a major version bump and coordinated migration across all consumers.

---

## Before you open a PR

1. **Run local validation:**

   ```bash
   # Validate all schemas are syntactically correct JSON Schema 2020-12
   npm install -g ajv-cli
   for f in schemas/*.json; do
     ajv compile -s "$f" && echo "$f: ok"
   done

   # Validate all examples against their schemas
   for f in examples/*.json; do
     type=$(jq -r '.type // empty' "$f")
     [ -n "$type" ] && ajv validate -s "schemas/${type}.json" -d "$f" && echo "$f: ok"
   done
   ```

2. **Ensure CI passes** — the `validate.yml` workflow runs automatically on every PR.

3. **One concern per PR** — separate schema additions, bug fixes, and breaking changes into distinct PRs.

---

## Schema design conventions

All schemas must follow these rules:

1. **`"$schema": "https://json-schema.org/draft/2020-12/schema"`** — always pin the draft version.
2. **`"$id": "https://schemas.srcos.ai/v2/<SchemaName>.json"`** — canonical ID must match the filename.
3. **`"additionalProperties": false`** — no open-ended objects. This enforces strict schema evolution.
4. **`"description"` on every schema** — add a top-level `description` field explaining the schema's purpose.
5. **`"description"` on every property** — all properties must have a `description` string.
6. **Use `$ref`** to reference other schemas rather than inlining their structure.
7. **Discriminator constants** — top-level objects include a `"type"` property with `"const": "<SchemaName>"` to support polymorphic deserialization.
8. **No `$defs`/`definitions` in individual files** — shared sub-schemas live in their own files.
9. **Nullability** — use `"type": ["string", "null"]` (or equivalent) for optional nullable fields; never use `required` to hide optionality.
10. **Enums** — prefer explicit `"enum": [...]` over free strings wherever the value space is finite and stable.

---

## URN naming conventions

All stable IDs use URNs in the pattern:

```
urn:srcos:<family>:<local-id>
```

Where `<family>` is a short lowercase noun (e.g., `dataset`, `policy`, `session`, `skill`). Examples:

- `urn:srcos:dataset:health_obs`
- `urn:srcos:policy:export_health_restricted`
- `urn:srcos:session:a1b2c3d4`

Local IDs may be UUIDs, slugs, or short hashes — but must be globally unique within the family.

---

## Adding a new schema

1. Create `schemas/<SchemaName>.json` using the template below.
2. Add an entry for it in `schemas/README.md` under the appropriate area.
3. Add a corresponding example file `examples/<snake_case_name>.json`.
4. If the schema represents a first-class API resource, add an endpoint to `openapi.yaml` (or the appropriate patch file).
5. If it generates events, add a channel to `asyncapi.yaml` (or the appropriate patch file).
6. Add the type mapping to `semantic/context.jsonld`.
7. If it is API-accessible, add a `hydra:supportedClass` entry to `semantic/hydra.jsonld`.

### Schema template

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.srcos.ai/v2/MySchema.json",
  "title": "MySchema",
  "description": "One paragraph explaining what this schema represents and when it is used.",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "type", "specVersion"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Stable URN identifying this object (urn:srcos:<family>:<id>)."
    },
    "type": {
      "const": "MySchema",
      "description": "Discriminator constant — always 'MySchema'."
    },
    "specVersion": {
      "type": "string",
      "description": "Semantic version of the SourceOS spec this record conforms to."
    }
  }
}
```

---

## Modifying an existing schema

### Backward-compatible changes (minor version bump)
- Adding a new **optional** property
- Adding a new enum value (consumers must handle unknown values gracefully)
- Relaxing a constraint (e.g., removing a `minLength`)
- Adding a new schema file

### Breaking changes (major version bump)
- Adding a new **required** property to an existing schema
- Removing or renaming a property
- Narrowing a type (e.g., `string` → `enum`)
- Removing an enum value
- Changing a `$ref` target

Breaking changes require:
1. Incrementing the major version in `README.md`, `openapi.yaml`, and `asyncapi.yaml`.
2. A migration note in `CHANGELOG.md`.
3. An ADR in `docs/adr/` explaining the rationale.

---

## Adding or updating examples

Every schema should have a corresponding example file in `examples/`. Naming convention:

- Use `snake_case` matching the schema name: `SchemaDefinition.json` → `schema.json` (or `schema_definition.json` for new files).
- The example must be a **valid** instance of the schema — CI validates this automatically.
- Examples should be realistic and self-contained (all referenced URNs should also appear in other examples where possible).
- Null values should be shown for optional nullable fields to make the shape of the object clear.

---

## API and event-spine changes

- **New REST endpoints:** Add to `openapi.yaml` (metadata plane) or `openapi.agent-plane.patch.yaml` (agent plane). Follow the existing pattern: include `summary`, `description`, `tags`, and responses for `200`, `400`, `401`, `403`, and `500`.
- **New event channels:** Add to `asyncapi.yaml` or `asyncapi.agent-plane.patch.yaml`. Include both `publish` and `subscribe` directions, a `description`, and `operationId` values.

---

## Semantic overlay changes

- `semantic/context.jsonld` — Add a mapping for every new schema type.
- `semantic/hydra.jsonld` — Add a `hydra:supportedClass` entry for every new API-accessible resource, listing all supported HTTP methods.

---

## Review process

1. Open a pull request against `main`.
2. The automated `validate.yml` workflow must pass (schema lint + example validation).
3. At least one maintainer must review and approve.
4. The PR description must reference the area affected (schema family, API, event spine, or semantic overlay).
5. Breaking changes require two maintainer approvals and an ADR.

---

## Versioning policy

This specification uses [semantic versioning](https://semver.org/):

| Bump | When |
|---|---|
| Patch (`2.0.x`) | Bug fixes, description improvements, example additions |
| Minor (`2.x.0`) | New optional properties, new schemas, new enum values, new API endpoints |
| Major (`3.0.0`) | Breaking changes to existing schemas or removal of resources |

The version appears in `openapi.yaml` (`info.version`), `asyncapi.yaml` (`info.version`), and should be reflected in the `specVersion` field of all new records written after the bump.
