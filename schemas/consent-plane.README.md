# Consent plane — opt-in, explained, revocable, self-sovereign

Two contracts that record **how consent gates observation and action** in a self-sovereign
deployment. They are governance documents: they classify surfaces, pin defaults, and hold the
sentence a person is shown before anything is enabled. **They contain no capture code** — no
collector, no transport, no payload shape, no invocation path. A surface can be fully registered
here and permanently unobserved, which is exactly how a sensitive surface is meant to appear: as a
default-deny row that makes the *non*-collection auditable instead of merely absent.

The inversion is structural, not aspirational. `deploymentScope` is `const: "self-sovereign"` and
`collectorPrincipal` must equal `subjectPrincipal`, so **a document describing one party collecting
from another is not expressible in this family.**

## Schemas

| Schema | URN prefix | Governs |
|---|---|---|
| `ConsentSurfaceRegistry.json` | `urn:srcos:consent-registry:` | Passive telemetry surfaces — what *may be observed*. Classification + consent state only. |
| `CapabilityConsentPolicy.json` | `urn:srcos:consent-policy:` | Active capabilities — what *may be done* on the subject's behalf. |

### The deliberate asymmetry

Telemetry surfaces ship at `standing-persistent`; active capabilities ship at `per-use`. That gap is
the design, not an inconsistency. A passive counter you opted into once should not re-interrupt you
forever, but a camera that asks once and remembers the answer has stopped being consent. The one
exception is `microphone` (`standing-session`): a per-utterance prompt makes continuous listening
unusable, so the honest mitigation is a session bound rather than a prompt nobody reads.

### Canonical shipped defaults (pinned in the gate)

| Capability | riskClass | defaultStandard | defaultState | oneShot |
|---|---|---|---|---|
| `camera` | sensor-capture | `per-use` | disabled | ✅ |
| `screen_capture` | sensor-capture | `per-use` | disabled | ✅ |
| `microphone` | sensor-capture | `standing-session` | disabled | — |
| `control_my_computer` | device-control | `per-use` | disabled | ✅ |
| `skycomputer` | remote-compute | `per-use` | disabled | ✅ |
| `file_write` | data-write | `per-use` | disabled | ✅ |
| `network_egress` | data-egress | `per-use` | disabled | ✅ |
| `send_on_behalf` | act-as-user | `per-use` | disabled | ✅ |

The matrix lives in `tools/validate_consent_plane_examples.py`, not only in the example. An example
is a file anyone can edit; a gate is a thing you have to argue with.

## The five invariants (CI-enforced, each proven to bite)

`make validate-consent-plane-examples` runs schema conformance plus:

- **(a) self-sovereign** — `collectorPrincipal == subjectPrincipal`.
- **(b) default-deny** — the registry schema must *declare* `consent.state` default `denied`; a
  `granted` surface must carry `grantedAt` + `grantRef` and a `revoked` one `revokedAt` + `grantRef`
  (a state cannot be edited into existence — it must point at something that happened); and every
  per-use capability must ship `defaultState: disabled`.
- **(c) canonical defaults** — every capability in the matrix must be **present** (absence from the
  policy is not a safe default, it is *ungoverned*) with its pinned `defaultStandard`; and
  `effectiveMode` may diverge from `defaultStandard` only when `userOverride` is true. The same
  attributability rule is applied to a **granted** surface; a denied or revoked surface is `off` by
  consequence of consent, not by override, and is exempt.
- **(d) one-shot** — a per-use capability must be `oneShot: true` and may never sit in a standing
  mode, *not even behind `userOverride`*. The subject may always tighten; nothing may loosen a
  per-use capability into a standing one. Per-use without one-shot is the exact hole through which
  one "allow" becomes a permanent permission.
- **(e) explanation** — every surface and capability carries a non-trivial plain sentence. Consent
  to something unexplained is not consent, so the sentence is a structural precondition of
  registering the thing at all. Length alone does not satisfy it: placeholder text and
  single-word-repeated filler are rejected.

Each invariant is pinned by a **synthetic negative control that runs on every invocation** (16 of
them). If any control fails to trip, the validator exits non-zero and certifies nothing — the
`tools/validate_schema_references.py` discipline. The controls are built from in-memory documents
only and never read or mutate `examples/`, so the proof cannot pollute the thing being proven.

## Examples

| Example | Shows |
|---|---|
| `examples/consent_surface_registry.json` | Two **benign** granted surfaces (`model:tokens_used`, `policy:gate_verdict` — the latter demonstrating an attributed `userOverride` divergence), one **sensitive** surface (`device:hardware_id`) present purely as a default-deny classification row with `OPAQUE_HANDLE_ONLY` projection and nothing reading it, and one **revoked** surface (`app:session_start`) showing that a withdrawal stays legible rather than decaying back into an indistinguishable "denied". |
| `examples/capability_consent_policy.json` | The full canonical set at shipped defaults, all `disabled`, with `microphone` tightened to `off` under an attributed `userOverride` — the only direction an override is allowed to move. |

Only benign surfaces are granted anywhere in the example set. The sensitive and personal rows exist
to demonstrate the classification, and both are off.

## What this family deliberately does not do

- It defines **no capture mechanism**. Nothing here says how a value would be read, encoded, or
  moved; `projectionMode` describes what a projection *would be permitted to be*, not a codec.
- It grants nothing at runtime. `grantRef` points at a grant record held elsewhere
  (`mcp-a2a-zero-trust` owns `Grant`/`AttestationBundle` — this family conforms to that authority
  rather than re-inventing it) so that a consent state in this file cannot be self-issued.
- `projectionMode` reuses the semantic-serdes SEM243 vocabulary (`LOSSLESS` / `LOSSY` /
  `OPAQUE_HANDLE_ONLY`) so the consent board and the codec speak the same word.
