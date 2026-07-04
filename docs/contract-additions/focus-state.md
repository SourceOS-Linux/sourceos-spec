# FocusState contract addition

This addition introduces `FocusState` as the typed ownership/state record for
keyboard-first cross-surface interaction in SourceOS / SociOS.

## Why this contract exists

`InteractionSurface` describes a surface and its high-level policies.
`CommandBus` describes routing and interpretation across multiple surfaces.
What was still missing was an explicit typed record for **who owns the keyboard right now**.

`FocusState` fills that gap by making these aspects explicit:

- current surface reference
- ownership mode (`host`, `local-surface`, `shell-overlay`, `pass-through`, etc.)
- printable-input ownership
- escape and tab behavior
- completion and selection activity
- multiline boundary-history semantics

## Intended use

- canonical specification lives here in `sourceos-spec`
- Linux / browser / shell implementations bind to this state model downstream
- execution/control-plane repos may consume focus-state evidence later, but do not own the contract

## Relationship to the other keyboard-navigation contracts

- `InteractionSurface` = what the surface is and what high-level policies it carries
- `CommandBus` = how commands route across surfaces
- `FocusState` = who owns keyboard behavior in the current moment

All three are needed for the cross-surface keyboard-navigation model.
