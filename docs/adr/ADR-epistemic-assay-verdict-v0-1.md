# ADR: The Epistemic Assay — Verdicts as Projections, Not Scalars (v0.1)

## Status

Proposed.

## Context

The operational health of a subsystem is well modelled by a tri-state readout — `ok` / `sad` / `bad`
(came up / degraded-but-survived / hard failure). These are mutually exclusive states of a single
thing (the outcome of an operation), and the middle state is deliberately first-class.

That same three-state readout was being reached for to describe the trustworthiness of a **claim**.
This conflates concerns that are not points on one severity scale. Recent evaluation work surfaced at
least four independent facts hiding behind a single "confidence" pixel:

- **method** — was the claim computed, retrieved, or generated? These behave as decorrelated *classes*,
  not degrees; the verified-compute arm is decorrelated from grounding arms precisely because it is a
  different method.
- **binding time** — was the supporting evidence produced *inline* with the computation, or attached
  *post-hoc*? Generative paths are post-hoc bound; only deterministic paths are inline. A post-hoc
  "verified" is a different animal from an inline one, and nothing recorded which was obtained.
- **verifier authority** — who judged, and how reliable is that judge, *measured*? A deployed verifier
  grading at low F1 with only "slight" inter-rater agreement does not issue a weaker verdict — it
  issues an **unanchored** one, because its own reliability is unrecorded.
- **agreement** — arm concurrence overstates confidence when arms are correlated (they fail together),
  so raw "N arms agree" is closer to one vote than N.

Collapsing orthogonal axes into one stored scalar is the design flaw. It also makes history
un-re-judgeable: when the verifier improves, every past verdict is stuck at the reliability it was
stamped with.

## Decision

### 1. Keep the tri-state readout for operational health; do not store it as a claim's verdict

`ok` / `sad` / `bad` remains the canonical readout for operational outcomes. For **claims**, the verdict
is no longer a stored scalar.

### 2. Introduce `ReasoningAssay` — a typed verdict over five orthogonal axes

`schemas/ReasoningAssay.json` records `method`, `binding`, `verifier`, `agreement`, and `authority`.
The `ok` / `sad` / `bad` value (`projectedState`) is a **render-time projection** of these axes, cached
at `assayedAt` and re-derivable — never the source of truth. This is the "operation ⊥ verdict" principle
(separate the fact from the judgement so history stays re-judgeable) applied to epistemics.

The projection is defined so that:

- `ok` requires inline binding **and** an attestable method (computed/retrieved) **and** a calibrated verifier;
- `sad` ("unassayed") covers everything real-but-unresolved — post-hoc binding, generation-with-citations,
  an uncalibrated verifier, or correlated-arm agreement. The amber band is deliberately wide and *earned*;
- `bad` covers refuted / failed / authority-broken.

### 3. Introduce `AssayStandard` — the verifier's measured reliability as canon

`schemas/AssayStandard.json` records a verifier's confusion matrix, sample size, optional derived metrics
and inter-rater agreement, and a `calibrated` flag, versioned per measurement. A `ReasoningAssay`'s
`verifier.calibrationRef` **must** point at one; a verdict without it cannot project above `sad`. This
gives "who verifies the verifier" a mechanical answer: the verifier's own measured receipts. Re-measuring
publishes a new version, and referencing assays re-project against it — the same discipline as keeping
every benchmark arm rather than only its current winner.

### 4. The projection is executable and CI-enforced

`tools/validate_reasoning_examples.py` recomputes `assay()` from each example's stored axes and fails the
build if the recorded `projectedState` does not follow from them. The projection cannot silently drift from
the axes it claims to summarise.

## Consequences

- On the current stack, essentially only inline-bound verified-compute paths project to `ok`. This is
  honest, and renders the verified-compute moat directly as UX.
- Authenticity is a property of the actor/channel (mirroring `EventEnvelope.actor`/`integrity`), so a
  confident-sounding answer cannot launder its own authority.
- The single highest-leverage follow-on is populating real `AssayStandard` records from verifier calibration
  runs, so production verdicts reference measured — not assumed — reliability.

## Non-goals

- This ADR does not change operational-health telemetry.
- It does not mandate a runtime; it defines the canonical shapes that emitters (e.g. superconscious,
  agentplane evidence sealing) conform to.
