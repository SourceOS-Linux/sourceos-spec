# Skill Execution Lifecycle v0.1

Status: draft

## 1. Scope

This specification defines the end-to-end lifecycle for hard-lane MeshSkill execution in the control plane. It covers admission, orchestration, execution, evidence production, policy evaluation, truth-state impact, and commit gating.

The lifecycle exists so that agent-driven work remains bounded, attributable, and replayable.

## 2. Terms

- **proposal**: a candidate action, patch, investigation, or change request produced by a human or agent.
- **admission**: policy-governed authorization to start a skill run.
- **shadow cell**: a bounded validation environment with topological fidelity.
- **evidence bundle**: the durable artifact set emitted by a run.
- **promotion**: a status transition in the claim store based on policy and evidence.
- **commit**: an allowed side effect that changes external or durable state.
- **cairn**: a cryptographically committed checkpoint before or after a materially relevant transition.

## 3. Lifecycle states

A run SHOULD move through: `proposed`, `planned`, `resolved`, `admitted`, `materialized`, `running`, `evidence_collected`, `evaluated`, `approved|denied`, `promoted|rejected|committed`, `archived`.

## 4. End-to-end flow

1. Proposal
2. Planning
3. Resolution
4. Admission
5. Materialization
6. Execution
7. Evidence collection
8. Evaluation
9. Approval
10. Promotion and commit
11. Archival

## 5. Idempotence and retries

Retries MUST remain within declared policy and idempotency constraints. Commit-class retries MUST be conservative and SHOULD require explicit idempotency proof or human review.

## 6. Failure handling

Failure is evidence. The lifecycle MUST preserve failures as first-class outputs rather than merely log noise.

## 7. Truth-maintenance integration

A run result is not truth merely because it exists. Promotion requires provenance, evidence completeness, and satisfied policy.

## 8. Minimum artifacts per run

Every archived run MUST retain or reference:

- run identifier
- actor identity
- descriptor identifier and version
- resolved coordinates
- event trail
- evidence bundle
- policy decision
- approval record if applicable
- `cairn_before` and `cairn_after` when stateful execution occurred

## 9. Event set

The recommended event set for v0.1 includes:

- `skill.requested`
- `skill.planned`
- `skill.resolved`
- `skill.admitted`
- `skill.materialized`
- `skill.started`
- `action.started`
- `action.completed`
- `action.failed`
- `evidence.attached`
- `skill.evaluated`
- `policy.denied`
- `approval.requested`
- `approval.granted`
- `approval.denied`
- `claim.promoted`
- `claim.rejected`
- `claim.retracted`
- `commit.approved`
- `commit.executed`
- `commit.denied`
- `skill.archived`

## 10. Security invariants

1. No run may start without resolved coordinates.
2. No run may exceed descriptor-declared coordinate bounds.
3. No validated promotion may occur without required evidence.
4. No commit may occur without satisfying required approval policy.
5. Every state transition of consequence must be attributable.
6. Every materially stateful run must be replayable through cairn references and event lineage.
