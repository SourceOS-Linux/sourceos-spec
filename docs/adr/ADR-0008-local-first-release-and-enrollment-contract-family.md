# ADR-0008 — Local-first release and enrollment contract family

Status: Proposed

## Context

ADR-0007 reserved the local-first control-node and image-promotion seam in `SourceOS-Linux/sourceos-spec`.

What remains missing is the first machine-readable contract family needed to make that seam executable for the thin local-first lifecycle slice:

- assign a release to a device or cohort
- optionally authorize a boot/install or recovery path
- enroll a device or session against that assignment
- realize operator/user experience and isolation posture
- emit a post-apply fingerprint suitable for compliance and rollback decisions

Without a canonical object family here, downstream repos risk re-inventing overlapping structures for release assignment, enrollment, host realization, and attestation.

## Decision

Reserve and introduce the first local-first control-plane contract family in this repository.

The initial object family is:

- `ExperienceProfile`
- `IsolationProfile`
- `ReleaseSet`
- `BootReleaseSet`
- `EnrollmentToken`
- `Fingerprint`

These objects define the minimum SourceOS local-first lifecycle seam for:

1. profile selection
2. release assignment
3. boot/recovery authorization when needed
4. enrollment and one-time redemption semantics
5. post-apply attestation and compliance comparison

## Repo ownership split

This repository owns:

- machine-readable schemas
- normative object semantics
- example payloads for the local-first lifecycle slice

This repository does not own:

- runtime execution enforcement (`SocioProphet/agentplane`)
- workspace/fabric choreography (`SocioProphet/sociosphere`)
- transport binding (`SocioProphet/TriTRPC`)

## Consequences

### Positive

- gives SourceOS a canonical typed object family for local-first release control
- avoids parallel release/enrollment/fingerprint vocabularies appearing downstream
- creates a stable seam for `agentplane` and other consumers

### Constraints

- this tranche is intentionally minimal and additive
- it does not yet define the full audit-event extension family
- it does not yet standardize every possible config-source shape

## Follow-on work

1. Bind `ReleaseSet`, `BootReleaseSet`, `EnrollmentToken`, and `Fingerprint` into `SocioProphet/agentplane` runtime evidence surfaces.
2. Add any required transport-safe references in `SocioProphet/TriTRPC` only after object semantics stabilize.
3. Add broader `ConfigSource` and lifecycle event families as follow-on contracts if the thin slice proves sound.
