# Reasoning Run Contract Family

The reasoning run contract family defines canonical SourceOS/SociOS objects for governed recursive reasoning runs.

These contracts were introduced to move the Superconscious reference loop out of local draft-only artifact shapes and into the shared typed-contract layer.

## Schemas

| Schema | URN prefix | Purpose |
|---|---|---|
| `ReasoningRun.json` | `urn:srcos:reasoning-run:` | Top-level governed reasoning run record. |
| `ReasoningEvent.json` | `urn:srcos:reasoning-event:` | Safe operational trace event emitted during a reasoning run. |
| `ReasoningReceipt.json` | `urn:srcos:receipt:reasoning:` | Final receipt for a reasoning run. |
| `ReasoningReplayPlan.json` | `urn:srcos:reasoning-replay-plan:` | Replay classification and replay input/constraint record. |
| `ReasoningBenchmark.json` | `urn:srcos:reasoning-benchmark:` | Benchmark result for a reasoning run. |

## Examples

| Example | Schema |
|---|---|
| `examples/reasoning_run.json` | `ReasoningRun` |
| `examples/reasoning_event.json` | `ReasoningEvent` |
| `examples/reasoning_receipt.json` | `ReasoningReceipt` |
| `examples/reasoning_replay_plan.json` | `ReasoningReplayPlan` |
| `examples/reasoning_benchmark.json` | `ReasoningBenchmark` |

## Design intent

Reasoning contracts expose safe operational traces and evidence-backed coordination records. They do not depend on raw private reasoning content.

Expected consumers:

- `SocioProphet/superconscious` as the reference governed cognition loop;
- `SocioProphet/agentplane` for evidence and replay integration;
- `SocioProphet/sociosphere` for workspace validation and topology binding;
- `SourceOS-Linux/sourceos-devtools` for `sourceosctl reasoning ...` inspection and validation;
- `SourceOS-Linux/agent-machine` for future runtime-plan integration;
- product surfaces such as TurtleTerm, AgentTerm, BearBrowser, SocioSphere, and SocioProphet web.

## Safe trace boundary

A reasoning run may expose:

- task state;
- event summaries;
- trace level;
- trust level;
- adapter or coordination records;
- policy/model/memory/approval posture summaries;
- evidence references;
- replay class;
- benchmark result.

It must not require raw private reasoning content.

## Open item

The Superconscious local draft object currently called `AdapterDecision` was not promoted in this tranche. The canonical `ReasoningRun.adapterRecords` field intentionally accepts structured adapter records while we evaluate whether a narrower future schema such as `ReasoningStepRecord` is preferable.
