# Execution Control Contract Pack v0.2

This note captures the first tranche of net-new execution-control contracts for `sourceos-spec`.

## Why this tranche exists

The current contract registry already contains nearby execution and agent-plane primitives such as:

- `WorkflowSpec`
- `RunRecord`
- `SkillManifest`
- `ExecutionDecision`
- `ExecutionSurface`
- `TruthSurface`
- `DeltaSurface`

To avoid duplicate object classes, this tranche adds only the primitives that do not yet have a clean canonical representation in the spec layer:

- `ExecutionFork`
- `RoutingContract`
- `CapabilityPolicy`
- `ToolExposurePolicy`
- `QuotaPolicy`
- `RunnerGroup`
- `ProtocolWorkbench`
- `ArtifactDescriptor`

## Intended reuse map

- Validation programs continue to profile or extend `WorkflowSpec`.
- Agent skill packaging continues to profile or extend `SkillManifest`.
- Runtime execution receipts continue to profile or extend `RunRecord`.
- Evidence promotion and drift continue to use `TruthSurface` and `DeltaSurface`.

## Downstream consumers

These schemas are intended to be consumed by:

- `SocioProphet/agentplane`
- `SocioProphet/policy-fabric`
- `SocioProphet/TriTRPC`
- `SociOS-Linux/workstation-contracts`
- `SourceOS-Linux/openclaw`
- `SocioProphet/socioprophet-agent-standards` (profile/conformance layer)

## Follow-on work

1. Add examples for all new schemas.
2. Update `schemas/README.md`, `examples/README.md`, and root `README.md` schema counts and family tables.
3. Add OpenAPI / AsyncAPI patch entries where the runtime surfaces stabilize.
4. Add derived profiles in `socioprophet-agent-standards`.
5. Wire consumer implementations in `agentplane`, `policy-fabric`, `TriTRPC`, `workstation-contracts`, and `openclaw`.
