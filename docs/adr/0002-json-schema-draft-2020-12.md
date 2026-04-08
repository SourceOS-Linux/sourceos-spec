# ADR-0002: Use JSON Schema draft 2020-12

**Status:** Accepted  
**Date:** 2025-12-24  
**Deciders:** SourceOS core team

---

## Context

The specification needs a schema language to define the shape, types, and constraints of all platform objects. Several options were considered:

| Option | Pros | Cons |
|---|---|---|
| **JSON Schema draft 2020-12** | Widely supported (AJV, jsonschema, etc.), JSON-native, no compilation step, large ecosystem | More verbose than Protobuf/Avro; no native binary encoding |
| **OpenAPI-native schemas** | Already required for the REST API layer | Tied to HTTP; awkward for standalone schema use |
| **Protobuf / gRPC** | Compact binary format; strong codegen | Requires a compiler; not JSON-native; harder to embed in YAML/JSON config |
| **Apache Avro** | Efficient for streaming | Less ergonomic for REST payloads; schema registry dependency |
| **Zod / TypeScript-first** | Excellent DX for TS consumers | Language-specific; no runtime support for Python/Go/Java |

## Decision

Use **JSON Schema draft 2020-12** for all schema definitions.

## Rationale

1. **Language-neutral** — validators exist in every major language (Node, Python, Go, Java, Rust, .NET).
2. **Tooling depth** — quicktype, datamodel-code-generator, and openapi-generator can all consume JSON Schema files directly.
3. **OpenAPI compatibility** — OpenAPI 3.1.x is a superset of JSON Schema 2020-12, enabling future migration without rewriting schemas.
4. **Self-describing** — schemas are valid JSON documents that can be hosted at stable `$id` URLs and referenced via `$ref`, supporting a distributed schema registry.
5. **`additionalProperties: false`** — JSON Schema's `additionalProperties` keyword lets us enforce strict object shapes, which is essential for a spec that must be forward-compatible.

## Consequences

- All schemas must include `"$schema": "https://json-schema.org/draft/2020-12/schema"`.
- All schemas must have a stable `"$id"` URL.
- Validators must be configured for draft 2020-12 (e.g., AJV requires `new Ajv({ strict: false })` for some 2020-12 features).
- Binary/streaming use cases (Kafka, gRPC) must use a separate serialisation layer (e.g., Avro wrappers); this spec does not define that layer.
