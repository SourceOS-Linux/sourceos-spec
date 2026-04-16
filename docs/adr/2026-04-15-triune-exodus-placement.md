# ADR — Triune / Exodus placement and contract boundaries

- **Status:** Proposed
- **Date:** 2026-04-15
- **Owners:** mdheller / SourceOS-Linux

## Context

SourceOS now has two classes of work that must be placed cleanly across the ecosystem:

1. **Triune runtime governance and security controls**
   - live / audit / replay call semantics
   - watchdog / validator flows
   - quarantine receipts
   - replay envelopes
   - audit anchoring
   - validator decisions and session receipts
   - capability scoping tied to policy decisions

2. **Exodus / Exodus Reversed controls**
   - vendor-block policies
   - egress-policy contracts
   - exception ledger records
   - reversal detection events
   - migration receipts and posture declarations

The SourceOS-Linux/sourceos-spec repository is already the canonical contract layer for the SourceOS metadata governance platform and the SociOS agent plane. This repository already defines the two-plane model, policy / decision / capability objects, execution records, provenance, and agent-plane receipts.

The question is not whether Triune / Exodus belong here at all. The question is **which parts** belong here.

## Decision

**All contract-layer artifacts for Triune and Exodus belong in `SourceOS-Linux/sourceos-spec`.**

This repository is the canonical home for:

- schema definitions
- OpenAPI additions
- AsyncAPI additions
- semantic overlay updates
- URN conventions
- governance lifecycle clarifications
- architecture decision records (ADRs)
- conformance examples

This repository is **not** the home for runtime daemon code, eBPF programs, installer flows, or build-image wiring.

## Contract-surface additions

The following objects should be added here, either as new schemas or as extensions to existing schema families.

### Governance / execution additions

- `ReplayEnvelope`
  - canonical digest of inputs, environment, dependencies, seeds, and determinism bounds
- `AuditAnchorRecord`
  - append-only anchor record containing entry digest, rolling root, witness set, and media references
- `ValidatorDecision`
  - explicit quorum vote / verdict record with signer, role, evidence references, and outcome
- `QuarantineReceipt`
  - immutable record of isolation action, scope, trigger, timing, and restoration or termination result
- `ExceptionLedgerEntry`
  - signed, time-boxed exception for vendor egress or policy bypass
- `IsolationPolicy` or extensions to `ExecutionSurface`
  - egress mode, network boundaries, mount policy, sandbox mode, replay constraints
- `ReleaseReceipt` extensions
  - inclusion of policy-digest, replay-verifier result, and quarantine-related gate results

### Existing-family extensions

Extend existing objects where appropriate:

- `CapabilityToken`
  - network / mount / replay / attest constraints
- `PolicyDecision`
  - explicit tie to replay / anchor / validator artifacts
- `ExecutionDecision`
  - ask / allow / deny / quarantine / defer / rewrite outcomes
- `TelemetryEvent`
  - add quarantine, reversal-detection, and allowlist-mutation event kinds
- `SessionReceipt`
  - tie to validator decision set and replay verification summary
- `EventEnvelope`
  - typed event streams for Triune and Exodus posture changes

## API and event additions

### OpenAPI

The following endpoint families should be added or patched into the spec surface:

- `/v2/replay-envelopes`
- `/v2/audit-anchors`
- `/v2/validator-decisions`
- `/v2/quarantine-receipts`
- `/v2/exception-ledger`
- `/v2/exodus-posture`

### AsyncAPI

Add event channels for:

- `srcos.v2.quarantine.events`
- `srcos.v2.replay.events`
- `srcos.v2.audit-anchor.events`
- `srcos.v2.validator.events`
- `srcos.v2.exception-ledger.events`
- `srcos.v2.exodus-reversal.events`

## Boundaries / non-goals

The following do **not** belong in this repository:

- watchdog daemon code
- validator daemon code
- cgroup eBPF programs
- nftables / Unbound / WireGuard operational scripts
- self-hosted service compose files
- installer UX / migration wizards
- image-build hooks
- metapackage dependency lists

Those belong in runtime or distro integration repositories.

## Consequences

### Positive

- SourceOS keeps a clean separation between **contract** and **implementation**.
- Triune and Exodus become first-class typed surfaces rather than informal docs.
- Downstream runtimes, installers, and builders gain a canonical contract target.

### Negative

- This repo alone cannot “land the work” end to end; runtime and distro integration still need separate homes.
- Additional repos must consume these contracts correctly or the split becomes ceremonial.

## Immediate follow-on work

1. Add schema stubs and examples for the objects listed above.
2. Add OpenAPI / AsyncAPI patch files for the endpoint and event families above.
3. Add conformance examples for strict write-before-read, quarantine, replay verification, and exception-ledger usage.
4. Pair this ADR with a runtime-bootstrap document in the SourceOS / SociOS runtime umbrella.

## Acceptance gates

This ADR is considered operational when:

- the schemas exist,
- at least one example payload exists for each new type,
- OpenAPI / AsyncAPI paths and channels are present,
- and the runtime repo consumes the resulting contract surface.
