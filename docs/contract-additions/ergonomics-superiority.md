# Ergonomics — one integrated system, more ergonomic than Apple

Apple ships excellent apps that do **not** share a spine: each has its own permissions
(TCC), its own sync (iCloud), its own idea of the assistant (Siri, which mostly can't act
inside them). SociOS is the inverse thesis — **one system**. The ergonomic win is not a
prettier clone of any single app; it is that **every app rides the same five planes**, so
the whole set composes.

## The one spine (every app rides all five)
| Plane | Every app gets… | Contract |
|---|---|---|
| **Launcher + NLQA** | reachable by name; grounded, cited help | lampstand · sherlock · docs-index |
| **Consent** | one purpose model for app *and* agent | role × surface × space × purpose (E11) |
| **Model** | one board, cloud ∩ local, sovereignty-ranked | InferenceGateway · GatewayCallAudit |
| **Mesh** | continuity across every device you own | MeshTransfer · WireGuard (E3) |
| **Receipts** | every action readable, sealed, replayable | AutonomyAdmissionReceipt (E4) |

Because the spine is shared, **anything you can do the agent can do the same governed
way**, and every action — a file drop, a mail draft, a model call, a launcher query —
carries the same consent and the same receipt. That composition is the ergonomics.

## Why it beats Apple (the dimensions)
- **One grammar** — ask in plain language; the launcher routes to a *typed, consented*
  action in any app. (Apple: learn each app; Siri can't act inside most.)
- **Agent = you** — the agent uses the *same consented surface you do*; nothing it can do
  is off-book. (Apple: brittle Shortcuts; the assistant can't drive your apps.)
- **Permissions** — one *purpose* model, fail-closed, editable, legible. (Apple: per-app
  TCC checkboxes, opaque, all-or-nothing.)
- **Transparency** — every action is a sealed receipt with its warrant. (Apple: you can't
  see what an app or Siri did.)
- **Continuity** — your mesh, any device you own, no vendor cloud, every transfer
  receipted. (Apple: Handoff/AirDrop only between Apple devices via iCloud.)
- **Help** — grounded NLQA cites the docs and *abstains* when it can't. (Apple: scattered
  docs, confident guessing.)
- **Ownership** — no account lock-in; models run local-first, ranked by sovereignty.
  (Apple: Apple ID + iCloud; models are theirs.)

## Done-definition for "integrated"
A surface is part of the integrated set only when it is **agent-native** (agent uses the
same typed/consented/receipted surface as a human), **accessible by default**, passes its
**seam's purple-team test**, and **rides all five planes** (or honestly declares which it
does not yet). The census (`macos-replacement-matrix.md`) tracks the ~37 surfaces; the
[integrated surface](../surfaces/integrated.html) is the operator view of the whole set.

The honest caps remain the hardware register (Neural Engine, Secure Enclave, HW codecs,
display on Asahi) — silicon, not ergonomics. Everywhere else the integrated, agent-native,
receipted system is a superset, not a clone.
