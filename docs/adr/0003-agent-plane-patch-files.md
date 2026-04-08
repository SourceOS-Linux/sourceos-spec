# ADR-0003: Additive patch files for the agent plane

**Date:** 2025-12-24  
**Status:** Accepted

---

## Context

The SourceOS agent plane (agent sessions, execution decisions, skill manifests, memory) is a distinct concern from the metadata governance plane (datasets, policies, provenance).  Not all deployments require the agent plane.  Folding agent-plane endpoints into the single `openapi.yaml` and `asyncapi.yaml` would:
- Force all consumers to deal with agent-plane types even if they only use the metadata plane.
- Make the base spec harder to read and maintain.
- Couple the release cycle of both planes.

## Decision

The agent-plane OpenAPI endpoints are defined in a separate file, `openapi.agent-plane.patch.yaml`, and the agent-plane AsyncAPI channels in `asyncapi.agent-plane.patch.yaml`.

Both patch files are **additive only** — they add new `paths` / `channels` without modifying or removing anything in the base spec.

Consumers merge the patches at build time using standard tooling (`openapi-merge-cli`, `@asyncapi/bundler`).

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Separate standalone specs | Duplicates shared component schemas; two separate server surfaces to maintain |
| Single unified spec | Couples agent-plane and metadata-plane release cycles; harder to deploy metadata-only |
| OpenAPI overlays (v1 spec) | Standard not finalised at time of design; tooling immature |

## Consequences

**Positive:**
- Metadata-plane-only implementations carry zero agent-plane surface area.
- Each plane can evolve independently.
- The patch model is explicit and auditable — diffs are small and focused.

**Negative:**
- Build pipelines must include a merge step.
- Tooling for patch merging is not yet standardised across all OpenAPI/AsyncAPI tools.
- Ordering matters — the base spec must be loaded before the patch.

## References

- `openapi.agent-plane.patch.yaml`
- `asyncapi.agent-plane.patch.yaml`
- `CONTRIBUTING.md` §Updating the API specs
