# CompressionEvaluation v0 placement note

## Purpose

This note turns the Compression Commons design assessment into an exact `sourceos-spec` landing plan.

It does not add schemas. It records what the first real schema/API PR should contain.

## New top-level schema

Add exactly one new top-level schema in the first cut:

- `schemas/CompressionEvaluation.json`

Place it under the existing Execution / Provenance family in `schemas/README.md`.

## Reused existing contracts

CompressionEvaluation should compose existing contracts rather than duplicate them.

Reuse as references:
- `PolicyDecision`
- `RunRecord`
- `ProvenanceRecord`
- `ContentRef`
- `DataRef`
- optional later summary refs: `TruthSurface`, `DeltaSurface`

Do not introduce in the first cut:
- `ArtifactRef` top-level schema
- `CorpusSnapshotRef` top-level schema
- `MetricVector` top-level schema
- `EvidenceBundle` top-level schema

## Proposed schema outline

Required fields:
- `id`
- `type`
- `specVersion`
- `artifact`
- `baseline`
- `estimatorSet`
- `metrics`
- `createdAt`

Recommended optional fields:
- `purpose`
- `policyDecisionRef`
- `runRecordRef`
- `provenanceRef`
- `truthSurfaceRef`
- `deltaSurfaceRef`
- `integrity`
- `notes`

Recommended URN prefix:
- `urn:srcos:compression-eval:`

## Proposed REST addition

Add one metadata-plane action endpoint to `openapi.yaml`:

- `POST /v2/compression-evaluations/evaluate`

Reason:
- the first need is evaluate-and-persist
- this matches the existing `POST /v2/decisions/evaluate` pattern
- it avoids premature noun-upsert semantics for externally supplied evaluations

Request shape should include:
- `artifact`
- `baseline`
- `purpose`
- `estimatorSet`
- optional `environment`

Response shape should be:
- persisted `CompressionEvaluation`

## Not in v0

Do not add in the first cut:
- `openapi.agent-plane.patch.yaml` changes
- `asyncapi.yaml` channel additions

Agent-plane integration can consume CompressionEvaluation later when an agent is the evaluator.
AsyncAPI can be added later if evaluation becomes asynchronous or requires downstream event consumers.

## Semantic overlay impact

Because `CompressionEvaluation` is intended as a first-class type, the first schema PR should also update:
- `semantic/context.jsonld`
- `semantic/hydra.jsonld`

## First real PR file list

- `schemas/CompressionEvaluation.json`
- `examples/compressionevaluation.json`
- `schemas/README.md`
- `ARCHITECTURE.md`
- `openapi.yaml`
- `semantic/context.jsonld`
- `semantic/hydra.jsonld`
- `CHANGELOG.md`
- one ADR

## Rationale

This is the smallest additive move that keeps:
- `sourceos-workspace` as planning/freeze
- `sourceos-spec` as machine-readable canon
- `source-os` as Linux realization
- future SDK work as downstream consumer rather than contract owner
