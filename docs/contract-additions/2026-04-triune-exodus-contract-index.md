# Triune / Exodus contract additions index

- **Status:** bootstrap index
- **Date:** 2026-04-15

This document provides a discoverability layer for the initial Triune / Exodus contract additions landed in the typed-contract repository.

## New schema types

### Replay and anchoring

- `ReplayEnvelope.json`
- `AuditAnchorRecord.json`

### Quorum / review

- `ValidatorDecision.json`
- `QuarantineReceipt.json`

### Time-boxed bypass governance

- `ExceptionLedgerEntry.json`

## Matching examples

- `examples/replay_envelope.json`
- `examples/audit_anchor_record.json`
- `examples/validator_decision.json`
- `examples/quarantine_receipt.json`
- `examples/exception_ledger_entry.json`

## Why these additions exist

These objects provide typed contract support for:

- replay verification
- append-only audit anchoring
- validator quorum outcomes
- quarantine lifecycle tracking
- signed exception-ledger operation for bounded policy bypasses

## Relationship to existing schema families

These additions extend the existing SourceOS/SociOS contract system rather than replacing it.

- `ReplayEnvelope` and `AuditAnchorRecord` extend the execution / provenance story.
- `ValidatorDecision` and `QuarantineReceipt` extend the agent-plane and runtime-governance story.
- `ExceptionLedgerEntry` extends governance and exception handling beyond the simple inline `Exception` sub-object.

## Intended next updates

1. add these objects to the schema catalog in `schemas/README.md`
2. add them to the examples index in `examples/README.md`
3. connect them into OpenAPI / AsyncAPI patch surfaces
4. add ADR cross-references from the placement decision document
