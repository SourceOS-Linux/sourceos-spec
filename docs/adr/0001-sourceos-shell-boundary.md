# ADR 0001 — sourceos-shell contract boundary

## Status
Accepted

## Context

The SourceOS shell work introduces a product/runtime surface for:

- Markdown-first authoring
- PDF derivation, signing, and validation
- search routing decisions
- comment/review signal surfaces
- annotation export
- run reports and Noether diagnostics
- publish and mirror receipts

These objects are exchanged across product code, Linux realization, and publishing/provenance systems. They should not be defined ad hoc inside runtime repositories.

## Decision

The repository split is:

- `SourceOS-Linux/sourceos-shell` — product/runtime code
- `SourceOS-Linux/sourceos-spec` — shared machine-readable contracts
- `SociOS-Linux/source-os` — Linux realization surfaces
- `SociOS-Linux/albert` — temporary launcher bridge only

The canonical object shapes for shell/document/provenance/search/report flows are defined here in `sourceos-spec`.

## Consequences

- shell/runtime code consumes generated types from this repository
- Linux realization refers back to these contracts instead of redefining them
- publish, mirror, validation, and routing receipts become interoperable across implementations
