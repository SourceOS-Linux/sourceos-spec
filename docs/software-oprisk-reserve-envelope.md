# Software Operational Risk Reserve Envelope

This note documents the first reserve/report contract added for the software operational risk lane.

## Added schema

- `schemas/ReserveScenarioReport.json`

## Added example

- `examples/reservescenarioreport.json`

## Purpose

The reserve/report envelope gives the platform a typed object for:

- expected annual loss,
- benchmark reserve,
- scenario reserve,
- suggested reserve,
- current-versus-target control deltas,
- and scenario-level reserve contributions.

## Why this matters

The earlier incident and watchlist schemas describe event and upstream-state inputs.
This envelope describes a financially legible output layer that can be consumed by:

- governance reporting,
- reserve and capital analysis,
- control ROI narratives,
- and downstream dashboards.

## Follow-on contract work

1. Add scenario-run and model-metadata envelopes.  
2. Add explicit references to typed incident and watchlist inputs.  
3. Add API / event exposure once the first consumers are ready.
