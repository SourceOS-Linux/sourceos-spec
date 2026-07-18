# Semantic Evidence Chain (SEC)

Status: draft
Scope: a directed, weighted analytic view onto the reasoning-evidence fabric (ReasoningRun / ReasoningEvent / ReasoningReceipt) that feeds image-gen red-team and blue-team detection playbooks, containment, and forensic capture.

## Scope discipline

SEC formalizes only falsifiable graph and evidence semantics. The "ghost space" topology and geometry framing that motivated this contract is **metaphor only** and is explicitly out of scope. This spec defines no physical quantities, no E8 or Hopf projections, no tensor fields, and no derived geometry. Every number in an SEC is an observed or estimated analytic over fabric events, never a computed physics result.

## Thesis

A reasoning or detection process is a walk through states of awareness. Each state is grounded in a recorded reasoning-evidence event. The transitions between states carry evidence: how clearly the transition is supported, how much uncertainty it removed, and how much time it cost. Reading those transitions as a directed weighted graph lets us score how a system arrived at awareness, where it branched into competing hypotheses, where it looped, and where competing paths converged on a single verdict.

SEC is that graph. It is a **derived view**, not a new evidence store. It binds every node and edge back to the canonical fabric so that any SEC claim is traceable to a `ReasoningEvent` and ultimately to a `ReasoningReceipt`.

## Data model

`SEC = (N, E, W)`

- **N — nodes**: awareness/detection states. Each node binds to exactly one `ReasoningEvent` via `eventRef`. `kind` is `awareness` (cognitive/reasoning state) or `detection` (security observation state). A node never upgrades trust above its bound event.
- **E — directed edges**: state transitions, tail `from` to head `to`. `transition` is one of `advance` (linear), `branch` (divergence, >1 outgoing), `loop` (entanglement, returns to an ancestor), `converge` (inbound at a node with >1 distinct-path predecessor). An edge MAY bind an `eventRef` evidencing the transition itself.
- **W — weight vector** (per edge): `{ clarity, entropyReduction, temporalCost }`.
  - `clarity` ∈ [0,1] — confidence the transition is well-evidenced, from bound-event trust level and corroboration count.
  - `entropyReduction` ≥ 0 — reduction in candidate-state uncertainty, in bits, over the run's hypothesis set. Information-theoretic analytic, not physics.
  - `temporalCost` ≥ 0 — elapsed cost in milliseconds, from bound-event timestamps.

Full awareness is a **convergence path**: a directed path that reaches a converge node, scored by cumulative W.

Schema: `schemas/SemanticEvidenceChain.json`. Example: `examples/semantic_evidence_chain.json`.

## Binding to the reasoning-evidence fabric

SEC is a conformant projection, not a parallel store:

| SEC field | Fabric binding |
|---|---|
| `SEC.runRef` | `ReasoningRun.id` (`urn:srcos:reasoning-run:`) |
| `SEC.receiptRef` | `ReasoningReceipt.id` (`urn:srcos:receipt:reasoning:`) |
| `node.eventRef`, `edge.eventRef` | `ReasoningEvent.id` (`urn:srcos:reasoning-event:`) |
| `node.trustLevel` | mirrors `ReasoningEvent.trustLevel` |
| `SEC.traceLevel` | the most restricted bound `ReasoningEvent.traceLevel` |

Rules:

1. An SEC MUST NOT exist without a parent `ReasoningRun`.
2. Every node and every weighted edge MUST be reconstructable from bound fabric events; SEC stores no evidence the fabric does not already hold.
3. SEC honors the fabric's safe-trace boundary: it never requires raw private reasoning content, only event summaries, trust levels, trace levels, and timestamps.
4. `SEC.analysis` is an advisory cache. It is always recomputable from `nodes` + `edges`; a consumer MUST be able to discard and recompute it.

## Operations

All operations are pure functions over `(N, E, W)`.

