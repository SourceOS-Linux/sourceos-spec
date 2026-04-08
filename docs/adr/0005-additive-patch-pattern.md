# ADR-0005: Additive patch pattern for the agent plane

**Status:** Accepted  
**Date:** 2025-12-24  
**Deciders:** SourceOS core team

---

## Context

The SourceOS platform has two distinct deployment surfaces:

1. **Metadata Plane** — always deployed; governs data assets, policies, lineage, and collaboration.
2. **Agent Plane** — optionally deployed; adds AI agent session management, skill orchestration, memory persistence, and real-time execution decisions.

The Agent Plane depends on the Metadata Plane (agents consume datasets, trigger policies, record runs) but the Metadata Plane does not depend on the Agent Plane.

Three options were considered for representing this in the spec:

| Option | Description |
|---|---|
| **Single file** | Merge all schemas and API endpoints into one `openapi.yaml` and one `asyncapi.yaml` |
| **Separate repositories** | Maintain agent-plane as an entirely separate spec repo |
| **Additive patch files** | Core spec in `openapi.yaml` / `asyncapi.yaml`; agent-plane additions in `*.agent-plane.patch.yaml` files |

## Decision

Use **additive patch files** (`openapi.agent-plane.patch.yaml`, `asyncapi.agent-plane.patch.yaml`) that extend the core specification.

## Rationale

1. **Deployment flexibility** — teams deploying only the Metadata Plane do not need to process or implement agent-plane endpoints.
2. **Single-repo governance** — keeping both planes in one repo simplifies cross-cutting concerns (versioning, CI, shared schemas).
3. **Additive-only** — patch files add paths/channels; they never modify existing ones. This preserves backward compatibility of the core spec independently of the agent-plane additions.
4. **Clear seam** — the patch boundary documents the exact contract surface of the agent plane, making it easy to audit what an agent-plane deployment requires.

## Merge strategy

To obtain the full combined API spec, merge the patch files with the base using either:

```bash
# With yq (recommended)
yq eval-all 'select(fi == 0) *+ select(fi == 1)' openapi.yaml openapi.agent-plane.patch.yaml > openapi.combined.yaml

# With OpenAPI Overlay tooling
# The patch files are structured to be compatible with the OpenAPI Overlay specification.
```

The `paths` and `channels` objects are deep-merged (not replaced). The patch files do not include `info`, `servers`, or `components` keys — these are defined only in the base files.

## Consequences

- The patch files are not standalone valid OpenAPI/AsyncAPI documents; they are fragments.
- CI must validate each patch file in the context of the merged spec (done in `.github/workflows/validate.yml`).
- Any new plane or extension (e.g., a federated-governance plane) should follow the same pattern with a new `*.patch.yaml` pair.
- Consumer tooling must apply the appropriate patches before generating client stubs.
