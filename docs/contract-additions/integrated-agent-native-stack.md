# SourceOS Integrated Agent-Native Stack v0.1

## Purpose

macOS wins because it is **one integrated system**, not a pile of apps. SourceOS
matches that integration and goes past it by being **agent-native**: every app is
a **modified** first-class citizen of one coherent stack — wired to the shell, the
consent-plane, the receipts/warrant trail, the mesh, and the local model plane —
rather than a stock upstream binary dropped in. This contract specifies the
**per-app feature modifications**, makes **accessibility a first-class default**,
names the **security seams**, and mandates **purple-team tests** on each seam.

Depends on: `isolation-spaces-and-taints.md`, `socioprophet-agent-standards`
`consent-plane/001`, the enhancement program (`SociOS-Linux/enhancements` E1–E12),
and the owned SociOS shell (`SourceOS-Linux/sourceos-shell`).

## Decision — one integrated, agent-native, owned stack

1. **Owned shell, not extensions.** The shell (menu, dock, monitors, Tilix-quake,
   the Albert-parity launcher, the E11 consent/receipts UX) is ONE owned,
   version-locked layer in `sourceos-shell` — never a gnome-look extension
   graveyard, never proprietary apps (no WhatsApp/Telegram/Element).
2. **Every app carries feature modifications** (below): it MUST integrate the
   agent-native seams, not ship stock.
3. **Accessibility is a first-class default** (opt-in for the deeper agent modes).
4. **Every integration crosses a named security seam**, and each seam has a
   **purple-team test** that must fire.

## Per-app feature-modification matrix (agent-native integration)

Each app in the macOS-replacement set gets these modifications designed in:

| App (replacement) | Feature modifications (agent-native, integrated) |
|---|---|
| **Launcher + `lampstand`** | Albert-class parity (keyboard-first, fuzzy, actions/plugins, calc) **wired natively to `sherlock-search` (IR) + slashtags (tagging) + `holmes` (investigation) + NewHope**; every query is purpose-gated (E1) and receipted (E4/E11); results carry warrant. |
| **Browser (BearBrowser)** | agent-runtime mode; every navigation/DOM action consent-gated + receipted; pinned to `agent-space`; mesh handoff of tabs/sessions; page content is untrusted input. |
| **Files (`sourceos-syncd`)** | agent file-ops with consent receipts; slashtag tagging; mesh sync (Continuity); data-namespace taints on tenant data. |
| **Terminal (Tilix-quake + `sourceos-shell`)** | command-bus with consent-plane on exec + receipts; agent co-pilot in the drawer. |
| **Mail/PIM + `prophet-workspace`** | local-agent triage/summarize/draft; consent receipts on send/read; office surfaces show their warrant. |
| **Media + `imagelab`/`ocrlab`** | on-device vision via the governed model plane (E6); consent on library access. |
| **Messaging (OWN capability)** | first-class on the mesh/Matrix substrate, E2EE, agent-assisted, consent-gated — never a third-party client. |
| **Assistant (local agent cell)** | local-agent default (E2); App-Intents/Shortcuts bridge; every action receipted. |
| **Search (Spotlight → `sherlock`/`lampstand`)** | purpose-gated, slashtag-aware, transparent ranking, receipted. |

Each row's modifications are **contracts on the app repo**, tracked against the
enhancement matrix (`enhancements` E1–E12).

## Accessibility — first-class defaults (opt-in for agent modes)

- **On by default:** AT-SPI + Orca screen reader available, high-contrast + large-
  text toggles, full keyboard-only navigation, reduced-motion respected — WCAG 2.2
  AA is the baseline, not an add-on.
- **Agent-native accessibility (opt-in):** the local agent + `speechlab` (STT) + a
  TTS + Agent-S UI-grounding form a first-class **assistive layer** — the agent can
  describe and *operate* the UI on the user's behalf. This is opt-in (it is a
  powerful capability) and, being an agent acting for the user, it runs under the
  consent-plane with receipts like any other agent action.
- Accessibility settings live in the owned shell's Privacy/Accessibility pane (E11),
  not scattered across apps.

## Security seams (the enforcement boundaries)

Every integration crosses exactly one named seam; the seam is where policy is
enforced fail-closed and a receipt is emitted:

1. **Consent seam** — the `purpose_admissibility_gate` before any privileged tool/action (E1).
2. **Space seam** — isolation-space taints ⇄ tolerations (kernel/system/user/agent/data-namespace).
3. **Surface seam** — the surface envelope (browser confined to agent-space, notes = personal-data consent, terminal = no egress/operate).
4. **Supply-chain seam** — signed, reproducible (Guix), zot-registered artifacts; provenance receipts (Gatekeeper analog).
5. **Mesh seam** — cross-device / cross-tenant federation boundary (data-namespace NoExecute = consent withdrawal severs flows).
6. **Identity seam** — machine + human identity bound to a hardware root (TPM/vTPM; SEP where available).

## Purple-team tests (mandatory, must fire)

Each seam MUST have a **purple-team test** in CI — a red-team probe paired with the
blue-team detection it must trigger — and it must be *proven to fire* (never-fired =
suspect). Fail-closed. Examples:

- **Consent/Surface seam:** red = a page-injected browser agent attempts `implement`/
  `operate` (run a shell, write source); blue = denied, pinned to agent-space,
  receipted + alarmed. (Ties to BearTrap/honeypot.)
- **Space seam:** red = a `user`-role process attempts `system`/`kernel`-space
  syscalls; blue = denied by capability set / LSM, receipted.
- **Mesh seam:** red = withdraw a tenant's consent mid-flow; blue = in-flight
  cross-tenant data flow severed (NoExecute), receipted (GDPR 7(3)).
- **Supply-chain seam:** red = an unsigned/tampered artifact; blue = admission
  refused at zot/verify, receipted.

Purple-team tests are first-class CI (like the consent-plane fires-both-ways tests),
owned by the estate, and are the acceptance gate for each seam's "done."

## Implementation boundary
This is the contract. The owned shell + launcher live in `sourceos-shell`; per-app
modifications live in each app repo (governed by the matrix); the purple-team tests
live beside each seam's enforcement. Enforcement code stays in the owning repos.
