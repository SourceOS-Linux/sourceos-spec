# ADR — Proof-of-Self Identity Plane

## Status
Accepted

## Context
SourceOS requires a first-class identity plane for local issuance, validator-backed trust, recovery, revocation, and attestation-bound proof artifacts.

## Decision
We add a Proof-of-Self identity family to `sourceos-spec` as typed contracts and additive agent-plane patches.
The runtime lives in a separate implementation repo and is not embedded into the substrate, integration spine, or optional commons.

## Consequences
- Identity objects become machine-verifiable and transport-neutral.
- Issuance, revocation, and recovery become receipt-bearing and event-emitting.
- Local operation remains possible without `socios`.
- `agentos-spine` integrates but does not absorb the runtime.
