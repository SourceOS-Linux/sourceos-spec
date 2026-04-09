# ADR-0001: Use `urn:srcos:` as the universal identifier namespace

**Date:** 2025-12-24  
**Status:** Accepted

---

## Context

Every object in the spec needs a stable, globally unique identifier that:
- Is collision-free across multiple deployments and organisations.
- Can be compared as a plain string without parsing.
- Embeds type information so a resolver can route to the right handler without a schema look-up.
- Follows an existing, well-understood standard.

Several options were evaluated:
- UUID v4 (opaque, no type information, collision-free)
- HTTP URL (requires a resolvable server, fragile across environments)
- URN with custom NID (standards-compliant, type-aware, stable)

## Decision

All top-level objects use Uniform Resource Names of the form:

```
urn:srcos:<type-slug>:<local-id>
```

The NID (Namespace Identifier) is `srcos` — a stable, project-specific NID registered in the spec.  The NSS (Namespace Specific String) has a mandatory `<type-slug>` prefix so the type of object can be determined from the URN alone.

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| UUID v4 | No embedded type information; resolving requires external registry |
| HTTP URL | Fragile — depends on server availability; breaks in air-gapped environments |
| `urn:sourceos:` (long form) | More verbose; abbreviation `srcos` is consistent with other project naming |

## Consequences

**Positive:**
- Identifiers are portable across environments and are self-describing.
- Pattern constraints in JSON Schema (e.g. `"pattern": "^urn:srcos:dataset:"`) provide type-safe cross-references validated at schema-validation time.
- No central registry required for local development.

**Negative:**
- Local IDs are not globally unique without organisational prefix conventions; multi-tenant deployments must ensure their `local-id` space is scoped (e.g. include an org slug).

## References

- RFC 8141 – Uniform Resource Names (URNs)
- `ARCHITECTURE.md` §4 URN identity scheme
