# SourceOS Interaction Reference Flow v0.1

Status: Informational reference packet  
Manifest: `examples/interaction-flow/noetica-superconscious-agentplane-agentterm.flow.json`

## Purpose

This reference packet pins the current end-to-end SourceOS interaction substrate path:

```text
Noetica emits SourceOSInteractionEvent
  -> Superconscious binds the interaction at the task/cognition boundary
  -> AgentPlane attaches execution evidence and replay refs
  -> AgentTerm renders and records the governance trace
```

The packet exists to make the current multi-repo implementation auditable as one governed interaction path, without moving authority into a new plane.

## Authority map

| Plane | Authority |
| --- | --- |
| `SourceOS-Linux/sourceos-spec` | Canonical schema and generated contract artifacts. |
| `SocioProphet/Noetica` | Browser chat, model-selection, steering UX, and inline governance-trail surface. |
| `SocioProphet/superconscious` | Task/cognition coordination boundary. |
| `SocioProphet/agentplane` | Execution evidence, run artifacts, validation artifacts, placement artifacts, and replay artifacts. |
| `SourceOS-Linux/agent-term` | Terminal/operator rendering and local event-recording surface. |
| Policy Fabric | Policy admission authority. |
| Agent Registry | Identity, grants, sessions, and revocation authority. |
| Memory Mesh | Durable memory and context-pack authority. |

## Pinned implementation commits

The reference manifest records the exact downstream commits that completed the first implementation wave:

| Repository | Commit | Role |
| --- | --- | --- |
| `SourceOS-Linux/sourceos-spec` | `c7f8c2d9e42a56e1127c2f9b85649cbea0f0a9fa` | Canonical schema/codegen/catalog. |
| `SocioProphet/Noetica` | `2a73b44338335a39283bcf65b4e072e29b8946a3` | Emitter and TypeScript contract-sync check. |
| `SourceOS-Linux/agent-term` | `076db5f0ebd6acae665a0b3b90e56c88735bc301` | Renderer/recorder and Python contract-sync check. |
| `SocioProphet/superconscious` | `a4742b092584432871a7a15da49e15f054b8d393` | Task-boundary binding. |
| `SocioProphet/agentplane` | `e9797a8358405475fc12eb94d5c6b00547bd0ddf` | Evidence/replay binding. |

## Payload posture

The reference packet is ref-oriented. It must not contain raw secrets, credentials, unrestricted browser history, unrestricted shell output, unrestricted transcripts, private chain-of-thought, private reasoning, or raw execution logs.

## Validation

Run:

```bash
python tools/validate_interaction_flow_reference.py
```

The validator checks:

- required repository roles are present;
- pinned commits are present;
- interaction event refs use the canonical `urn:srcos:interaction-event:` prefix;
- the authority map preserves separation of concerns;
- forbidden payload categories are recorded;
- validation references include downstream sync/boundary/evidence checks.
