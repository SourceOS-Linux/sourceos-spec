# OpenClaw boundary and handoff placement

This document defines where OpenClaw-related contract work belongs inside the SourceOS / SociOS typed-contract lane.

## Position

OpenClaw is not the SourceOS control plane, not the policy canon, and not the durable truth surface.

Within the SourceOS ecosystem, OpenClaw is treated as a **bounded local agent cell** that may prepare artifacts, emit audit records, and hand work into other controlled planes.

That means this repository does **not** describe how to deploy OpenClaw on Linux hosts. That deployment guidance belongs in the Linux realization lane.

This repository instead owns the **contract layer** for any artifacts that cross the boundary between an OpenClaw cell and the broader SourceOS system.

## What belongs here

The typed-contract lane is the correct home for machine-readable definitions of OpenClaw-adjacent artifacts such as:

- gateway or cell descriptors
- tool invocation audit events
- model route records
- input and output artifact references
- approval records
- handoff manifests
- effect records
- restore handles
- policy evaluation receipts triggered by OpenClaw-prepared actions

If a SourceOS implementation needs to validate, replay, compare, store, or exchange one of those objects, the shape belongs here.

## What does not belong here

The following do not belong in this repository:

- Linux service modules
- host-level placement rules
- filesystem layout decisions
- loopback bind defaults
- container or VM isolation instructions
- package manager integration
- browser sandbox setup

Those belong in the Linux realization lane.

## Contract rule

OpenClaw outputs are not trusted merely because they were produced locally.

For SourceOS purposes, any meaningful OpenClaw-produced action must be representable as explicit objects with enough structure for:

- validation
- review
- evidence storage
- replay
- comparison
- approval tracking
- restoration or reversal analysis

## Initial contract candidates

The first contract candidates that should eventually be formalized here are:

### 1. OpenClawCell
Minimal identity and placement metadata for a bounded local agent cell.

Suggested fields:

- `cellId`
- `trustBoundaryId`
- `actorId`
- `hostClass`
- `runtimeClass`
- `toolPolicyRef`
- `modelPolicyRef`
- `networkPolicyRef`
- `createdAt`

### 2. ToolInvocationRecord
A typed record for one tool action prepared or executed by the cell.

Suggested fields:

- `invocationId`
- `cellId`
- `toolName`
- `mode` (`read`, `draft`, `write`, `external`)
- `inputRefs[]`
- `outputRefs[]`
- `startedAt`
- `endedAt`
- `status`
- `effectSummary`

### 3. ModelRouteRecord
A typed record of which model path was used.

Suggested fields:

- `routeId`
- `cellId`
- `providerClass` (`local`, `remote`, `hybrid`)
- `modelName`
- `embeddingMode`
- `browserMode`
- `policyDecisionRef`
- `timestamp`

### 4. HandoffManifest
A typed object representing the explicit boundary crossing from a local OpenClaw cell into another SourceOS surface.

Suggested fields:

- `handoffId`
- `sourceCellId`
- `targetSurface`
- `artifactRefs[]`
- `approvalState`
- `policyDecisionRef`
- `evidenceRefs[]`
- `restoreRef`
- `timestamp`

### 5. EffectReceipt
A typed record for downstream effects caused by an approved OpenClaw-prepared action.

Suggested fields:

- `receiptId`
- `handoffId`
- `result`
- `mutatedObjects[]`
- `evidenceRefs[]`
- `rollbackAvailable`
- `rollbackRef`
- `timestamp`

## Repository relationship

The intended split is:

- `SociOS-Linux/source-os` — Linux realization, host placement, service modules, profiles, tests
- `SourceOS-Linux/sourceos-spec` — machine-readable contract shapes for cross-boundary objects
- `SocioProphet/sourceos-workspace` — cross-repo planning, ownership maps, bootstrap tasks, sequencing
- `SociOS-Linux/socios` — opt-in automation commons and community-facing handoff policy

## Immediate implication

Before OpenClaw is wired into any automation path, the handoff objects need to be explicit. Otherwise the system collapses into session trust and informal logs.

The SourceOS position is the opposite: explicit objects first, informal convenience later.

## Initial backlog

1. reserve a schema family lane for local agent-cell boundary objects
2. define `HandoffManifest` and `EffectReceipt` before any automation integration
3. keep deployment doctrine and host instructions out of this repo
4. align event and receipt objects with the existing event, provenance, and release schema families
5. require that any future OpenClaw integration reference these typed objects rather than inventing ad hoc JSON in runtime code

## Bottom line

If the question is “where does OpenClaw runtime doctrine live?”, the answer is `source-os`.
If the question is “where do the durable boundary-crossing objects live?”, the answer is `sourceos-spec`.