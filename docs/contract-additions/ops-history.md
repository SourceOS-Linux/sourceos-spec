# OpsHistory and Local-First Service Contracts

## Status

Initial additive contract seed for SourceOS/SociOS spec issue #84.

## Purpose

OpsHistory is the shared local-first operational event fabric for multi-chat human/agent work. It is not a replacement for AgentTerm, BearBrowser, SourceOS shell, Memory Mesh, Policy Fabric, Agent Registry, or AgentPlane. It defines the typed envelopes those systems exchange when they need governed operational history, context-pack handoff, redaction propagation, and replayable evidence.

This contract family codifies two platform lessons:

1. A CloudHistory-style policy plane: adaptive throttling, bounded sync windows, payload caps, idle/debounce delays, topology-aware cadence, and deletion/redaction priority.
2. A SafariBookmarksSyncAgent-style service plane: activatable local services, named IPC endpoints, push/subscription registration, maintenance resource posture, network-aware bidirectional activity, idle-safe restart, and durable local state.

## Contract family

The initial contract set is:

- `OpsHistoryEvent` — normalized operational event envelope for chat, agent, browser, shell, memory, policy, execution, GitHub/CI, artifact, redaction, revocation, and handoff events.
- `OpsHistorySyncPolicy` — topology-aware local-first propagation policy.
- `LocalFirstServiceManifest` — Linux-oriented activatable local service manifest covering D-Bus/Unix socket endpoints, durable store, network posture, subscription registration, idle stop, and redaction-priority lanes.

Follow-on additive schemas should include:

- `BearHistoryEvent`
- `BearHistorySyncPolicy`
- `ShellReceiptEvent`
- `OpsHistoryContextPackRef`
- `RedactionTombstone`

## Downstream consumers

- `SourceOS-Linux/agent-term` owns the operator ChatOps surface and local event log UX.
- `SourceOS-Linux/BearBrowser` owns browser state production and profile separation.
- `SourceOS-Linux/sourceos-shell` owns shell receipt production and cloud/fog shell metadata.
- `SocioProphet/memory-mesh` owns governed recall, writeback, and context-pack ingestion.
- `SocioProphet/policy-fabric` owns replication, hydration, writeback, bridge/export, browser export, shell export, and redaction decisions.
- `SocioProphet/agent-registry` owns non-human actor identity, endpoint grants, event access grants, revocation, and runtime authority.
- `SocioProphet/agentplane` owns validated execution, placement, run evidence, replay evidence, and context-pack consumption.

## Non-negotiables

- Local state is primary; sync/relay/cloud services are coordination surfaces.
- Raw sensitive payloads are denied by default.
- Raw browser human-profile state is never exported to agents by default.
- Raw terminal/session material is not exported by default.
- Large artifacts are referenced by stable refs/hashes rather than embedded.
- Redaction/tombstone propagation has higher priority than ordinary sync or memory writeback.
- Memory Mesh receives bounded, policy-admitted context packs rather than raw unbounded transcripts.
- AgentPlane consumes context packs and emits evidence refs; it remains the replay authority for execution artifacts.
- Agent Registry grants are required for every non-human participant and every service endpoint.
- Policy Fabric decisions are required for replication, hydration, writeback, bridge/export, and redaction.

## Linux service mapping

| Apple-style concept | SourceOS/Linux contract |
| --- | --- |
| launchd Label | systemd user unit name / service identity |
| MachServices | D-Bus well-known names and/or Unix sockets |
| XPC activity | systemd timer/socket activation or subscription-registration task |
| Pressured exit | idle-stop, restartable service, durable local state |
| ProcessType Standard | maintenance/background cgroup/resource posture |
| RequireNetworkConnectivity | network-aware queue and retry policy |
| NetworkTransferDirection | ingress/egress policy |
| Priority Maintenance | background QoS unless governance-critical |

## Initial service endpoints

Recommended well-known endpoint names:

- `org.sourceos.OpsHistory`
- `org.sourceos.OpsHistory.Push`
- `org.sourceos.OpsHistory.Redaction`
- `org.sourceos.OpsHistory.ContextPack`
- `org.sourceos.BearHistory`
- `org.sourceos.BearHistory.Push`
- `org.sourceos.BearHistory.Redaction`
- `org.sourceos.BearHistory.Export`

## Implementation posture

First implementation passes should be contract-first: docs, schemas, examples, validators, and dry-run explain/replay surfaces. Live sync, live browser export, live terminal receipt capture, and live context hydration should follow only after Policy Fabric and Agent Registry contracts are enforced.
