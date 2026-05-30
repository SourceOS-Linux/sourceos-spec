# SourceOS Interaction Substrate Catalog

Status: Informational  
Schema: `schemas/SourceOSInteractionEvent.json`  
Example: `examples/sourceos-interaction-event.json`  
Normative contract: `docs/contract-additions/sourceos-interaction-substrate.md`

## Purpose

This catalog entry makes the SourceOS interaction substrate discoverable for implementers who start from the contract-additions directory rather than from the schema tree.

`SourceOSInteractionEvent` is the shared noetic/chat/task projection used by Noetica, AgentTerm, Matrix-facing operator flows, Superconscious task boundaries, AgentPlane evidence surfaces, Memory Mesh context-pack handoffs, Agent Registry grant references, and Policy Fabric decisions.

The key architectural rule is that Noetica and AgentTerm are separate surfaces over the same interaction contract:

- Noetica emits browser chat, model route, steering intent, provider evidence, and inline governance-trail events.
- AgentTerm ingests and renders the same event shape as a terminal / Matrix / operator governance trace.
- OpsHistory remains the local-first operational event ledger.
- Policy Fabric, Agent Registry, Memory Mesh, AgentPlane, and model-routing authorities remain outside both UI surfaces.

## Contract objects

| Artifact | Role |
| --- | --- |
| `schemas/SourceOSInteractionEvent.json` | Machine-readable JSON Schema for the shared interaction envelope. |
| `examples/sourceos-interaction-event.json` | Valid Noetica standalone completion example consumable by AgentTerm. |
| `tools/validate_sourceos_interaction_examples.py` | Dedicated validator for the schema/example pair. |
| `.github/workflows/sourceos-interaction-substrate.yml` | CI workflow for the interaction-substrate slice. |
| `docs/contract-additions/sourceos-interaction-substrate.md` | Normative design and authority-boundary contract. |

## Required downstream bindings

| Repository | Binding obligation |
| --- | --- |
| `SocioProphet/Noetica` | Emit `SourceOSInteractionEvent` for standalone and SourceOS chat lifecycle events. |
| `SourceOS-Linux/agent-term` | Ingest and render `SourceOSInteractionEvent` governance traces. |
| `SocioProphet/superconscious` | Accept or emit this shape at the task boundary without taking ownership of memory, policy, or evidence authority. |
| `SocioProphet/agentplane` | Attach run, replay, and evidence references rather than scraping surface-local state. |
| `SocioProphet/memory-mesh` | Consume bounded context-pack references rather than unbounded transcripts. |
| `SocioProphet/agent-registry` | Resolve non-human participants, grants, sessions, and revocation references. |
| `SocioProphet/policy-fabric` | Decide side effects, context release, memory writeback, bridge/export, redaction, and replay admission. |

## Payload posture

Interaction payloads are bounded by default. The valid payload modes are `metadata-only`, `summary`, `ref-only`, `inline-bounded`, and `redacted`.

Implementations must not place raw secrets, credentials, unrestricted browser history, unrestricted shell output, unrestricted transcripts, or private chain-of-thought in `payload`.

## Operational flow

```text
Noetica standalone or SourceOS chat lifecycle
  -> SourceOSInteractionEvent
  -> governance trace visible in Noetica
  -> OpsHistory or artifact reference
  -> AgentTerm render/record/replay surface
```

```text
AgentTerm Matrix or terminal command
  -> SourceOSInteractionEvent
  -> Policy Fabric decision
  -> Agent Registry grant resolution
  -> Superconscious / AgentPlane task
  -> governance trace visible in AgentTerm or Noetica
```

## Completion status

Initial implementation status at catalog creation:

- SourceOS spec schema/example/validator/workflow: merged.
- AgentTerm fixture ingest/render path: merged.
- Noetica emitter path: merged.

Future work should add generated types or schema-consumption automation when the downstream repositories are ready for a shared package or codegen path.
