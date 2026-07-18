# Design: CRDT merge over the reasoning-evidence fabric

**Status:** draft / spec-first
**Conforms to:** `sourceos-spec` v2 — `EventEnvelope.json`, `ReasoningRun.json`, `ReasoningEvent.json`, `SyncCycleReceipt.json`
**Closes local-first ideals:** 2 (multi-device), 3 (offline), 4 (collaboration) — **without regressing** 5 (longevity), 6 (privacy), 7 (user-control)
**Adds:** the eighth ideal — *correctness* — as a merge precondition, not an afterthought

---

## 1. Problem

Our stack scores green on the local-first ideals of Longevity / Privacy / User-control and **red on Multi-device / Collaboration** (Table 1 self-scorecard). Those two red cells are exactly what CRDTs were invented to close. We already emit the substrate: an append-only, hash-linked `EventEnvelope` log (Figure 18's "railroad track"). We are missing **merge semantics** over the derived store (the personal-knowledge-graph / workspace) so that two offline replicas converge on reconnect.

Non-goal: real-time OT/cursors. Goal: **asynchronous, offline-first convergence** of an edge-first graph, with no central authority (preserves privacy/control).

## 2. Why this is accretive, not a rewrite

- The personal-knowledge-graph is already a **Layer-2 derived, rebuildable, edge-first store**. A derived store is the ideal CRDT target: state = deterministic fold over an op-log.
- The op-log already exists as `EventEnvelope` messages. We do **not** add a new transport or wrapper.
- No central server is introduced → ideals 6/7 (privacy/user-control) are untouched by construction.

## 3. CRDT model

**Type:** op-based (CmRDT) **add-wins Observed-Remove graph** — an OR-Set of nodes ∪ an OR-Set of edges. Add-wins because in a knowledge graph a concurrent assert+retract should retain the assertion (retraction requires observing the specific add).

**Op = one `EventEnvelope`.** Mapping (all conformant, `additionalProperties:false` respected):

| EventEnvelope field | CRDT meaning |
|---|---|
| `eventId` (`urn:srcos:event:<uuid>`) | globally-unique op id / OR-Set unique tag |
| `eventType` | `GraphNodeAsserted` \| `GraphNodeRetracted` \| `GraphEdgeAsserted` \| `GraphEdgeRetracted` |
| `objectId` | URN of the node/edge the op mutates |
| `actor.subjectId` | replica / author identity |
| `occurredAt` | wall-clock (display only — **not** used for ordering) |
| `integrity.eventHash` | content hash; forms the hash-DAG (railroad track) |
| `payload` | the op body **+ causal metadata** (see §4) |

**Convergence:** merge = set-union of op-logs, then deterministic fold. OR-Set + add-wins is commutative/associative/idempotent → **strong eventual consistency** with zero coordination. That's the physics-aligned property from turn 1: no critical-path round-trip needed to converge.

## 4. Causality without a schema change

`EventEnvelope` is `additionalProperties:false`, but `payload` is `additionalProperties:true`. All causal metadata rides in `payload`:

```jsonc
"payload": {
  "op": "GraphEdgeAsserted",
  "edge": { "from": "urn:...", "rel": "cites", "to": "urn:..." },
  "crdt": {
    "replicaId": "urn:srcos:replica:<device>",
    "lamport": 421,                 // total-order tiebreak
    "parents": ["<eventHash>", ...],// hash-DAG causal parents (Fig 18 lineage)
    "removes": ["urn:srcos:event:<addTag>"] // OR-Set: for retract ops only
  }
}
```

- **Ordering:** hash-DAG parents give the partial (causal) order; `lamport` + `eventId` break ties deterministically. `occurredAt` is never trusted for ordering (clocks lie — turn-1 lesson).
- **Retraction:** an OR-Set remove names the exact add-tags it observed → concurrent re-adds survive (add-wins).

## 5. The eighth ideal: correctness as a merge precondition

This is the part local-first (2019) never had, and our moat. Each op carries the **locus it was authored/attested at**, reusing `SyncCycleReceipt.locus` verbatim:

```jsonc
"crdt": {
  "locus": "trusted_private",      // local | trusted_private | attested_fog | burst_cloud
  "attestationRef": "urn:srcos:reasoning-receipt:...", // correctness-gate result, if any
  "trustLevel": "trusted-workspace-source"             // from ReasoningEvent vocab
}
```

**Merge gate (fail-closed):**
- Ops from `local` / `trusted_private` merge into the **canonical view**.
- Ops from `attested_fog` / `burst_cloud` merge into canonical **only if** `attestationRef` resolves to a passing correctness-gate receipt; otherwise they land in a **quarantine view** (mirrors the existing `QuarantineReceipt` pattern) and surface for review.
- The CRDT still *converges* on all ops (longevity: nothing is lost); the **gate decides which converged sub-graph is authoritative.**

This is the key inversion: CRDTs guarantee *everyone sees the same graph*; our correctness gate decides *which part of that graph is trusted*. No competitor's local-first sync has this second layer.

## 6. Receipts / evidence

- Each merge cycle emits a receipt modeled on `SyncCycleReceipt` (reuse `cycleId`, `fromVersion`/`toVersion` = pre/post graph state hashes, `locus`, `outcome`, `auditId`).
- Optionally bind to a `ReasoningRun` via `agentplaneRunRef` when the merge was triggered by an agent task, so the graph's evolution is replayable on the same spine as reasoning.

## 7. Ideal-by-ideal effect

| Ideal | Before | After | Mechanism |
|---|---|---|---|
| 2 Multi-device | ● | ✓ | OR-Set converges across replicas |
| 3 Offline | ✓/– | ✓ | ops authored offline, merge on reconnect |
| 4 Collaboration | ● | ✓/– | async convergence (not live cursors) |
| 5 Longevity | ✓ | ✓ | op-log *is* the durable history (unchanged) |
| 6 Privacy | ✓/– | ✓/– | no central authority introduced |
| 7 User-control | ✓ | ✓ | locus-gated, replica-owned |
| **8 Correctness** | — | ✓ | **new**: attestation-gated canonical view |

## 8. Build slices (each shippable, ordered)

1. ✅ **Op emitter** — write PKG mutations as `EventEnvelope` ops with `crdt` payload. (No merge yet; just dual-write.) — *landed: prophet-mesh#13 `pkg_ops.py`, 5 tests.*
2. ✅ **Deterministic fold** — rebuild graph state from the op-log; assert it matches current derived store (regression gate). — *landed as `materialize()`; `test_materialize_matches_live_graph`.*
3. ✅ **OR-Set merge** — union two replicas' logs, prove convergence (property test: commutativity/idempotence over random op interleavings). — *landed: `merge()` + add-wins retracts; 9 tests incl. offline convergence, random-shuffle order-independence, add-wins-over-concurrent-retract. Suite 74 green.*
4. ✅ **Locus/attestation gate** — canonical vs. quarantine view split; emit `SyncCycleReceipt`-shaped merge receipts. — *landed: `pkg_gate.py` `gate()`, fail-closed admission + untrusted-retract security property + SyncCycleReceipt v2 conformance; 7 tests. Suite 81 green.*
5. ✅ **Live ingester** — second device / agent as a real second replica. — *landed: `pkg_replica.py` `Replica` + anti-entropy `sync()` + `replay_to_hellgraph()` (closes the emit-only gap) + `persist_canonical()` (only the gated-canonical graph reaches HellGraph); 6 tests. Suite 87 green.*

**All 5 slices landed** (prophet-mesh#13, 27 CRDT tests, suite 87 green). The design is end-to-end real: emit → reconstruct → converge → gate on correctness → live-sync + persist only the proven-correct sub-graph.

## 9. Open questions

- Compaction/GC of the op-log at scale (tombstone horizon) vs. the longevity ideal — needs a retention/retraction policy (ties to the PKG retention open-loop already noted).
- Do agent replicas (multi-agent swarm) each get a `replicaId`, making swarm output a first-class merge participant? (Likely yes — unifies "collaboration" across humans + agents.)
- Whether `attestationRef` resolution happens at merge time (strict) or lazily (converge-then-attest). Recommend strict for `burst_cloud`, lazy for `attested_fog`.
