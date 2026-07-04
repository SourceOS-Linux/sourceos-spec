# FocusTransition contract addition

This addition introduces `FocusTransition` as the typed transition edge between
keyboard-focus ownership states in SourceOS / SociOS.

## Why this contract exists

`FocusState` describes who owns the keyboard right now. What it does not capture
on its own is how ownership changes over time.

`FocusTransition` fills that gap by making these aspects explicit:

- source and destination focus states
- transition trigger
- priority ordering
- whether the transition is allowed
- conditions and ownership effect

## Intended use

- canonical specification lives here in `sourceos-spec`
- Linux / browser / shell implementations bind to this transition model downstream
- execution/control-plane repos may consume transition evidence later, but do not own the contract

## Relationship to the other keyboard-navigation contracts

- `InteractionSurface` = what the surface is
- `CommandBus` = how commands route across surfaces
- `FocusState` = who owns the keyboard right now
- `FocusTransition` = how ownership changes from one state to another
