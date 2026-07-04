# Software Operational Scenario Run Contract

This note documents the scenario-run lineage envelope added for the software operational risk lane.

## Added schema

- `schemas/SoftwareOperationalScenarioRun.json`

## Added example

- `examples/softwareoperationalscenariorun.json`

## Purpose

This contract makes the modeling lineage explicit by typing:

- the assessed subject,
- the modeling mode and method,
- the typed incident inputs,
- the typed upstream watch inputs,
- and the typed reserve/report outputs produced by the run.

## Why this matters

The current software operational risk family now has:

- typed incident inputs,
- typed watchlist inputs,
- typed reserve/report outputs,
- and now a typed scenario-run object that links them together.

## Follow-on contract work

1. Add model-metadata envelopes if the modeling surface needs separate provenance.  
2. Extend reserve reports with optional direct references back to their scenario-run objects.  
3. Expose the run/report family through OpenAPI / AsyncAPI when the first service consumers are ready.
