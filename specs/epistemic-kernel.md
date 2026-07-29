# Epistemic-Kernel Contract Family v0.1

Status: v0.1 (tranche strictness bar). Issue: SourceOS-Linux/sourceos-spec#207.

## Why one family

Seven external architecture patterns were audited for adoption: a federated
resource-management loop, IBM HOPE's causal relation model, a PM-gated
multi-agent workflow, a living-wiki knowledge plane, an agent governance
runtime, Anthropic's contextual retrieval, and a distributed trainer/rollout
topology. Three of them (resource loop, governance runtime, trainer/rollout)
are the same closed loop drawn three times: **sense → decide under a versioned
policy → act through a gate → verify → record**. This family lands that loop
once, plus the claims-graph and evidence-preparation contracts the remaining
patterns need. One spec, many consumers — never three parallel vocabularies.

## Schemas

Loop side:

| Schema | Role |
| --- | --- |
| `ControlLoop` | Loop definition: domain (`compute`\|`governance`\|`learning`), digest-pinned policy, fail-mode, retry budget + mandatory escalation, single-entry scheduler arbitration, idle tick (no End state). |
| `ControlLoopTick` | Per-iteration record: pinned `policyDigest`, membrane `executionDecisionRef` on work ticks, ops ternary verdict (`ok`/`sad`/`bad`), receipt-backed, anomaly bookkeeping. |
| `ExperienceRecord` | Rollout/eval output pinned to the exact policy/model digest that generated it; named storage tiers (`durable`, `hot`); receipt-backed; idempotent. |
| `GuardrailEvalReport` | Per-clause enforcement evidence for one policy version; promotion requires full passing coverage; installation requires human blessing. |

Claims side (HOPE-derived, hardened):

| Schema | Role |
| --- | --- |
| `CausalHypothesis` | Direction-neutral falsifiable hypothesis node with topic terms (literal or typed template slot), optional KKO typing, ER-cluster resolution, warrant-backed claim lifecycle (`proposed`→`evidenced`→`scored`). |
| `CausalEdge` | Signed edge (polarity lives ONLY here) with optional weight/lag/confidence, **mandatory non-empty warrants**, digest-pinned extractor provenance. |

Evidence-preparation side:

| Schema | Role |
| --- | --- |
| `ChunkContext` | Contextual-retrieval situating context keyed by `docHash` for incremental invalidation; closed index-target set (`embedding`, `bm25`); digest-pinned generator provenance. |

## Deliberate deltas from the source patterns

1. **No End state.** The source resource loop terminates when no new data is
   available and its anomaly path never re-reaches the exit check (livelock).
   A `ControlLoop` is a service: idle ticks are first-class, the anomaly path
   carries a bounded retry budget, and escalation is mandatory at exhaustion.
2. **Single-entry arbitration.** The source diagram re-enters its scheduler
   from two uncoordinated feedback edges — a race by construction. v0.1 closes
   arbitration to `single-entry`.
3. **Digest pinning everywhere.** Policies, models, extractors, documents, and
   payloads are referenced by content digest, never by moving tag. A stale
   rollout worker is attributable; an unpinned one is not.
4. **Polarity on edges only.** HOPE bakes direction into some hypothesis texts
   ("will improve") while carrying dash-dot negative edges elsewhere. Here
   hypothesis text is direction-neutral and falsifiable; `CausalEdge.sign` is
   the only carrier of polarity.
5. **No unwarranted causality.** HOPE edges carry no provenance. `CausalEdge`
   requires at least one warrant, which is what makes the graph scoreable by
   the provenance-fidelity eval.
6. **Verdict discipline.** Loop ticks are operations and take the ops ternary
   (`ok`/`sad`/`bad`). Hypotheses are claims and take the 5-axis claims
   verdict. The two vocabularies never mix.
7. **Human gate on the eval→policy edge.** The source governance diagram feeds
   eval results back into policy with no human in the loop. Here
   `installApproved` requires a `blessing` block; eligibility is machine-side,
   installation is not.
8. **Enforcement, not declaration.** Every declared policy clause must map to
   an enforcement test exercised with a violating input (`GuardrailEvalReport`)
   — the declared-unenforced gap closed as a contract, with red-team vectors
   counted as a permanent input lane.
9. **BM25, not TF-IDF; invalidation by content hash.** `ChunkContext` pins the
   published contextual-retrieval method's actual lexical index and makes
   staleness impossible to hide: a new `docHash` orphans every context minted
   against the old one.

## Consumers

This repo owns the contracts; runtime behavior lives with consumers:

- **SocioProphet/socioprophet** — product surface where causal graphs land
  (the same landing pattern used for the IBM and GYG work).
- **SocioProphet/economic-prophet** — the causal engine: graph math, signed
  propagation, KPI rollup over `CausalHypothesis`/`CausalEdge`.
- **SocioProphet/profit-mpcc** — event-fabric origin; causal documents ride
  inside `EventEnvelope` on channels next to the MPCC conversation/trading
  family and reference `PolicyDecision`/`ExecutionDecision`/`EffectRecord`
  rather than duplicating them.
- **prophet-platform** — the `compute` ControlLoop instantiation.
- **guardrail-fabric / policy-fabric / model-governance-ledger** — the
  `governance` instantiation; the ledger anchors `policyDigest` history.
- **systems-learning-loops** — the `learning` instantiation
  (trainer/rollout over `ExperienceRecord`).
- **Retrieval stack (Noetica lane)** — `ChunkContext` producers/indexers under
  the fibered-retrieval gate.

## Non-goals

- No runtime behavior in this repository.
- No duplication of `Policy`, `PolicyDecision`, `ExecutionDecision`,
  `EffectRequest`/`EffectDecision`/`EffectRecord`, `ReasoningRun`,
  `ReasoningReceipt`, or `EvidenceAtom` — the family references them.
- No claim that any consumer has implemented these contracts until verified.

## Validation

```
make validate-epistemic-kernel-examples
```

Four checks: schema conformance, strictness bar, cross-invariants
(tick↔loop digest parity, retry-budget escalation, edge endpoint resolution
and self-loop rejection, guardrail coverage arithmetic), and negative
conformance vectors (`fixtures/epistemic-kernel/conformance.json`) that must
all fail for their stated reasons.
