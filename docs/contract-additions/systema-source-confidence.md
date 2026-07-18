# Systema: Source Confidence Mapping to SourceOS Typed Contracts

## What Systema defines

Systema's `source_confidence_profile.yaml` models the trustworthiness of a data source across axes: recency, provenance, verifiability, and authority. It produces a scalar confidence score and a named confidence tier (`high`, `medium`, `low`, `unverified`).

## Existing SourceOS/SociOS coverage

The following schemas already carry source-confidence semantics:

| Systema concept | SourceOS/SociOS schema | Key fields |
|---|---|---|
| Source provenance | `ProvenanceRecord` | `sourceRef`, `authorityRef`, `method`, `verifiedAt` |
| Confidence score on an event | `EventEnvelope` | `integrity`, `actor`, `authorityRef` |
| Verifier attestation | `ValidatorReceipt` | `decision`, `confidence`, `verifierRef`, `evidenceRefs` |
| Release-time source quality | `ReleaseReceipt` | `buildEvidenceRef`, `signatureRef` |
| Assay verdict | `ReasoningAssay` | `binding`, `method`, `agreement`, `authority`, `projectedState` |

## Gap: runtime source-confidence metadata on local objects

Systema's `source_confidence_profile.yaml` can emit per-object confidence tiers that are not currently surfaced in `ProvenanceRecord` or `EventEnvelope`. Additive resolution: annotate `StaleStateRecord.stalenessRisk` and `ExactnessArtifactRecord.stalenessRisk` with the Systema confidence tier as an optional `sourceConfidenceTier` field (no breaking changes).

## Mapping rules

1. Systema `confidence >= 0.85` → `ExactnessArtifactRecord.admissionPolicy: verifier-required` is satisfiable with `ValidatorReceipt`.
2. Systema `confidence < 0.5` → `StaleStateRecord.stalenessClass: stale-context-injection` should be emitted.
3. Systema `tier: unverified` + exactness-sensitive field → `LocalReasoningFailure.failureClass: string-exactness-violation` must be raised and `suppressMutation: true`.
4. Systema confidence axes map to `ReasoningAssay` axes: recency→`binding`, authority→`authority`, verifiability→`verifier`.

## No new schemas required

All Systema source-confidence semantics can be expressed through the existing `ProvenanceRecord`, `ValidatorReceipt`, `ReasoningAssay`, `StaleStateRecord`, and `ExactnessArtifactRecord` schemas. Systema adapters should emit these records rather than creating parallel ProCybernetica confidence schemas.
