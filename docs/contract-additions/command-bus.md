# CommandBus contract addition

This addition introduces `CommandBus` as the typed routing contract for keyboard-first
cross-surface command dispatch in SourceOS / SociOS.

## Why this contract exists

`InteractionSurface` describes a specific user-facing surface and its ownership
policies. What it does not describe on its own is the shared routing layer that
interprets command prefixes, deictics, namespace handoff, and dispatch across
multiple surfaces.

`CommandBus` fills that gap by making these aspects explicit:

- default interpretation (`search`, `literal-input`, `local-action`)
- scope and explicit-command prefixes
- dispatch ordering (`focus-owner-first`, etc.)
- participating interaction surfaces
- protected namespaces and host-boundary handoff policy

## Intended use

- canonical specification lives here in `sourceos-spec`
- Linux / browser / shell implementations bind to this contract downstream
- execution/control-plane repos may consume command-bus evidence later, but do not own this contract

## Relationship to InteractionSurface

- `InteractionSurface` = a typed surface with focus/host-boundary/command binding rules
- `CommandBus` = the shared routing and interpretation layer that spans those surfaces

Both are needed for the keyboard-navigation model, but they serve different roles.
