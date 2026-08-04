# ADR-0018: RLD loader & diagnostics contracts (LoaderFault / ResilientDiagnosticRecord)

Status: Accepted
Date: 2026-08-03
Part of: Epoch E13 (Reference-Gated Sovereign Stack), workstream WS-A

## Context

The Resilient Loader & Diagnostics (RLD) design ships as a Rust workspace + a Lean
launch-completeness proof. What the fabric lacked was the *contracts* — so the loader's
faults and crash records could be carried, deduped, and projected like every other typed
value in the estate. This lands them, making RLD the L1 fail-closed substrate the rest of
Epoch E13 (identity twin, capture receipts) stands on.

## Decisions

1. **Every fatal stop is a typed value first (I5 / R2).** `LoaderFault` is an algebraic sum
   with **stable codes** (`LDR-DEP-MISSING`, `LDR-ABI-MISMATCH`, …). A bare string abort is a
   spec violation. Non-fatal `FEATURE`/`LAZY` misses are recorded too, at `degraded`/`handled`
   — the "what quietly turned off" trail the reference format could not express.

2. **Severity is a table, not a heuristic.** The failing edge's binding class fixes severity:
   `REQUIRED→fatal`, `FEATURE→degraded`, `WEAK→info`, `LAZY→handled|fatal`. Machine-checked.

3. **Root-cause-first, diffable, coalescing.** `ResilientDiagnosticRecord` puts the typed
   fault as field #1; `reproKey = H(code ‖ import.name ‖ chain ‖ image_hash)` excludes
   timestamps/PIDs so N occurrences of a defect collapse to one bucket.

4. **Privacy by projection (I8), not redaction.** The telemetry tier is an *allowlist*
   projection of the local record; path-like fields are represented symbolically (store names,
   content hashes), so there is no user path to leak — enforced by the validator. This is the
   same discipline as the reasoning-evidence receipts and the twin's reference-gated projection
   (ADR-0014): **what leaves is a projection, never a scrub.**

## Consequences

- New conformant contracts `LoaderFault` + `ResilientDiagnosticRecord`, canonical examples
  (the reference `CoreSimulator` abort re-encoded, plus its correct `FEATURE`-degraded form),
  and an invariant validator wired into `make validate`.
- RDR `$ref`s `LoaderFault` by `$id`; validators resolve it via a `referencing` registry.
- The Rust workspace + Lean proof remain the reference implementation; these contracts are the
  wire/record form the fabric carries.
- Ties WS-A into the E13 through-line: bind-at-capture, fail-closed, projection-not-redaction.
