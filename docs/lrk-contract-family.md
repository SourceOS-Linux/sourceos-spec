# LRK Contract Family

This document describes the LRK / Semantic Holography contract family that augments the SourceOS/SociOS typed contract layer.

## Contract family

- `TriuneRPC` — canonical action / provenance envelope for semantic and runtime transitions
- `ProofOfLife` — heartbeat attestation bound to policy hash and slot identity
- `LifeMirrorState` — lifecycle state for liveness/tamper escalation
- `B11Surface` — typed, attestable surface for semantic/runtime publication
- `DeltaSurface` — typed comparison object for attested surface deltas

## Why these are a family

These types are cohesive because they all represent:

1. an observable boundary object,
2. a local or distributed trust transition,
3. a machine-validated shape that downstream runtimes must agree on.

## Recommended catalog updates

When this family lands, update:
- `README.md` schema families section
- `schemas/README.md` quick reference and family listing
- semantic context material if/when these become first-class linked data terms

## Downstream consumers

- `agentos-starter` surface collectors and LRK runtime package
- `workstation-contracts` validation lanes
- `agentos-spine` runtime state binding and publication
