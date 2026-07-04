# Polycentric Observer-Control Schema Lane

This directory is the machine-readable contract lane for the **polycentric observer-control** model.

## Upstream ownership

- **Normative doctrine / invariants / ADRs:** `SocioProphet/socioprophet-standards-storage`
- **This repository:** machine-readable realization of the schema family

## Scope of this lane

The schema family covers:

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
- machine-readable surface profiles

## Staging rule

This lane is intentionally namespaced under `schemas/polycentric/` so it can mature without colliding with existing contract families already present in the repository.

## Downstream consumption

- `SocioProphet/TriTRPC` consumes transport bindings only.
- `SocioProphet/agentplane` consumes execution/evidence bindings only.
- `SocioProphet/prophet-platform-standards` consumes operational profile bindings only.
- `SocioProphet/prophet-platform` consumes the canon by reference during runtime adoption.
