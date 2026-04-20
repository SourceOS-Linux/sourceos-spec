# Shared Content / Build / Release Family v0

This additive contract family introduces shared object shapes that can be reused across:

- SourceOS artifact definitions and release lanes
- socios build / promotion automation
- workstation execution evidence
- office/editor export and publication lanes
- platform bundle publication
- catalog and promotion surfaces

## Design intent

The goal is not to force all domains into one execution engine.
The goal is to let all domains share one object-language for:

- desired content
- frozen overlays and inputs
- build requests
- releases
- enrollment/consumption profiles
- evidence bundles
- catalog entries
- access profiles

This keeps governance, provenance, and lifecycle semantics aligned even when the
runtime/build substrate differs.

## Object family

- `ContentSpec`
- `OverlayBundle`
- `BuildRequest`
- `ReleaseManifest`
- `EnrollmentProfile`
- `EvidenceBundle`
- `CatalogEntry`
- `AccessProfile`

## Boundaries

These schemas are additive. They do **not** replace:
- `ReleaseReceipt`
- `RunRecord`
- `PolicyDecision`
- `CapabilityToken`
- existing fog / agent-plane / governance families

Instead, they provide a cross-domain object layer that those families can reference.

## Follow-on

The next tranche after this family lands should add:
- example payloads
- fixture validation
- explicit bindings from runner/evidence/catalog implementations
- transport-boundary notes for local subprocess IPC vs remote TriTRPC transport
