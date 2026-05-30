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
| `generated/typescript/sourceos-interaction-event.ts` | Generated TypeScript interface/union definitions for downstream TypeScript consumers. |
| `generated/python/sourceos_interaction_event.py` | Generated Python `TypedDict` / `Literal` definitions for downstream Python consumers. |
| `tools/generate_sourceos_interaction_types.py` | Generator and stale-output checker for the generated artifacts. |
| `tools/validate_sourceos_interaction_examples.py` | Dedicated validator for the schema/example pair. |
| `.github/workflows/sourceos-interaction-substrate.yml` | CI workflow for the interaction-substrate schema/example slice. |
| `.github/workflows/sourceos-interaction-codegen.yml` | CI workflow that checks generated artifacts are current. |
| `docs/contract-additions/sourceos-interaction-substrate.md` | Normative design and authority-boundary contract. |

## Generated type consumption

The canonical generation command is:

```bash
python tools/generate_sourceos_interaction_types.py
```

The canonical drift check is:

```bash
python tools/generate_sourceos_interaction_types.py --check
```

Downstream repositories may consume the generated artifacts by vendoring from a pinned `sourceos-spec` commit, importing from a subtree/submodule, or running the generator during their own contract-sync process.

Recommended downstream mapping:

| Consumer | Generated artifact |
| --- | --- |
| `SocioProphet/Noetica` | `generated/typescript/sourceos-interaction-event.ts` |
| `SourceOS-Linux/agent-term` | `generated/python/sourceos_interaction_event.py` |
| `SocioProphet/superconscious` | Python or TypeScript artifact depending on implementation lane |
| `SocioProphet/agentplane` | Python or TypeScript artifact depending on implementation lane |

Schema changes must update the generated artifacts in the same PR. CI should fail when the generated files are stale.

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

Initial implementation status after codegen tranche:

- SourceOS spec schema/example/validator/workflow: merged.
- AgentTerm fixture ingest/render path: merged.
- Noetica emitter path: merged.
- TypeScript and Python generated artifacts: present.
- Drift check workflow: present.

Future work should migrate Noetica and AgentTerm from local mirrors to the generated artifacts or a pinned contract-sync process.
