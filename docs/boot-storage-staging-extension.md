# Boot / storage / staging extension

This note explains the first SourceOS substrate extension added to the typed contract layer.

## Added contracts

The initial extension introduces:

- `BootSurface`
- `StorageSurface`
- `StagedDeployment`

These objects support a workstation or edge substrate lane where a host baseline is promoted through a staged control-plane flow rather than mutated directly.

## Why these contracts exist

The existing spec already models metadata, governance, execution, agent sessions, and release receipts. The substrate lane needed typed objects that describe:

- the boot-facing operational surface,
- the storage and mount-surface policy view,
- the staged deployment object that ties host, stage lane, and promotion policy together.

## Intended consumers

- `SociOS-Linux/SourceOS` — substrate implementation
- `SociOS-Linux/workstation-contracts` — workstation lane conformance
- `SocioProphet/agentplane` — stage bundle execution and evidence
- `SocioProphet/sociosphere` — workspace/controller integration metadata

## Near-term next spec work

Follow-on work should decide whether to:

- add API resources for these objects,
- add event channels for stage/promote/rollback transitions,
- reuse existing receipt surfaces or introduce substrate-specific receipts only where necessary.
