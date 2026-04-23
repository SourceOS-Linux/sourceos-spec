# Workstation Contract Family

This note documents the first workstation-facing contract family for SourceOS Linux developer/operator environments.

## Added schemas

- `schemas/LauncherAction.json`
- `schemas/LauncherProvider.json`
- `schemas/PackageManifest.json`
- `schemas/DesktopProfile.json`
- `schemas/WorkstationProfile.json`

## Added examples

- `examples/launcheraction.json`
- `examples/launcherprovider.json`
- `examples/packagemanifest.json`
- `examples/desktopprofile.json`
- `examples/workstationprofile.json`

## Purpose

These contracts promote workstation profile semantics from implementation-local YAML and shell scripts into canonical typed objects.

They are intended to support:
- reproducible workstation profile descriptions
- launcher/action-bus interoperability
- package layer and desktop posture reuse across repos
- typed validation, rendering, and SDK generation downstream
- alignment between Linux realization and the SourceOS contract layer

## Boundary rule

These workstation-facing types describe **what a workstation exposes and installs**.
They do not replace execution/audit contracts already owned by the execution plane.

Specifically:
- `LauncherAction` describes a user/operator-facing action surface, not a full execution receipt.
- `LauncherProvider` describes routing and invariants, not search index internals.
- `PackageManifest` describes layered packages, not image-level substrate identity.
- `DesktopProfile` describes the desktop posture, not a policy canon.
- `WorkstationProfile` ties these together for a workstation lane while referencing—not redefining—execution/audit semantics elsewhere.

## Immediate alignment target

This family is intended to align with the current Linux realization in `SociOS-Linux/source-os`, including:
- workstation-v0 package layering
- GNOME desktop defaults and extension pinset
- SourceOS palette / command-bus posture
- Lampstand-backed local file search

## Follow-on contract work

1. Add richer search-provider and validation sub-objects once the shell/runtime product repo stabilizes.
2. Add typed references for doctor/fix report families and runtime execution surfaces.
3. Bind these objects into OpenAPI / AsyncAPI surfaces when the first product/runtime consumers are ready.
