# Reasoning Run Contract Additions

This tranche adds the first canonical SourceOS/SociOS contracts for governed recursive reasoning runs.

## Purpose

The Superconscious reference loop needs a contract family that can be consumed by AgentPlane, SocioSphere, sourceosctl, Agent Machine, Model Router, Policy Fabric, Agent Registry, and product surfaces without making Superconscious the schema authority.

These contracts define safe operational traces and evidence-backed reasoning coordination. They do not require raw private reasoning content.

## Added schemas

| Schema | URN prefix | Purpose |
|---|---|---|
| `ReasoningRun` | `urn:srcos:reasoning-run:` | Top-level record for a governed recursive reasoning run. |
| `ReasoningEvent` | `urn:srcos:reasoning-event:` | Safe operational trace event emitted during a reasoning run. |
| `ReasoningReceipt` | `urn:srcos:receipt:reasoning:` | Final receipt for a reasoning run. |
| `ReasoningReplayPlan` | `urn:srcos:reasoning-replay-plan:` | Replay classification and replay input/constraint record. |
| `ReasoningBenchmark` | `urn:srcos:reasoning-benchmark:` | Evidence-backed benchmark result for a reasoning run. |

## Boundary

Superconscious remains the reference cognition loop. It should consume these schemas after this tranche lands.

Authority remains distributed:

- `SourceOS-Linux/sourceos-spec` owns canonical schemas and semantic vocabulary.
- `SocioProphet/agentplane` owns execution, evidence sealing, placement, and replay authority.
- `SocioProphet/sociosphere` owns workspace topology, manifests, locks, registry governance, and validation lanes.
- `SourceOS-Linux/agent-machine` owns runtime planning and activation posture.
- `SocioProphet/model-router` owns model route decisions.
- `SocioProphet/guardrail-fabric` / Policy Fabric owns policy admission.
- `SocioProphet/agent-registry` owns agent identity and grants.

## Safe trace rule

Reasoning contracts expose safe operational traces only. They may include task state, event summaries, adapter records, policy/model/memory/approval posture, evidence references, replay class, and benchmark status.

They must not depend on raw private reasoning content.

## Open item

The Superconscious draft `AdapterDecision` object is conceptually useful, but connector-side filtering blocked direct promotion during this tranche. The current canonical schemas therefore model adapter records as structured objects inside `ReasoningRun` and coordination summaries inside `ReasoningReceipt`. A future tranche can promote a narrower `ReasoningStepDecision` or equivalent object if needed.
