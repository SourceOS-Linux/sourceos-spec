# ADR-0011: NLBoot Object Schemas

**Date:** 2026-04-30
**Status:** `Accepted`
**Deciders:** SourceOS-Linux/sourceos-spec maintainers

---

## Context

The NLBoot system orchestrates Linux boot on Apple Silicon (Asahi) and generic UEFI targets. It manages ordered boot stages, locally cached artifacts, per-boot integrity proofs, and Apple Silicon–specific adapter evidence.

Without canonical object schemas in this repository, downstream repos risk inventing overlapping structures for boot plans, artifact caching, proof reporting, and Apple Silicon adapter state. The `SourceOS-Linux/sourceos-spec` repository is the normative home for machine-readable contracts consumed by NLBoot, sourceos-boot, Sociosphere, and control-plane surfaces.

## Decision

Introduce four new top-level schemas in the Boot / NLBoot family:

| Schema | URN prefix | Purpose |
|--------|-----------|---------|
| `NLBootPlan` | `urn:srcos:nlboot-plan:` | Ordered boot stage plan for a target device |
| `ArtifactCacheRecord` | `urn:srcos:artifact-cache:` | Content-addressed local artifact cache entry |
| `BootProofRecord` | `urn:srcos:boot-proof:` | Immutable per-boot integrity proof with stage verdicts |
| `AppleSiliconAdapterEvidence` | `urn:srcos:as-adapter-evidence:` | Asahi-compatible Apple Silicon adapter evidence |

All four schemas follow the standard v2 conventions: `$id` under `https://schemas.srcos.ai/v2/`, `additionalProperties: false`, required `id`/`type`/`specVersion` discriminators, and `description` on every property.

### Scope of this repository

This repository owns:
- canonical JSON Schema definitions for the four types
- conforming example payloads
- validation tooling (`tools/validate_nlboot_examples.py`)

This repository does not own:
- NLBoot runtime boot executor implementation (`SociOS-Linux/nlboot`)
- Apple Silicon boot-chain implementation (`SociOS-Linux/asahi-u-boot`, `SociOS-Linux/asahi-installer`)
- transport bindings or RPC protocol definitions

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Add schemas inside `schemas/control-plane/` | NLBoot objects are boot-plane contracts, not legacy control-plane objects; they belong at the top level |
| Single merged `NLBootEvidence` schema covering all four concerns | Each concern has distinct required fields and lifecycle; splitting keeps schemas compact and independently consumable |
| Re-use existing `AttestationEvidence` for Apple Silicon evidence | `AttestationEvidence` models TPM/IMA measured-boot evidence; Apple Silicon adapter evidence captures Asahi-specific boot picker and m1n1/U-Boot state that does not fit that model |

## Consequences

### Positive

- downstream repos can reference canonical URN-typed NLBoot objects without re-inventing structure
- boot plan, artifact cache, and proof record objects are independently versioned and independently consumable
- Apple Silicon adapter evidence is first-class and auditable, not embedded in ad hoc implementation logs
- all four schemas are immediately validated by `make validate-nlboot-examples`

### Constraints

- schemas are intentionally minimal at introduction; fields may be added additively in follow-on PRs
- proof reporting endpoint binding (`policyDecisionRef`, `evidenceRefs`) is normative contract only; enforcement belongs in runtime repos

## References

- Issue: SourceOS-Linux/sourceos-spec — "Agent task: add NLBoot object schemas"
- ADR-0008: Local-first release and enrollment contract family
- ADR-2026-04: Contract vs Bootstrap Boundaries
- `schemas/BootSurface.json` — related boot-surface schema
- `schemas/AttestationEvidence.json` — measured-boot attestation evidence
