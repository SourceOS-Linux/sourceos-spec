# ADR-0002: Typed `PolicyCondition` with declared expression language

**Date:** 2025-12-24  
**Status:** Accepted

---

## Context

Version 1 policy rules used free-form JSON objects for conditions, with no declared language or evaluation semantics.  This made it impossible to:
- Statically analyse policies for conflicts or completeness.
- Choose an appropriate evaluator without out-of-band configuration.
- Validate that expressions are syntactically correct for their language.

The spec needed a way to embed policy conditions that is both machine-evaluable and auditable.

## Decision

`PolicyCondition` carries an explicit `language` discriminator field with four supported values:

| Value | Language | Evaluator |
|-------|----------|-----------|
| `jsonlogic` | [JSON Logic](https://jsonlogic.com/) | Lightweight, embeddable, no external deps |
| `cel` | [Common Expression Language](https://cel.dev/) | Google Cloud, Kubernetes, Open Policy Agent |
| `rego` | [Open Policy Agent Rego](https://www.openpolicyagent.org/docs/latest/policy-language/) | Full policy-as-code system |
| `cedar` | [AWS Cedar](https://www.cedarpolicy.com/) | Purpose-built authorisation, strongly typed |

The `expr` field holds the condition expression as an opaque JSON object whose structure is defined by the `language` value.

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Single language only (e.g. Rego) | Forces all deployments to run a full OPA sidecar; overkill for simple conditions |
| String expression (FEEL, SpEL) | Not natively embeddable in JSON without escaping; harder to statically analyse |
| No conditions (binary permit/deny) | Insufficient for real-world ABAC/PBAC requirements |

## Consequences

**Positive:**
- Implementations can choose the evaluator appropriate to their stack.
- `jsonlogic` covers the majority of simple conditions with zero external dependencies.
- The `language` field enables static routing to the correct evaluator without parsing the expression.
- Future languages can be added as new enum values (additive / minor version bump).

**Negative:**
- Implementations must handle all four languages or document which subset they support.
- Cross-language policy sets cannot be uniformly evaluated by a single engine.
- Expression syntax is not validated by JSON Schema (only `expr: { type: object }`) — a linter or separate validator is required.

## References

- `schemas/PolicyCondition.json`
- `schemas/Rule.json`
- `examples/policy.json` — demonstrates `jsonlogic` condition
