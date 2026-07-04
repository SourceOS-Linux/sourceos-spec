# Workstation Report Contract Family

This note documents the first typed contract family for SourceOS workstation-v0 health and remediation reports.

## Added schemas

- `schemas/WorkstationDoctorReport.json`
- `schemas/WorkstationFixShellReport.json`
- `schemas/WorkstationFixFishReport.json`
- `schemas/WorkstationFixAllReport.json`

## Added examples

- `examples/workstationdoctorreport.json`
- `examples/workstationfixshellreport.json`
- `examples/workstationfixfishreport.json`
- `examples/workstationfixallreport.json`

## Purpose

These contracts promote the workstation doctor/fix surfaces from implementation-local JSON blobs into canonical typed reports.

They are intended to support:
- local workstation health checks
- local remediation/audit flows
- evidence ingestion into higher-level control planes
- UI rendering in workspace/operator surfaces
- typed CLI and SDK generation downstream

## Compatibility note

The current Linux realization emits compatibility discriminator strings such as:
- `sourceos.doctor`
- `sourceos.fix.shell`
- `sourceos.fix.fish`
- `sourceos.fix.all`

These schemas preserve those `kind` strings so the canonical layer stays aligned with the current implementation while still giving downstream systems a stable typed contract family.

## Follow-on contract work

1. Add optional metadata fields for host identity, generated timestamps, and artifact provenance if the local producer begins emitting them.
2. Add event/API exposure once the first agentplane and sociosphere consumers exist.
3. Consider a higher-order workstation bundle/envelope if multiple report artifacts need to be tied into one typed evidence object.
