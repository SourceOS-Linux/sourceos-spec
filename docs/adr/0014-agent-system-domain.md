# ADR-0014: Introduce agent-system as a new schema family

**Date:** 2026-07-31
**Status:** `Accepted`

---

## Context

The existing Agent Plane schema family (`AgentSession`, `ExecutionDecision`,
`ExecutionSurface`) operates at the **workflow / session** level. It has no
host-level agent classification object — no typed vocabulary for "what class is
this process, what flags govern it, and what is it authorized to do on this
host."

Analysis of the macOS/iOS `usernoted` server ontology revealed a five-class
typed agent model that governs execution authorization, spatial permissions,
and intelligence constraints. Multiple downstream repos need this vocabulary as
a stable reference: `agent-machine` (host attestation → execution surface),
`mcp-a2a-zero-trust` (agent identity → trust tier), `synapseiq` (enrichment),
`workstation-contracts` (conformance fixtures), and `source-os` (kernel-level
class enforcement). Without a canonical anchor, each would invent its own
incompatible classification.

## Decision

Introduce **agent-system** as a new schema family in `sourceos-spec`:

- Canonical schemas: **`AgentPassport`** (T0-1, #227) — five-class typed
  host-agent classification; **`SeamDefinition`** (T0-2, #229) — typed
  architectural-seam registry object.
- Vocabulary seed: **`semantic/agent-system-vocabulary.jsonld`** (T0-3, #231) —
  base namespace `https://spec.sourceos.dev/vocab/agent-system#`.
- Boundary: **agent-system = host-level process classification**; **Agent Plane
  = workflow execution.** They are complementary, not overlapping.

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Extend the Agent Plane family with host fields | Conflates two distinct concerns (host process vs. workflow session); pollutes AgentSession with fields most consumers don't need. |
| Let each downstream repo define its own agent classes | Guarantees divergent, incompatible vocabularies and no stable cross-repo URN. |
| Define only OWL/SHACL in ontogenesis, no JSON Schema anchor | Leaves JSON-consuming surfaces (NLBoot, control plane, web) without a validatable contract. |

## Consequences

- All downstream repos may import `urn:srcos:agent-passport:*` and
  `urn:srcos:seam-definition:*` as stable references.
- Breaking changes to these schemas require a major version bump and a
  migration guide.
- `ontogenesis` provides the OWL/SHACL realization (T1); `sourceos-spec`
  provides the JSON Schema / JSON-LD anchor. The two must stay in sync — the
  SHACL constraints in T1-4 are the authoritative enforcement of the cross-field
  invariants that JSON Schema expresses only partially.
- Cross-field invariants (e.g. `third_party` cannot set `system_bundle: true`;
  SEAM-002 suppression bans) are enforced in the JSON Schema via `if/then` where
  expressible and asserted by rejection in the validators.

## References

- T0-1 AgentPassport — #227 (schema), PR #228
- T0-2 SeamDefinition — #229, PR #230
- T0-3 agent-system vocabulary — #231, PR #232
- Tranche Work Orders v1.0 (2026-06-09), SP-SESSION-DOSSIER-20260609
- Related: ADR-0001 URN identity scheme, ADR-0002 JSON Schema draft 2020-12
