# MeshSkill Descriptor Specification v0.1

Status: draft

## 1. Scope

This specification defines the `MeshSkill` descriptor used by the validation and control plane. A MeshSkill is a typed, versioned, policy-bound capability object for hard-lane execution. It exists to make validation, simulation, replay, verification, and bounded commitment explicit, schedulable, and replayable.

This document is normative unless marked otherwise.

## 2. Goals

The descriptor MUST:

- make execution intent explicit;
- bind execution to typed coordinates;
- declare action composition or plan references;
- declare inputs, outputs, and side-effect class;
- define evidence obligations;
- support policy admission and approval gating;
- support deterministic replay and auditing.

The descriptor SHOULD:

- be signable and Merkle-addressable;
- be compatible with capability-descriptor registries;
- support cross-node and cross-cluster execution via TriTRPC;
- remain transport-neutral above the action envelope layer.

The descriptor MUST NOT:

- grant implicit authority outside declared coordinates;
- hide side effects behind untyped plugins;
- permit promotion without evidence;
- treat success/failure flags as sufficient evidence.

## 3. Object shape

A MeshSkill is a resource with `metadata` and `spec` sections.

### 3.1 Metadata

`metadata.id` is the canonical skill identifier. It SHOULD follow the braided naming model used across registries.

`metadata.merkle_root` is the content commitment for the descriptor and referenced in-registry normalization rules.

`metadata.signer` identifies the entity that signed or published the descriptor.

Additional metadata MAY include ownership, publication scope, lifecycle state, and lineage.

### 3.2 Spec

The `spec` section defines execution semantics.

Required fields:

- `lane`
- `class`
- `coordinates`
- `actions` or `plan`
- `inputs`
- `outputs`
- `evidence`

Optional but strongly recommended fields:

- `policy`
- `side_effects`
- `risk`
- `attestation`
- `timeouts`
- `budgets`

## 4. Lane

`spec.lane` identifies the execution lane.

Allowed values in v0.1:

- `hard`

Future values may exist for descriptive compatibility, but a MeshSkill governed by this specification is intended for hard-lane execution. Soft-lane operations are not represented as MeshSkill execution rights.

## 5. Skill classes

`spec.class` MUST be one of:

- `read`
- `replay`
- `simulate`
- `verify`
- `commit`

## 6. Coordinates

`spec.coordinates` binds where and under what trust conditions a skill may execute. Coordinates MUST be machine-checkable.

Recommended fields in v0.1:

- `env`
- `topology_scope`
- `trust_class`
- `tenant_scope`
- `frontier_hops`
- `data_sensitivity`

## 7. Actions and plans

A MeshSkill MUST define either ordered `actions` or a `plan` reference / embedded plan object.

## 8. Inputs and outputs

`spec.inputs` defines required external materials or references.

`spec.outputs` defines the durable outputs expected from successful execution.

## 9. Evidence obligations

`spec.evidence.require` lists evidence artifacts that MUST exist for the run to satisfy the descriptor.

## 10. Policy section

`spec.policy` declares local constraints and default execution rules. Platform policy overlays MAY narrow execution further but MUST NOT broaden execution beyond what the descriptor declares.

## 11. Side effects

A descriptor SHOULD declare intended side-effect class explicitly.

## 12. Risk and approval

Commit-class skills SHOULD include stricter approval and evidence requirements.

## 13. Invariants

1. A MeshSkill MUST have an identifier.
2. A MeshSkill MUST declare a class.
3. A MeshSkill MUST bind coordinates.
4. A MeshSkill MUST define actions or plan.
5. A MeshSkill MUST define inputs and outputs.
6. A MeshSkill MUST define required evidence.
7. A MeshSkill MUST be rejected if requested execution exceeds declared coordinates.
8. A MeshSkill MUST NOT promote claims without required evidence.
9. A commit-class MeshSkill MUST NOT execute without satisfying approval policy.
10. Every admitted run MUST be traceable through events and cairn references.
