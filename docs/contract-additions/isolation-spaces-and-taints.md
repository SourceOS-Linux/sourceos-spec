# SourceOS Isolation Spaces and Taints v0.1

## Purpose

This contract makes the isolation **spaces** used by the consent-plane
(`socioprophet-agent-standards` `consent-plane/001-purpose-bound-tool-use-and-agent-roles.md`)
real at the OS layer. The consent-plane defines the admission *gate*; this
contract defines the *spaces* the gate admits into, so the OS — not just the
governance layer — enforces the isolation. It extends the OS boundary set in
`docs/adr/0014-agent-system-domain.md` and `docs/adr/0001-os-build-cybernetic-boundary.md`.

## Decision

SourceOS recognizes five ordered isolation spaces. Every OS operation targets
exactly one space and crosses into it only if the acting `(role, surface)`
context tolerates that space's **taints** (Kubernetes-style `key=value:effect`).
The org boundary aligns to the ring: `kernel-space`/`system-space` are SourceOS
base-OS territory; `agent-space`/`user-space` are SociOS managed/agentic territory.

| Space | Ring | Taint | Effect | Territory |
|---|---|---|---|---|
| `kernel-space` | 0 | `ring=kernel` | NoEntry | SourceOS base-OS core |
| `system-space` | 1 | `ring=system` | NoEntry | system services, daemons, infra |
| `user-space` | 3 | `ring=user` | PreferNoEntry | user apps / workspaces |
| `agent-space` | 4 | — (untainted) | — | the agent's native sandbox |
| `data-namespace` | tenant | `tenant=<id>` | NoExecute | per-tenant data isolation |

## Admission (taint ⇄ toleration)

- An operation MUST carry a **toleration** matching every blocking taint
  (`NoEntry`, `NoExecute`) of its target space, or it is denied (fail-closed).
- `NoEntry`: no entry without a matching toleration.
- `NoExecute`: a running operation whose toleration is withdrawn is aborted —
  this is how a tenant's consent withdrawal (GDPR Art. 7(3)) evicts in-flight
  work touching `data-namespace=<tenant>`.
- Only the `operator` role tolerates `ring=system` and `ring=kernel`.
- The **surface** may hard-deny a space regardless of toleration
  (defence-in-depth): the `browser` surface denies all but `agent-space`, so an
  injected browser agent cannot reach system/kernel/user/tenant space.

## Accountability

Every space-crossing decision emits an Action-Ontology receipt
(`docs/adr` mutation/evidence family) carrying `{space, taint, toleration,
role, surface, purpose, decision}` — the same receipt the consent-plane gate
records (GDPR Art. 5(2)).

## Implementation boundary

Per the contract-additions rules, enforcement code lives in the owning
implementation repositories: `source-os` (kernel/system/user space enforcement),
and the surface agents `BearBrowser` / `goose-notes` / `TurtleTerm` /
`sourceos-shell` (surface envelope + `space_deny`). This document is the
contract those implementations MUST satisfy; conformance is a receipt trail
proving denied operations never crossed a taint they did not tolerate.

## Cross-references

- Consent-plane gate + catalogs: `socioprophet-agent-standards` `consent-plane/001`, `standards/consent-plane/spaces_v1.yaml`.
- OS boundaries: `docs/adr/0014-agent-system-domain.md`, `docs/adr/0001-os-build-cybernetic-boundary.md`.
