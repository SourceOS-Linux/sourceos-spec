# ADR-0016: Model Plane store manifests (Tranche 7, T7-2)

**Date:** 2026-08-02  
**Status:** `Accepted`

---

## Context

Tranche 7 (T7-2) calls for `ModelManifest` and `AdapterManifest` — the content-addressed store manifests the Model Plane spec §IV places beside the weights (`/var/lib/sourceos/models/{base,adapters}/sha256-<digest>/manifest.json` + `signature.sig`). ADR-0015 deferred this pending two reconciliations (tracked as issue #242):

1. The store manifest appears to overlap `SourceOSModelCarryRef`.
2. "AdapterManifest" collides in name/concept with the existing `AdapterDescriptor`, which types **connector/actuation** adapters (api/cli/sdk/event/file).

## Decision

Add two new schemas, `ModelManifest` and `ModelAdapterManifest`.

- **`ModelManifest`** — the content-addressed manifest for base-model weights at rest: `modelDigest` (the store key), architecture, quantization, format, tokenizer digest, context length, default tier, modalities, `license`, and a required `signature` descriptor.
- **`ModelAdapterManifest`** — the LoRA adapter manifest: `adapterDigest`, the `baseModelDigest` it binds to, task, rank, alpha, target modules, format, `license`, a required `signature`, and an optional `evalReportDigest`.

**Naming:** the adapter manifest is `ModelAdapterManifest`, **not** `AdapterManifest`, so it does not collide with `AdapterDescriptor`. This resolves reconciliation (2).

**Relationship to `SourceOSModelCarryRef`:** the manifest and the carry-ref are complementary, not duplicative. The manifest is the store-level content-addressed truth about what the weights *are*; `SourceOSModelCarryRef` is the governance/policy wrapper about how the OS may *carry/prepare* a model reference (carryPolicy, cachePolicy, `mutableModelState: false`, router/governance refs). A carry-ref's `modelRef` points at a manifest digest; the manifest's optional `carryRefs` back-link to carry-refs. This resolves reconciliation (1).

**Teeth (schema `if/then`/required, verified both ways):**
- SEAM-014 — a `ModelManifest` is invalid without a `signature` (no model loads without signature verification).
- SEAM-017 — a `ModelAdapterManifest` is invalid without `baseModelDigest` (rejected on mismatch) and without a `signature`.
- MIT/Apache-only estate rule — both require an SPDX `license`, so the rule is checkable before wiring; non-SPDX licenses use `LicenseRef-<name>` (e.g. `LicenseRef-Gemma`, `LicenseRef-Llama-Community`), which are visibly NOT Apache/MIT. This closes Model Plane spec OQ3 at the contract layer.

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Name it `AdapterManifest` per the spec text | Collides with `AdapterDescriptor` (connector adapters) — a downstream-mapping hazard. |
| Extend `SourceOSModelCarryRef` instead of new manifests | The carry-ref is a governance reference with policy, not a content-addressed store record; conflating them would overload one type with two concerns. |
| Reuse `ArtifactManifest`/`PackageManifest` | Generic artifact/package manifests do not carry model-specific fields (architecture, quantization, LoRA rank/alpha, base-model binding). |
| Put signature/license as optional | Then SEAM-014/017 and the MIT/Apache rule would not be enforceable at the contract layer. |

## Consequences

- Positive: `AdapterPromotionDecision` (ADR-0015) `candidateAdapterDigest`/`baseModelDigest` now reference real manifest digests; SEAM-014/017 and the license rule are contract-enforced.
- Positive: the store layout in source-os T7-11 (`modelplaned`) now has typed manifests to read/verify.
- Follow-up (SHACL, ontogenesis T7-8): the cross-document invariant `ModelAdapterManifest.baseModelDigest == ModelManifest.modelDigest` (when `baseModelManifestRef` is set) and `carryRef.modelRef == manifest.modelDigest` are cross-document and cannot be expressed in JSON Schema `if/then`.

## References

- SourceOS Model Plane — Architecture Specification v0.1, §IV, §IX (SEAM-014/017), §XIV (T7-2)
- ADR-0015 — Model Plane inference-provenance schemas (deferred T7-2 here)
- Issue #242 (this decision); epic #241
- Reused/related: `schemas/SourceOSModelCarryRef.json`, `schemas/AdapterDescriptor.json`, `schemas/AdapterPromotionDecision.json`
