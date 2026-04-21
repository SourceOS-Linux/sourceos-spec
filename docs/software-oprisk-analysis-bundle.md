# Software Operational Analysis Bundle

This note documents the linkage envelope added for the software operational risk report family.

## Added schema

- `schemas/SoftwareOperationalAnalysisBundle.json`

## Added example

- `examples/softwareoperationalanalysisbundle.json`

## Purpose

This contract exists to make the report lineage explicit without requiring in-place edits to previously added report objects.

It binds:

- one typed `SoftwareOperationalScenarioRun`,
- one or more typed `ReserveScenarioReport` objects,
- and the assessed subject into a single typed bundle.

## Why this matters

The current software operational risk contract family now includes:

- incident inputs,
- watchlist inputs,
- scenario-run lineage,
- reserve/report outputs,
- and now an additive linkage object that joins run and report artifacts together.

## Follow-on contract work

1. Add model-metadata envelopes where deeper reproducibility is required.  
2. Fold these contract-family links into API and event exposure once first service consumers exist.
