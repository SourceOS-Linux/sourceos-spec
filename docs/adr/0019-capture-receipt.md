# ADR-0019: CaptureReceipt — the universal bind-purpose-before-f() primitive

Status: Accepted
Date: 2026-08-03
Relates-to: ADR-0014 (multiverseal twin identity)

## Context

Epoch E13 / workstream WS-B. `TwinAttestation.envelope.authorization` already binds a
declared purpose + proof at ingest, but only inside the twin family. The reidentification-
economy result makes that binding a universal necessity, not a twin-local nicety: purpose is
provably **unrecoverable** from the signal — the mutual information `I(purpose; Q)` between a
purpose bit and a quasi-identifier-bearing signal `Q` is `0`. So purpose cannot be inferred
after the fact; it has to be bound BEFORE the transform `f()` runs, at capture, or it is gone.
We need one domain-agnostic object that seals it — for any capture, not just twins.

## Decisions

1. **`CaptureReceipt` generalizes the twin authorization** into a standalone contract:
   `declaredPurpose` + `authorizationProof` + `boundBeforeTransform: true`, gating a named
   `transform` (the `f()`), optionally bound against a `contextRef` (reference-at-ingest / VRF).
2. **Fail-closed.** `disposition ∈ {admitted, refused, inert}`. A receipt with a missing/empty
   purpose or proof MUST be `refused` or `inert` — you cannot be `admitted` without a bound
   purpose+proof. Enforced in-schema (required fields) and machine-checked by the validator.
3. **Ties to WS-D.** `reversibilityFloorBits` records the reversibility-distance floor this
   capture re-establishes, linking WS-B to `ReversibilityDistance`.
4. Canonical examples (`capture_receipt.json` admitted, `capture_receipt_refused.json` refused)
   and an invariant validator wired into `make validate`.

## Consequences

- A single primitive now carries the capture-time purpose bit across every domain; the twin's
  `envelope.authorization` becomes one specialization of it rather than the only home.
- The purpose bit is sealed where it is the only place it can live — at capture — closing the
  post-hoc-inference gap the reidentification result proves is otherwise unrecoverable.
- Downstream consumers can gate `f()` on a resolvable receipt and refuse fail-closed.
