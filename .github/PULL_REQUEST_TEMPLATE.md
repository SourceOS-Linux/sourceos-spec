## Summary

<!-- Briefly describe what this PR changes and why. -->

## Area(s) affected

<!-- Check all that apply -->
- [ ] Schema(s) — which ones: 
- [ ] Example(s)
- [ ] OpenAPI (`openapi.yaml` or agent-plane patch)
- [ ] AsyncAPI (`asyncapi.yaml` or agent-plane patch)
- [ ] Semantic overlay (`semantic/context.jsonld` or `hydra.jsonld`)
- [ ] Documentation (`README.md`, `schemas/README.md`, `CONTRIBUTING.md`)
- [ ] ADR (`docs/adr/`)
- [ ] CI / workflows

## Type of change

<!-- Check one -->
- [ ] 🐛 Bug fix (corrects an error in an existing schema, example, or doc)
- [ ] ✨ New schema / endpoint / channel (backward-compatible addition)
- [ ] 📝 Documentation improvement
- [ ] 💥 Breaking change (modifies or removes an existing schema property or endpoint)

## Checklist

- [ ] I have run local schema validation (`ajv compile` on all changed schemas).
- [ ] I have run example validation (`ajv validate` for any new or changed examples).
- [ ] All new schemas include a top-level `description` and property-level `description` on every field.
- [ ] All new schemas have a corresponding example in `examples/`.
- [ ] New schemas are documented in `schemas/README.md`.
- [ ] New API endpoints include `summary`, `description`, and 4xx/5xx responses.
- [ ] New event channels include a `description`, `publish` and `subscribe` directions, and `operationId`.
- [ ] New schema types are mapped in `semantic/context.jsonld`.
- [ ] `CHANGELOG.md` is updated with a summary of changes under `[Unreleased]`.
- [ ] Breaking changes include an ADR in `docs/adr/` and two maintainer approvals.

## Related issues / ADRs

<!-- Link to any related issues or ADR files -->
