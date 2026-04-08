# ADR-0004: Multi-language policy conditions

**Status:** Accepted  
**Date:** 2025-12-24  
**Deciders:** SourceOS core team

---

## Context

The `Rule` schema includes an optional `condition` property (a `PolicyCondition`) that gates a rule's effect with a boolean expression. The platform's governance use cases require varying levels of expressiveness:

| Use case | Required expressiveness |
|---|---|
| Simple attribute equality | `purpose == "export"` |
| Complex ABAC with functions | `time.now() < agreement.effectiveEnd` |
| Full Rego-based OPA integration | Multi-file policy bundles |
| Cedar (AWS Verified Permissions) | Structured entity-based conditions |

A single built-in expression language cannot satisfy all these use cases without significant implementation complexity.

## Decision

`PolicyCondition` declares a **`language` field** with an enum of four supported policy languages: `jsonlogic`, `cel`, `rego`, `cedar`. The `expr` field carries the condition in the format appropriate for the declared language.

## Rationale

1. **jsonlogic** — JSON-native, zero-dependency expression evaluation; suitable for simple conditions embeddable in UI rule builders.
2. **cel** — Google Common Expression Language; supports rich function libraries, type-safe evaluation, and is the foundation of Kubernetes admission policies.
3. **rego** — Open Policy Agent's rule language; enables full OPA integration for organisations already running OPA.
4. **cedar** — Amazon's Cedar policy language; enables direct integration with AWS Verified Permissions.

This approach lets platform teams adopt the policy engine they already use, rather than migrating to a SourceOS-specific language.

## Trade-offs

- **Evaluation heterogeneity** — a policy engine must support (or delegate to) all four languages. Implementations that support only a subset must reject policies with unsupported `language` values.
- **`expr` is untyped** — `PolicyCondition.expr` is typed as `object` in the schema. For CEL and Rego, the expression is typically a string, which means it must be JSON-escaped. Future schema versions may refine this with `oneOf` per language.
- **Testing complexity** — integration tests for the policy engine must cover all four languages.

## Conflict resolution

When multiple rules in a policy match the same request, the **first matching rule** wins (ordered evaluation). The `condition` guard is evaluated only if the rule's `operations` and the policy's `scope` already match.

## Consequences

- `PolicyCondition.language` is a required enum field; no default language is assumed.
- Implementations must validate the `expr` syntax for the declared language at policy-upsert time and reject syntactically invalid conditions with a `400` response.
- The `notes` field is strongly recommended to document the intent of non-trivial conditions for human reviewers.
