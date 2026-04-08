# Semantic Overlay

This directory provides the JSON-LD and Hydra semantic overlay for the SourceOS/SociOS specification.  These files make the schema types and REST API self-describing to Linked Data tooling.

---

## Files

| File | Purpose |
|------|---------|
| `context.jsonld` | JSON-LD `@context` mapping all 54 schema type names to stable IRIs under `https://schemas.srcos.ai/v2/` |
| `hydra.jsonld` | A `hydra:ApiDocumentation` document describing the REST API's supported classes and operations |

---

## `context.jsonld` — JSON-LD context

Include the context in any JSON document to make it a JSON-LD document:

```json
{
  "@context": "https://schemas.srcos.ai/v2/context.jsonld",
  "@type": "Dataset",
  "id": "urn:srcos:dataset:health_obs",
  ...
}
```

Or embed the context inline:

```json
{
  "@context": {
    "srcos": "https://schemas.srcos.ai/v2/",
    "Dataset": "srcos:Dataset"
  }
}
```

The context maps:
- `id` → `@id` (every `id` field becomes the node's IRI)
- `type` → `@type` (every `type` field becomes the node's RDF type)
- All 54 schema type names to `srcos:<TypeName>` IRIs
- Selected cross-vocabulary terms: `prov:wasGeneratedBy`, `prov:used`, `prov:wasAssociatedWith`

---

## `hydra.jsonld` — Hydra API documentation

The Hydra document is a machine-readable API description that extends the JSON-LD context.  It can be served at `/.well-known/hydra` to make the API self-describing.

The document lists every resource class supported by the API with its supported operations (HTTP methods), expected inputs, and returned types.

---

## Usage with Linked Data tools

### Validate JSON-LD framing

```bash
npm install -g jsonld-cli
jsonld frame --frame '{"@type":"Dataset"}' examples/dataset.json
```

### Generate RDF/Turtle from an example

```bash
jsonld format --output-format nquads examples/dataset.json
```

### Check Hydra documentation

```bash
curl https://api.srcos.local/.well-known/hydra | python3 -m json.tool
```

---

## Extending the context

When adding a new first-class schema type:

1. Add a mapping to `context.jsonld`: `"NewType": "srcos:NewType"`
2. Add a `hydra:supportedClass` entry to `hydra.jsonld` with at minimum `hydra:title`, `hydra:description`, and the applicable `hydra:supportedOperation` entries.
3. Update this README's file table.

See [CONTRIBUTING.md](../CONTRIBUTING.md#6-update-the-semantic-context-if-needed) for the full guide.

---

## Standards references

- [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/)
- [Hydra Core Vocabulary](https://www.hydra-cg.com/spec/latest/core/)
- [W3C PROV-O](https://www.w3.org/TR/prov-o/) — used for `ProvenanceRecord` mappings
