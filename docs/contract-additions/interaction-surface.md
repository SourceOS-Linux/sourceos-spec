# InteractionSurface contract addition

This addition introduces `InteractionSurface` as the first canonical contract for
keyboard-first cross-surface interaction ownership in SourceOS / SociOS.

## Why this contract exists

Existing contract families already describe execution, policy, provenance, and
agent-session behavior. What was missing was a typed description of the user-facing
surface itself: launcher, browser, shell, terminal, editor, overlay, and related
host-boundary contexts.

`InteractionSurface` fills that gap by making these aspects explicit:

- surface type and platform
- focus ownership policy
- host-boundary preservation vs mirroring vs opt-in replacement
- command binding defaults (`/` scope, `>` explicit command mode, etc.)
- optional command-bus / overlay / keymap references

## Intended use

- canonical specification lives here in `sourceos-spec`
- Linux-side implementation may live in SourceOS / SociOS Linux repos
- execution/control-plane repos may consume evidence or policy hooks later, but do not own this contract

## Current scope

This is intentionally the first slice, not the full interaction model. Follow-on
contracts may add richer focus-state, command-bus, keymap-profile, and surface-
discoverability types once they stabilize.
