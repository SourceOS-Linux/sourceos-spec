# Control node starter pack (v0)

This note accompanies the first machine-readable starter slice for the local-first control-node and image-promotion seam.

## Included contracts

The starter pack currently contains:

- `schemas/ControlNodeProfile.json`
- `schemas/NodeCommanderRuntime.json`
- `schemas/ImagePromotionGate.json`
- `schemas/BuildValidationEvidenceBundle.json`

Matching examples are included under `examples/`.

## Why this exists

These starter contracts are the first typed realization of the local-first control-node and image-promotion seam reserved by ADR-0007.

They are intentionally narrow and do not yet redefine the broader existing schema families. Their job is to give downstream repos a stable first target for:

- operator-node profile identity
- Node Commander runtime identity
- image promotion decision envelopes
- build validation evidence bundles

## Intended downstream consumers

- `SociOS-Linux/source-os` — workstation/bootstrap application
- `SocioProphet/agentplane` — execution/evidence consumption
- `SocioProphet/prophet-platform` — runtime/service implementation

## Follow-on

A later catalog cleanup should add these starter contracts directly into `schemas/README.md` and `examples/README.md`. This note exists so the starter slice is discoverable immediately without blocking on a larger catalog-edit pass.
