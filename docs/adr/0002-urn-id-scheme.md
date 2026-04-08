# ADR-0002: Stable URN identifier scheme

**Status:** Accepted  
**Date:** 2025-12-24  
**Deciders:** SourceOS core team

---

## Context

Every first-class object in the platform needs a globally unique, stable, dereferenceable identifier. Several identifier schemes were considered:

| Option | Example | Pros | Cons |
|---|---|---|---|
| **UUID v4** | `550e8400-e29b-41d4-a716-446655440000` | Universally unique; tooling support | Opaque; no human-readable semantics |
| **URL** | `https://api.srcos.ai/v2/datasets/health_obs` | Dereferenceable | Tightly coupled to a single deployment; breaks in offline/air-gapped contexts |
| **URN** | `urn:srcos:dataset:health_obs` | Stable regardless of deployment URL; human-readable; globally unique | Requires a custom URN namespace |
| **Slug** | `health_obs` | Human-readable | Not globally unique; collides across domains |

## Decision

Use **URNs** in the pattern `urn:srcos:<family>:<local-id>` as the canonical identifier format for all first-class objects.

## Rationale

1. **Deployment-agnostic** — URNs do not encode server location, enabling the same records to be portable across local dev, staging, and production environments.
2. **Human-readable** — the `<family>` segment immediately communicates the object type (e.g., `urn:srcos:policy:…` is obviously a policy).
3. **Namespace isolation** — the `srcos` namespace prevents collisions with external systems.
4. **Stable** — URNs cannot change after issuance. This is enforced by the `id` field being required and `additionalProperties: false` preventing accidental mutation.
5. **Cross-reference-friendly** — `$ref`-style cross-references between schemas (e.g., `Dataset.assetRef` → a PhysicalAsset URN) are human-readable without a lookup table.

## Conventions

- `<family>` must be a short lowercase noun matching the schema family: `dataset`, `policy`, `session`, `skill`, `memory`, `run`, `prov`, `agreement`, `connector`, `asset`, `schema`, `glossary`, `mapping`, `workflow`, `workload`, `flag`, `rollout`, `receipt`, `review`, `community`, `comment`, `rating`, `signal`, `telemetry`, `party`, `event`.
- `<local-id>` should be either a UUID v4, a short content-addressed hash, or a human-readable slug — but must be unique within the family.
- CapabilityTokens use an opaque `tok_<id>` format instead of a URN because they are short-lived and treated as bearer tokens, not catalogued objects.

## Consequences

- All `id` fields in top-level schemas are `string` with no further format constraint in the JSON Schema — enforcement of the URN pattern is left to the implementation layer.
- IDs must never be recycled after deletion; implementations must maintain a tombstone registry.
- Cross-deployment federation requires a namespace prefix strategy (e.g., `urn:srcos:tenant_a:dataset:health_obs`) — this is out of scope for v2 but the URN scheme accommodates it naturally.
