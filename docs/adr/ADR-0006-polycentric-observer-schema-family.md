# ADR-0006 — Polycentric Observer-Control Schema Family

- Status: Proposed
- Date: 2026-04-09

## Context

The organization is adopting a polycentric observer-control model upstream in `SocioProphet/socioprophet-standards-storage`.

That normative doctrine introduces a canonical split between:

- entities
- interactions
- scoped state records
- observations, claims, evidence, and inferences
- actions, effects, and policy decisions
- artifacts and views
- trust labels, attestations, and flow rules
- retention and revocation semantics
- compile targets for CI/CD and NixOS ops

`SourceOS-Linux/sourceos-spec` is already the canonical machine-readable contract layer for the SourceOS metadata governance platform and the SociOS agent plane. This repository is therefore the correct downstream home for the schema family that implements that doctrine.

## Decision

Reserve this repository as the authoritative machine-readable home for the polycentric observer-control schema family.

The expected schema additions are:

- `Entity`
- `Interaction`
- `StateRecord`
- `View`
- `Observation`
- `Evidence`
- `Claim`
- `Inference`
- `Action`
- `Effect`
- `Artifact`
- `PolicyDecision`
- `ResourceAccount`
- `TrustLabel`
- `Attestation`
- `FlowRule`
- `BoundaryCrossing`
- `RetentionPolicy`
- compile-target schemas for CI/CD and NixOS ops
- machine-readable surface profiles where they belong in this contract layer

## Consequences

- Upstream normative prose and ADRs stay in `SocioProphet/socioprophet-standards-storage`.
- This repository owns the machine-readable realization: JSON Schema, examples, and semantic overlays.
- Runtime and transport repositories consume these schemas by reference and should not become the canonical schema source of truth.

## Follow-on work

1. Add the schema family under `schemas/`.
2. Add conforming examples under `examples/`.
3. Add JSON-LD / semantic overlay material under `semantic/`.
4. Wire adoption into downstream runtime repos.
5. Add conformance checks beyond structural validation where needed.
