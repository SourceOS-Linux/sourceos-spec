# ADR-0010 — CompressionEvaluation placement

**Date:** 2026-04-25  
**Status:** Proposed

## Context

Compression Commons has been seeded upstream in `SocioProphet/sourceos-workspace` as a planning/freeze artifact, but the live placement guidance now distinguishes four lanes:

- `sourceos-workspace` for planning and sequencing
- `sourceos-spec` for typed contract canon
- `source-os` for Linux realization
- `socios` for later opt-in commons handoff

The next contract decision is where Compression Commons belongs as a machine-readable object and how much of it should be modeled as new schema versus composition over existing governance, execution, provenance, and reference types.

The current `sourceos-spec` surface already contains adjacent objects:
- `PolicyDecision`
- `RunRecord`
- `ProvenanceRecord`
- `ExecutionDecision`
- `SessionReceipt`
- `TruthSurface`
- `DeltaSurface`
- `ContentRef`
- `DataRef`

## Decision

Introduce Compression Commons into `sourceos-spec` as one new top-level metadata-plane contract:

- `CompressionEvaluation`

Place it under the existing Execution / Provenance family rather than creating a new family in the first cut.

`CompressionEvaluation` should reuse existing neighboring objects rather than cloning them:
- `PolicyDecision` for allow/deny/obligations
- `RunRecord` for evaluator execution audit
- `ProvenanceRecord` for lineage
- `ContentRef` for digest-first artifact or baseline handles
- `DataRef` for dataset/asset/stream/file references

The first API surface should be a base metadata-plane action endpoint in `openapi.yaml`:

- `POST /v2/compression-evaluations/evaluate`

The first cut should not add:
- a new `ArtifactRef` top-level schema
- a new `CorpusSnapshotRef` top-level schema
- a new `MetricVector` top-level schema
- a new AsyncAPI channel
- an agent-plane patch surface

Semantic overlay updates are required if `CompressionEvaluation` becomes first-class.

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Put Compression Commons only in `sourceos-workspace` | Correct for planning/freeze, wrong for canonical machine-readable contracts |
| Start in `sourceos-sdk` first | Premature; SDK should consume the canon, not define it |
| Put Compression Commons in the agent-plane patch first | Too narrow; evaluation is broader than agent sessions |
| Create a whole new Compression Commons schema family immediately | Too much schema sprawl before reuse is exhausted |
| Keep `socioprophet-agent-standards` as the machine-readable contract home | Conflicts with the active typed-contract lane in `sourceos-spec` |

## Consequences

Positive:
- keeps one contract canon for machine-readable evaluation objects
- minimizes duplication by reusing governance/provenance/reference primitives
- keeps SDK and Linux realization work downstream of the contract decision
- preserves a clean split between planning, contracts, runtime, and commons handoff

Negative:
- requires explicit reconciliation of older docs that still point schema ownership at other repos
- delays SDK-facing work until the contract shape is agreed
- may require later extraction of additional top-level schemas if reuse proves insufficient

## References

- `SocioProphet/sourceos-workspace`
- `SociOS-Linux/source-os`
- `SocioProphet/socioprophet-agent-standards`
- `SourceOS-Linux/sourceos-spec`
- follow-on design note: `docs/contract-additions/compression-evaluation-v0-placement.md`
