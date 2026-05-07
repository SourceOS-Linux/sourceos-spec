# Execution Control Reconciliation v0.3

Status: planning baseline  
Base: current `main` after agent harness, runtime observability, OpsHistory, reasoning, Agent Machine, local runtime, browser, and shell receipt tranches.

## Purpose

This note reconciles the proposed execution-control contract pack with the newer contract families already present in `sourceos-spec`.

The goal is to avoid duplicate schema classes while preserving the missing control-plane vocabulary needed by downstream consumers.

## Upstream families already present

Recent upstream work already covers several adjacent domains:

- Agent harness execution receipts: local runtime, shell, browser, host mutation, and download artifact receipt boundaries.
- Runtime observability and capability governance: capability ledger, browser automation receipt, Git workspace state, orphan event receipt, and runtime install receipt.
- OpsHistory: local-first operational history and redaction vocabulary.
- Reasoning contracts: reasoning event, run, receipt, replay plan, and benchmark surfaces.
- Agent Machine / model carry projections: model residency, inference provider, placement facts, and machine receipts.
- Local runtime, browser history, shell receipt, and local-first service manifest surfaces.

## Reuse-first decisions

| Need | Reuse existing upstream surface | Net-new surface only if needed |
|---|---|---|
| Runtime receipt / execution proof | `AgentHarnessExecutionReceipts`, `RunRecord`, `SessionReceipt`, `TruthSurface`, `DeltaSurface` | No new generic run receipt in this tranche |
| Browser, shell, terminal, host, and download evidence | Existing local-runtime, browser/shell, OpsHistory, and runtime observability receipts | No generic replacement evidence schema in this tranche |
| Capability truth after reconciliation | `CapabilityLedger`, `Policy`, `PolicyDecision`, `CapabilityToken` | Optional `ToolExposurePolicy` for presentation-layer tool visibility only |
| Workflow / validation program shape | `WorkflowSpec`, `WorkflowNode`, `WorkflowEdge`, `SkillManifest` | No new `ValidationProgram` schema in this tranche |
| Agent skill packaging | `SkillManifest` | No new `AgentSkillBundle` schema in this tranche |
| Lightweight environment fork | No exact current top-level schema | `ExecutionFork` remains net-new |
| Request/session routing into a fork | No exact current top-level schema | `RoutingContract` remains net-new |
| Team/developer runtime quota controls | No exact current top-level schema | `QuotaPolicy` remains net-new |
| Runner image and primitive bundle | No exact current top-level schema | `RunnerGroup` remains net-new |
| Protocol server test harness | No exact current top-level schema | `ProtocolWorkbench` remains net-new |
| Generic artifact index | Partly covered by download/runtime receipts and Memory Mesh pointers | Defer `ArtifactDescriptor` until it aligns with existing artifact-pointer conventions |

## Proposed v0.3 net-new tranche

Add only these top-level schemas first:

1. `ExecutionFork`
2. `RoutingContract`
3. `ToolExposurePolicy`
4. `QuotaPolicy`
5. `RunnerGroup`
6. `ProtocolWorkbench`

Defer or profile instead of adding:

- `CapabilityPolicy`: use existing `Policy`, `PolicyDecision`, `CapabilityToken`, and `CapabilityLedger` until a genuine missing shape is proven.
- `ArtifactDescriptor`: reconcile first with AgentHarness download artifact receipts, RuntimeInstall receipts, and Memory Mesh artifact pointer conventions.
- `ValidationProgram`: profile `WorkflowSpec`.
- `AgentSkillBundle`: profile `SkillManifest`.
- `GovernedRun`: profile `RunRecord` and `AgentHarnessExecutionReceipts`.
- `CairnEvidenceManifest`: profile `TruthSurface`, `DeltaSurface`, and existing provenance/receipt contracts.

## Downstream alignment

- `SocioProphet/agentplane`: consume `ExecutionFork`, `RoutingContract`, `RunnerGroup`, and `ProtocolWorkbench` as runtime orchestration inputs.
- `SocioProphet/policy-fabric`: consume `ToolExposurePolicy` and `QuotaPolicy`; continue using existing policy decision/token flows for authority.
- `SocioProphet/TriTRPC`: bind routing/workbench/session events to protocol frames.
- `SourceOS-Linux/openclaw`: consume `ProtocolWorkbench` and `ToolExposurePolicy` for agent workbench and skill execution defaults.
- `SourceOS-Linux/agent-term`, `TurtleTerm`, `sourceos-shell`, `BearBrowser`, and `agent-machine`: continue emitting the receipt families already added upstream.
- `SociOS-Linux/workstation-contracts`: publish a workstation-safe subset profile.
- `SocioProphet/socioprophet-agent-standards`: own conformance profiles, not canonical schemas.

## Non-goals

- No ADR in this tranche.
- No replacement of current receipt or runtime-observability families.
- No direct external-system wire compatibility promise.
- No catalog count update until the exact schema tranche stabilizes.

## Validation plan

1. Add schemas and examples for the six net-new top-level objects.
2. Add focused validators only after the shape stabilizes.
3. Add OpenAPI/AsyncAPI patch entries later, when runtime producers are ready.
4. Add derived profiles in downstream standards repos after canonical merge.
