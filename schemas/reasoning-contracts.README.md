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
| `ReasoningAssay.json` | `urn:srcos:reasoning-assay:` | Typed epistemic verdict on a claim; ok/sad/bad is a render-time projection of five orthogonal axes. |
| `AssayStandard.json` | `urn:srcos:assay-standard:` | Measured, versioned reliability of a verifier — the calibration reference every assay is checked against. |

## Examples

| Example | Schema |
|---|---|
| `examples/reasoning_run.json` | `ReasoningRun` |
| `examples/reasoning_event.json` | `ReasoningEvent` |
| `examples/reasoning_receipt.json` | `ReasoningReceipt` |
| `examples/reasoning_replay_plan.json` | `ReasoningReplayPlan` |
| `examples/reasoning_benchmark.json` | `ReasoningBenchmark` |
| `examples/assay_standard.json` | `AssayStandard` |
| `examples/reasoning_assay.json` | `ReasoningAssay` (projects `ok`) |
| `examples/reasoning_assay.unassayed.json` | `ReasoningAssay` (projects `sad`) |
| `examples/reasoning_assay.refuted.json` | `ReasoningAssay` (projects `bad`) |

## Design intent

Reasoning contracts expose safe operational traces and evidence-backed coordination records. They do not depend on raw private reasoning content.

### The Assay: verdicts are projections, not scalars

`ReasoningAssay` records an epistemic verdict on a claim. Confidence, authenticity, and
verification-vs-generation are **orthogonal axes**, not points on one severity scale, so they are
stored separately and the `ok`/`sad`/`bad` readout is a render-time **projection** (`projectedState`),
never a stored opinion. The five axes:

1. **method** — `computed` / `retrieved` / `generated` (categorical; these behave as decorrelated classes).
2. **binding** — `inline` / `post-hoc` (was evidence produced with the computation, or attached after?).
3. **verifier** — points at an `AssayStandard` (the judge's *measured* reliability). A verdict without a
   calibration reference cannot project above `sad`.
4. **agreement** — decorrelation-weighted; correlated arms fail together, so `effectiveVotes` discounts raw arm count.
5. **authority** — authenticity as a property of the actor/channel (mirrors `EventEnvelope.actor`/`integrity`),
   never of the content.

Because the axes are stored, a verdict is **re-projectable**: when a verifier's `AssayStandard` improves,
historical assays re-project without mutating their records — the same discipline as keeping every benchmark
arm rather than only its current winner. `tools/validate_reasoning_examples.py` enforces this: it recomputes
`assay()` from the stored axes and fails CI if the recorded `projectedState` does not follow from them.

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
