# SourceOS Interaction Substrate v0.1

Status: Proposed  
Date: 2026-05-22

## Purpose

This contract defines the shared interaction substrate for Noetica, AgentTerm, Matrix rooms, Prophet Workspace workrooms, Superconscious task submission, AgentPlane evidence, Policy Fabric decisions, Agent Registry grants, Memory Mesh scope, Slash Topics, and replay surfaces.

The architectural rule is simple: Noetica and AgentTerm are different surfaces over the same governed interaction substrate.

Noetica owns the browser chat, model-selection, steering UX, and inline governance trail. AgentTerm owns the terminal-native / Matrix-first operator console, room/thread flow, approvals, event tailing, and trace rendering. Neither surface owns model routing, memory durability, tool grants, policy admission, or execution evidence.

## Relationship to OpsHistory

`OpsHistoryEvent` remains the local-first operational event ledger. `SourceOSInteractionEvent` is the noetic/chat/task projection that can be embedded in, referenced by, or derived from OpsHistory.

The intended binding is:

```text
Noetica message/send/result
  -> SourceOSInteractionEvent
  -> OpsHistoryEvent
  -> AgentTerm tail/render/replay
  -> Memory Mesh context-pack request or AgentPlane evidence ref, when policy admits
```

AgentTerm can emit the same event shape from Matrix, terminal commands, or operator approvals:

```text
Matrix / terminal command
  -> SourceOSInteractionEvent
  -> Policy Fabric decision
  -> Agent Registry grant resolution
  -> Superconscious / AgentPlane task
  -> Noetica or AgentTerm governance-trail rendering
```

## Normative boundaries

1. A surface may render a governance trail, but Policy Fabric owns policy decisions.
2. A surface may request or display model routing, but model-router or the SourceOS route authority owns route decisions in `sourceos` mode.
3. A surface may request memory scope, but Memory Mesh owns recall and writeback.
4. A surface may list participants, but Agent Registry owns non-human identity, grants, sessions, revocation, and runtime authority.
5. A surface may display evidence, but AgentPlane owns execution evidence and replay artifacts.
6. A surface may declare steering intent, but blackbox prompting must not be represented as mechanistic SAE steering.
7. A surface may carry bounded summaries inline, but raw secrets, credentials, unrestricted browser history, unrestricted shell output, and private chain-of-thought are not valid payloads.
8. Redaction tombstones must propagate through OpsHistory and invalidate derived context packs, memory writebacks, exports, and replay surfaces.

## Required producers

- `SocioProphet/Noetica`: emit `SourceOSInteractionEvent` for standalone provider calls, SourceOS submissions, steering intent, governance trace updates, and task completion or failure.
- `SourceOS-Linux/agent-term`: emit the same event shape for terminal / Matrix / operator commands, approvals, room-thread bindings, task submissions, and trace rendering.
- `SocioProphet/superconscious`: accept or emit this event shape at the task boundary without becoming the memory, policy, or evidence authority.
- `SocioProphet/agentplane`: attach run, evidence, and replay refs rather than scraping raw surface state.
- `SocioProphet/memory-mesh`: receive bounded context-pack references, not unbounded transcripts.
- `SocioProphet/agent-registry`: resolve non-human participants and grants before enablement.
- `SocioProphet/policy-fabric`: decide side effects, context release, memory writeback, bridge/export, redaction, and replay admission.

## Minimum event content

A conforming event records:

- event identity and class;
- emitting surface;
- execution mode;
- conversation/workroom/topic/thread scope;
- actor and participants;
- optional task status/model/provider projection;
- optional steering intent;
- governance trace;
- payload disclosure posture;
- source event refs;
- redaction refs;
- integrity envelope.

## Surface obligations

Noetica must show the governance trace inline beside model output. AgentTerm must render the same trace in terminal/Matrix/operator form. Both must preserve enough fields for replay and audit.

Noetica-specific obligations:

- standalone mode still emits route evidence, request hash, evidence hash, provider, latency, memory posture, and policy posture;
- sourceos mode emits the same shape even when live submission is unavailable or blocked;
- steering UI emits explicit `steeringIntent` status and does not conflate prompt engineering with mechanistic steering.

AgentTerm-specific obligations:

- terminal, Matrix, and slash-command actions become interaction events before dispatch;
- high-risk actions require Policy Fabric decisions and Agent Registry grants before execution;
- AgentTerm can render Noetica / Superconscious / AgentPlane traces without owning cognition, routing, memory, or execution authority.

## Non-goals

This contract does not replace `OpsHistoryEvent`. It does not define model-provider SDK behavior. It does not define Matrix transport semantics. It does not create a new memory store. It does not permit unrestricted transcript replication. It does not grant tool authority.

## Acceptance criteria

- `schemas/SourceOSInteractionEvent.json` validates.
- `examples/sourceos-interaction-event.json` validates.
- Noetica can emit the example shape from a standalone chat completion.
- AgentTerm can ingest and render the example governance trail without live Matrix or live provider credentials.
- All side-effecting follow-on behavior remains behind policy and grant gates.
