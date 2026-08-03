# Surfaces — the diagram is a witness, not an illustration

Canonical visual surfaces for the estate. **The rule:** a diagram of a governed,
provenance-bearing system MUST be truthful, legible, version-controlled, and — for the
live ones — *rendered from the source of truth*, regenerated in CI so it can never drift
from what is real. Raster AI art (DALL·E et al.) garbles text and equations and knows
nothing about the system; it is a mood board, **disqualified** from documenting state here.
An instrument that can lie is worse than none — the same reason the Life-Mirror surface
flags a never-fired tripwire as SUSPECT.

## Live-feed wiring
The Tier-2 surfaces are **wired to a live feed**: each reads `./data/<name>.json`
(or `window.SURFACE_FEED_URL`) at load, falls back to an embedded seed, and shows a
**LIVE / SAMPLE** badge — an instrument that declares its own provenance. Regenerate a
feed from real state with `tools/build_surface_feed.py`; see `data/README.md`.

## Three tiers
| Tier | What | Medium | Reads |
|---|---|---|---|
| **1 · Architecture** | static structure (the braid, genesis, fibrations, flywheel) | SVG / Mermaid in-repo | nothing — hand-authored truth, regenerated on change |
| **2 · Live surface** | operational dashboards | HTML | guardrail-fabric · consent-plane · netwatch (sample data until wired) |
| **3 · Dynamics / math** | the model, falsifiable | typeset spec | states what each term is measured from |

## Style is validated against source
The **house theme** is the *first theme* (the B₁₁ instrument): deep instrument ground
(#0a0e18) + cyan action accent + the four-space semantic hues, sitting on the OS dark base.
`sourceos.tokens.css` documents both the source-derived base and this chosen house layer.
Every surface imports `sourceos.tokens.css` — the canonical palette + font (**Cantarell**,
`color-scheme`-honored) extracted from `source-os/website/index.html` and the GNOME
workstation-v0 appearance profile. A surface that invents its own colors is **not
validated against the OS** and is not canonical. The operational surfaces render inside
the real SociOS/GNOME chrome (top bar, launcher card) so they read as in-shell, not as generic web pages.

## In this directory
- **`holography-framework.html`** — Tier 1. The *Semantic Holography + Ghostspace* one-pager:
  four spaces (Atzilut/Beriah/Yetzirah/Assiah), four fibrations (π: E→B, fiber B₁₁),
  the life-mirror state machine, Δ-surface metrics (Jaccard / JS / affinity),
  flow/thermo-info (ΔF=H−T·S, ΔC, Rₑ, ℓ, η), the T₀–T₁₁ genesis braid, and the tripwire
  refusal sigmoid r(x)=σ(β(risk−θ)). Every glyph regenerable from data.
- **`b11-life-mirror.html`** — Tier 2. The runtime automaton: NORMAL→WATCHFUL→SAFE-HALT
  over the four spaces, tripwires (soft→hard→trip), receipted transitions, response ladder
  (zero-response→revoke/rotate; SAFE-HALT→owner-operated recovery; consent-QR→verify/rollback).
- **`lampstand-launcher.html`** — Tier 2, *actionable*. The Spotlight replacement: natural
  language → typed intents/entities/relations (the annotation tree) → **governed actions**
  (purpose-bound, consent-gated, receipted), ranked by sherlock (IR). Not web search — typed acts.
- **`docs-support.html`** — Tier 2, *grounded NLQA + support*. Answers only from the
  auto-generated docs index (`tools/build_docs_index.py`), cites every source, and **abstains**
  to support when a question isn't in the docs. A CI drift-guard keeps the index fresh from source.
- **`model-governance.html`** — Tier 2, *regulated model registry*. Business targets (fraud/churn/
  credit/AML/propensity) with champion-vs-challenger, historic version comparison, PSI drift, and the
  DataClass classifiers per target. Model risk management as a witness surface.
- **`model-catalog.html`** — Tier 2, *intersection cockpit*. Every foundation model + OS
  capability, cloud∩local placement, a sovereignty×governance-weighted leaderboard, and the
  SP-vs-Claude-Enterprise positioning (marked DRAFT/VERIFY). Backed by `inference-gateway-intersection.md`.
- **`genesis-flywheel.html`** — Tier 1. The install spine + growth dynamics: the T₀–T₁₁
  genesis braid (sealed, four-space colored), the five-phase zero-trust install, and the
  connected flywheel topology with correct ΔEP=(P−C)·X−λK / K=k₀·α·cov(A)·φ(P) /
  m(t+1)=σ(W·ΔEP+B·K+A·m) / Moufang equations.
- **`turn-witness.html`** — Tier 2, *verifiable*. Any chat turn annotated → **Gödel-numbered**
  (canonical G = ∏ pᵢ^codeᵢ, reproducible integrity fingerprint) → **consistency-checked** →
  **conclusions** with a sealed verdict. Demonstrates *well-formed ≠ admissible*: a turn can
  pass every structural check and still be refused (the destructive example escalates to Governor).
- **`e11-consent-receipts.html`** — Tier 2. The [E11](./e11-consent-receipts-ux.md) consent &
  receipts center (per-app purpose envelopes, sealed receipt timeline, Governor queue, residency).

## Provenance note
These replace a set of DALL·E renders that were aesthetically nice but factually garbled
(mangled equations, wrong state names, invented labels). Same visual language — parchment,
four-world color-coding, the vocabulary — now correct and reproducible. Both HTML surfaces
are self-contained, theme-aware (light + dark), and keyboard-accessible.

## Backlog (to finish Tier 1)
12-step braid + five-phase genesis as standalone Mermaid; flywheel topology (Trust/Growth/
Dev-Platform/Device loops); and the Tier-3 dynamics spec (ΔEP, K functional, m(t+1)
recurrence, Moufang identity) with each term's measurement source.
