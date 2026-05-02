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

## Mac-on-Linux polish signals

`SociOS-Linux/source-os` has added workstation-v0 Mac-on-Linux polish surfaces. The canonical
contract examples reflect these signals without over-claiming implementation parity.

**Implementation authority** for all polish features below remains in `SociOS-Linux/source-os`.
This repository owns only the typed contract descriptors and examples.

### Currently active signals (reflected in examples)

| Signal | Contract field | Example value |
|--------|---------------|---------------|
| Screenshot helper | `WorkstationProfile.macOnLinuxPolish.screenshotHelperCommand` | `"sourceos-screenshot"` |
| Quick Look / Sushi file preview | `WorkstationProfile.macOnLinuxPolish.quickLookPackages` | `["sushi", "gnome-sushi"]` |
| Mac keyboard remap policy | `WorkstationProfile.macOnLinuxPolish.keymapPolicyRef` | `urn:srcos:keymap-profile:mac-linux-primary` |
| Aggregate polish validation | `WorkstationProfile.validation.polishValidationCommand` | `"sourceos polish validate --json"` |
| Bounded appearance defaults | `DesktopProfile.appearance` | `colorScheme: dark, fontScaling: 1.0` |
| Sidebar bookmarks (Finder-style) | `DesktopProfile.sidebarBookmarks` | Home, Desktop, Documents, Downloads, Code |

### Future / non-goal signals (not yet in examples)

The following signals are tracked as follow-on work and are **not** represented in the current
examples. They should not be claimed as implemented until the corresponding feature lands in
`SociOS-Linux/source-os` and is verified:

- Deep Sushi/QuickLook MIME-type extension registration
- Per-app appearance override surfaces
- Native assistant bridge for Siri/Shortcuts-style flows (see `native_assistant_bridge_profile.apple_app_intents.json`)
- Full macOS parity — this is explicitly a **non-goal**; SourceOS targets polish, not emulation.

## Immediate alignment target

This family is intended to align with the current Linux realization in `SociOS-Linux/source-os`, including:
- workstation-v0 package layering
- GNOME desktop defaults and extension pinset
- SourceOS palette / command-bus posture
- Lampstand-backed local file search
- Mac-on-Linux polish surfaces (screenshot, Quick Look/Sushi, sidebar bookmarks, appearance defaults, keyboard remap)

## Follow-on contract work

1. Add richer search-provider and validation sub-objects once the shell/runtime product repo stabilizes.
2. Add typed references for doctor/fix report families and runtime execution surfaces.
3. Bind these objects into OpenAPI / AsyncAPI surfaces when the first product/runtime consumers are ready.
4. Add negative examples for future/non-goal polish signals once the boundary is further stabilized.

