# OS Build / Cybernetic Boundary — additive contract note

## Status

Merged into `main` via PR #26.

Merge commit:
- `025ebc02dcf6eeeb21340804fb5e60fe30cc7be8`

## Purpose

This note exists to make the new OS build / cybernetic seam discoverable in the current repository structure without forcing a broad repo-wide doc rewrite while other additive families are also landing.

The seam introduces three canonical top-level schema types:

- `OSImage`
- `NodeBinding`
- `CyberneticAssignment`

## Intent

These objects separate three concerns that should not be collapsed into one deployable identity:

1. **immutable substrate identity** — `OSImage`
2. **mutable install / enrollment assignment** — `NodeBinding`
3. **runtime semantic and policy layer** — `CyberneticAssignment`

## Where to look

Canonical machine-readable schemas:

- `schemas/OSImage.json`
- `schemas/NodeBinding.json`
- `schemas/CyberneticAssignment.json`

Aligned examples:

- `examples/osimage.json`
- `examples/nodebinding.json`
- `examples/cyberneticassignment.json`

Normative discussion:

- `docs/specs/canon.os-build.v1.md`
- `docs/adr/0001-os-build-cybernetic-boundary.md`

## What this note does not do

This note does **not** by itself make these objects first-class REST resources, event-spine topics, or semantic overlay classes.

Those decisions remain follow-on work and should be evaluated against the current repository direction rather than assumed automatically.

## Why this note exists

Recent upstream activity expanded the repository with additional additive families and discoverability lanes. This note follows that pattern so the OS build / cybernetic seam is visible in the same way, without fighting the current structure.
