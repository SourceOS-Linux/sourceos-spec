# Control-Plane Contracts (MeshSkill / Validation Lifecycle)

This directory is the intended canonical home for the typed control-plane contract surface that was previously published in the umbrella public-surface repo.

## What lives here

- architecture and doctrine for agent validation control planes
- MeshSkill descriptor specification
- skill execution lifecycle specification
- machine-readable control-plane schemas
- starter policy pack and examples

## Why this is here

`sourceos-spec` is the canonical typed-contract and vocabulary lane for the SourceOS / AgentOS topology. The control-plane package belongs here as contract material, even if public-facing documentation or downstream examples continue to exist elsewhere.

## Current caveat

This first import preserves the existing schema IDs and content shape from the previously published package so we do not silently change identifiers during the re-home. A follow-on revision should decide whether those `$id` values should remain stable for compatibility or be normalized into the SourceOS / SourceOS-Linux namespace.

## Adjacent repos

- `SociOS-Linux/agentos-spine` should treat these files as the canonical contract surface for Linux-side integration.
- `SocioProphet/sociosphere` may reference or consume these contracts at the platform workspace-controller layer.
- `SocioProphet/socioprophet` and `SociOS-Linux/socioslinux-web` may explain these contracts downstream, but should not be treated as the canonical source of truth.