1. **build-chain(run)** — project a `ReasoningRun` and its `ReasoningEvent` set into `(N, E)`. One node per event; one edge per recorded state transition. Compute each edge's W from bound-event trust level (clarity), hypothesis-set delta (entropyReduction), and timestamp delta (temporalCost). Set `traceLevel` to the most restricted bound event.
2. **score-path(path)** — fold W along an ordered node path: `clarity` = product of edge clarities, `entropyReduction` = sum, `temporalCost` = sum. Returns a cumulative weight vector.
3. **detect-divergence(SEC)** — return nodes with >1 outgoing `branch` edge. Each is a competing-hypothesis fork.
4. **detect-loop(SEC)** — return cycles reachable via `loop` edges (entanglements): a state that re-enters an ancestor. Used to flag non-terminating reasoning and repeated detection re-triggering.
5. **find-convergence(SEC)** — find converge nodes (>1 distinct-path predecessor); among inbound paths select the one maximizing `clarity × entropyReduction` while bounding `temporalCost`. The winning ordered path is the full-awareness path; its score-path output is `analysis.cumulativeWeight`.

## Mapping to the Linux image-gen red/blue playbooks

The image-gen pipeline (imagelab / image-builder) emits reasoning-evidence events during build, scan, and review. SEC turns those events into actionable security graphs across three lanes; `analysis.playbookLane` records the selected lane.

- **Detection coverage (blue-team).** `detect-divergence` surfaces every competing explanation a detector entertained for a suspicious image artifact (e.g. an unexpected post-install layer mutating a shell startup file). Branches that never reach a converge node are **uncovered hypotheses** — coverage gaps to add detectors for. `find-convergence` yields the confirmed verdict path with its cumulative clarity.
- **Containment.** A converge node carrying high cumulative `clarity` and a `detection` verdict is the trigger to quarantine. SEC pairs naturally with `SecurityVerdictState` (the converge node's verdict) and `QuarantineReceipt` (the containment action), both referenced by the bound run's evidence pointers.
- **Forensic capture.** The full SEC, with its hash-linked binding to `ReasoningEvent` and the sealing `ReasoningReceipt.traceHash`, is the forensic artifact: a replayable, append-only account of how awareness of the threat was reached, including dead-end branches and any loops (re-triggered detections).
- **Red-team.** Run SEC over an adversarial build. A short convergence path with low `entropyReduction` means the injected artifact was caught quickly with little investigation; a long path with many `branch` divergences and `loop` entanglements means the attack induced expensive, uncertain reasoning — a detector-quality signal to harden.

### Threat-detection mapping

- A `loop` cycle = repeated re-triggering or oscillating hypotheses → detector instability.
- A `branch` with no downstream converge = an explanation the system could neither confirm nor rule out → blind spot.
- A converge node with low cumulative `clarity` = a verdict reached on weak evidence → escalate to review, do not auto-contain.
- Rising aggregate `temporalCost` to convergence across runs = detection latency regression.

## Required audit events

- `sec.chain.built`
- `sec.path.scored`
- `sec.divergence.detected`
- `sec.loop.detected`
- `sec.convergence.found`
- `sec.verdict.bound` (SEC convergence linked to a `SecurityVerdictState`)
- `sec.containment.triggered` (SEC convergence linked to a `QuarantineReceipt`)

## Dangerous anti-patterns

- Treating an SEC node as evidence in its own right rather than a view onto a `ReasoningEvent`.
- Storing reasoning content in SEC that the fabric does not hold (parallel evidence store).
- Upgrading a node's trust level above its bound event.
- Auto-containing on a converge node without checking cumulative `clarity`.
- Reading the chain's geometry as a physical or topological measurement.

## Acceptance criteria

1. Every SEC has a `runRef` to an existing `ReasoningRun`.
2. Every node and every weighted edge binds to a fabric event reconstructable from canonical schemas.
3. No SEC node has a trust level higher than its bound `ReasoningEvent`.
4. `analysis` is recomputable from `nodes` + `edges` and is never the sole source of any claim.
5. Every blue-team containment action triggered from an SEC references a `SecurityVerdictState` and a `QuarantineReceipt`.
6. Every divergence with no downstream convergence is reported as a detection-coverage gap.
7. No field in any SEC asserts a derived physical, topological, or geometric quantity.
