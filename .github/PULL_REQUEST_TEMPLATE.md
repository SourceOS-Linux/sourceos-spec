## Description of change

<!-- Summarise what this PR does and why. -->

## Type of change

- [ ] New schema (additive)
- [ ] Modified schema — additive (new optional field, new enum value)
- [ ] Modified schema — breaking (required field added/removed, type narrowed)
- [ ] New or updated example
- [ ] OpenAPI / AsyncAPI change
- [ ] Documentation only
- [ ] Bug fix

## Checklist

- [ ] Schema file created/updated in `schemas/` with `"description"` on schema and all properties
- [ ] `"additionalProperties": false` present on all object types in the schema
- [ ] Example file created/updated in `examples/` and passes `ajv validate`
- [ ] `schemas/README.md` updated (family table row added/updated)
- [ ] `openapi.yaml` or patch updated with `summary`, `description`, `tags`, and error responses
- [ ] `asyncapi.yaml` or patch updated with channel and message descriptions
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] `specVersion` bumped if this is a breaking change
- [ ] ADR created in `docs/adr/` if the design involves a non-obvious choice
- [ ] `semantic/context.jsonld` and `hydra.jsonld` updated for new first-class types
- [ ] No Git merge conflict markers remain in touched files

## Validation commands run

```bash
# Schema validation
ajv validate -s schemas/<TypeName>.json -d examples/<typename>.json

# OpenAPI lint
spectral lint openapi.yaml

# AsyncAPI lint
asyncapi validate asyncapi.yaml

# Merge-conflict marker check
rg -n '^(<{7}|={7}|>{7})' .github/PULL_REQUEST_TEMPLATE.md CHANGELOG.md CONTRIBUTING.md README.md asyncapi.agent-plane.patch.yaml asyncapi.yaml examples/community.json examples/rating.json openapi.agent-plane.patch.yaml openapi.yaml schemas/AgentSession.json schemas/Agreement.json schemas/AuthorityLink.json schemas/CapabilityToken.json schemas/Comment.json schemas/Community.json schemas/Connector.json schemas/DataRef.json schemas/DataSphere.json schemas/Dataset.json schemas/EntityField.json schemas/EventEnvelope.json schemas/Exception.json schemas/ExecutionDecision.json schemas/ExecutionSurface.json
```

## Related issues / ADRs

<!-- Link any related issues or ADR documents -->
