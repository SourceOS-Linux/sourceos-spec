# E11 — Consent & Receipts UX (Privacy/Security Center)

**Gap #2 of the [feature-gaps-zero campaign](https://github.com/SourceOS-Linux/sourceos-spec/issues/267).**
macOS surfaces privacy as a per-app checkbox and hides *why* an action was allowed.
E11 is the surface that makes the [consent-plane](https://github.com/SociOS-Linux/ontogenesis)
legible: **which purpose** each app/agent may act under, on which surface and space, plus a
**hash-sealed receipt of every action** and the reason it was allowed, denied, or escalated.

Clickable prototype (one workflow, all regions): the E11 Consent & Receipts Center artifact.

## Regions (normative)
1. **Purpose vocabulary** — the 7 purposes (`discover/implement/verify/ship/operate/egress/administer`, GDPR Art 5(1)(b)). Contained surfaces show denied purposes struck through.
2. **Surfaces & their consent envelope** — per app/agent: `surface · space · posture(allow/ask/deny)` and the admissible/denied purpose set. Editable → writes back to `agent-standards/consent-plane/spaces_v1.yaml`.
3. **Receipt timeline** — every action as a row: time · verdict(allow/deny/escalate) · act · **why** (the warrant) · `sha256` seal. Sourced from the `AutonomyAdmissionReceipt` stream (E4). Read-only, tamper-evident.
4. **Governor queue** — actions of purpose `operate`/`egress` awaiting human approval (guardrail-fabric ESCALATE). Approve/Deny/Evidence. Mirrors `turtle-netwatch propose` → Governor decide/pending.
5. **Data residency** — tenant isolation + `region` toleration (GDPR Ch. V); a data-namespace crossing without both is refused fail-closed.

## Binding to what exists (build, don't rebuild)
| Region | Backing artifact (shipped this session) |
|---|---|
| Purpose vocab + envelope | `ontogenesis consent-plane/001` + `policy-fabric purpose_admissibility_gate.decide()` |
| Receipts | hash-sealed `AutonomyAdmissionReceipt` (emit+validate) |
| Governor queue | `guardrail-fabric` fail-closed `PolicyDecision` + `turtle-netwatch` propose/Governor |
| Residency | `spaces_v1.yaml` `region` taint + `goose-guard::consent` region branch |

## Done-definition
- Reads live from the receipt stream + consent catalog (no mock data).
- Envelope edits round-trip through the consent-plane catalog (agent-native: the agent edits the same surface a human does, itself consent-gated).
- Approve/Deny writes a Governor decision + emits its own receipt.
- Accessible by default (keyboard model, focus states, reduced-motion) + passes the **consent seam** purple-team test (no path renders an ungated action as allowed).
- Ported to `client-vue` (canonical UI) as the System Settings → Privacy & Security pane.

## Non-goals
Not a firewall UI, not a log viewer — those are Activity Monitor (`turtle-netwatch`) / Console (telemetry). E11 is specifically the **consent + warrant + receipt** surface.
