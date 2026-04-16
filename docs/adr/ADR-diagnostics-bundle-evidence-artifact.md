# ADR — Diagnostics bundle as evidence artifact

**Date:** 2026-04-16  
**Status:** `Proposed`

---

## Context

SourceOS and SociOS already define machine-readable contracts for workloads, provenance, policies, and agent-session telemetry. What remains under-specified is the host-diagnostics capture artifact itself: a bounded bundle of timed probes, artifact hashes, and redaction posture that can be collected locally, diffed later, and exported safely when needed.

Without a canonical diagnostics object, downstream repos risk inventing incompatible formats for:

- timed command manifests
- privacy-preserving host identifiers
- raw-vs-share artifact separation
- bundle-level hashing and signing
- support and incident handoff between runtime, operator, and automation layers

## Decision

Introduce `DiagnosticsBundle` as a first-class execution/provenance contract in `SourceOS-Linux/sourceos-spec`, with supporting schemas for `DiagnosticsProbeRecord` and `DiagnosticsRedactionPolicy`.

The bundle contract standardizes:

1. bundle identity via `urn:srcos:diag-bundle:<local-id>`
2. probe-level timing, exit status, and artifact digests
3. declared redaction posture for raw and share-safe bundle forms
4. optional bundle-level integrity hashes and signatures
5. optional linkage upward to `RunRecord` URNs for runtime or workflow correlation

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Keep diagnostics as an implementation-only script format in a runtime repo | Would create a second implicit schema authority and make provenance, conformance, and interop harder. |
| Reuse `RunRecord` directly for diagnostics bundles | `RunRecord` captures workload execution, not a custody-oriented bundle of timed host probes and redaction metadata. |
| Put diagnostics contracts only in SociOS runtime repos | The typed contract layer belongs in `sourceos-spec`; runtime repos should consume, not redefine, the object semantics. |

## Consequences

### Positive

- creates a canonical evidence object for host diagnostics capture
- makes raw/share separation and masking posture explicit instead of ad hoc
- gives downstream runtime and packaging repos a stable object to produce and validate
- preserves alignment with existing execution/provenance and event-envelope patterns

### Negative / constraints

- this initial tranche is additive and intentionally narrow
- it does not yet update every catalog and semantic index file in the repo
- it does not yet define the runtime capability or immutable-image packaging surface

## References

- `schemas/DiagnosticsBundle.json`
- `schemas/DiagnosticsProbeRecord.json`
- `schemas/DiagnosticsRedactionPolicy.json`
- `openapi.diagnostics.patch.yaml`
- `asyncapi.diagnostics.patch.yaml`
