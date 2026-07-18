# Systema: Projection Loss Mapping to SourceOS Typed Contracts

## What Systema defines

Systema's `projection_loss_profile.yaml` models the degradation between a source truth and its projected representation: information loss during transformation, summarization, embedding, or model inference. A `projectionLoss` score of 0.0 is lossless; 1.0 is total loss.

## Existing SourceOS/SociOS coverage

| Systema concept | SourceOS/SociOS schema | Key fields |
|---|---|---|
| Render-time projection state | `ReasoningAssay` | `projectedState`, `assay()` (recomputed from axes — not stored) |
| Transformation evidence | `ProvenanceRecord` | `transformationRef`, `method` |
| Session context boundary | `SessionReceipt` | `contextRef`, `boundaryPolicy` |
| Memory hydration staleness | `LocalReasoningFailure` | `contextHydrationBoundary.staleSinceEventTime` |

## Gap: projection-loss scalar on emitted artifacts

Systema tracks a per-artifact `projectionLoss` that has no direct field in current schemas. Additive resolution: `ReasoningAssay.binding` already encodes verifiability strength (a proxy for projection integrity). For cases where a numeric score is needed, add an optional `projectionLossScore: number` to `ReasoningReceipt.assay` — backward-compatible, not required.

## Mapping rules

1. Systema `projectionLoss > 0.3` on a model-derived value targeting an exactness-sensitive field → `LocalReasoningFailure.failureClass: stale-context-injection` must be raised.
2. Systema `projectionLoss > 0.7` → `ReasoningAssay.projectedState` must be `bad`; downstream systems must not apply the value to durable state.
3. Systema summarization boundary events map to `LocalReasoningFailure.contextHydrationBoundary.boundaryViolated: true`.
4. Lossless projections (score 0.0, cryptographic source) → `ExactnessArtifactRecord.admissionPolicy: cryptographic-proof`.

## No new schemas required

Projection-loss semantics are covered by `ReasoningAssay`, `ReasoningReceipt`, `LocalReasoningFailure`, and `ExactnessArtifactRecord`. Systema adapters emit these rather than separate projection-loss schemas.
