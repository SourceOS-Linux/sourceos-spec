# Software Operational Risk Schema Family

This note documents the initial software operational risk schema family added in this branch.

## Current schemas

- `schemas/SoftwareOperationalIncident.json`
- `schemas/UpstreamWatchItem.json`

## Intended URN prefixes

- `urn:srcos:oprisk-incident:` — normalized outage, degradation, integrity, and upstream-related operational incidents
- `urn:srcos:upstream-watch:` — normalized live watchlist items for repos, packages, providers, registries, and related upstream surfaces

## Initial examples

- `examples/softwareoperationalincident.json`
- `examples/upstreamwatchitem.json`

## Intended downstream consumers

- `SocioProphet/sociosphere` — harvester outputs and watchlist refresh jobs
- `SocioProphet/agentplane` — execution and evidence crosswalks
- `SociOS-Linux/source-os` — runtime/package/update posture
- financial and reserve-analysis layers that need a typed envelope for outage corpus records and upstream drift inputs

## Follow-on contract work

1. Add reserve / scenario report envelopes.
2. Add OpenAPI / AsyncAPI exposure where operational-risk objects move across service boundaries.
3. Fold these schemas into the main schema catalog and root spec documentation.
