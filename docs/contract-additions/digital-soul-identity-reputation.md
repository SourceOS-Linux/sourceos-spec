# Contract additions — digital soul: identity & reputation

Adds the two-layer "digital soul" contract family: a private, given **identity**
layer and an earned, portable, privacy-preserving **reputation** layer
(Neighbourhoods + Sacred Capital lineage). Reputation binds to the existing
reasoning-evidence fabric — community attestations reference `ReasoningReceipt`
records of works; no parallel receipt type is introduced.

## Why (the three forks this closes)

1. **Lock the spine.** `IdentitySpine` commits the canonical inner object to the
   64-gate yi-globe. Every other tradition (zodiac, sefirot, enneagram, chakra,
   the twelve senses) is a registered one-way **projection** — presentation only,
   never a writable source of truth, never a measured/derived physical value.
2. **The dimension-schema join.** `ReputationDimension.latticeBinding` expresses a
   community's Sensemaker dimension in the spine's shared vocabulary (a gate or an
   inner axis). This is what turns Sacred Capital from portable *data* into portable
   *meaning*: bound dimensions are legible across neighbourhoods; unbound ones stay
   opaque. There is never a global score.
3. **The private reading.** `AscensionReading` is the single one-way bridge from
   reputation to identity: it reads the holder's own works-receipts back through the
   spine to move private gate-state along its inner axes ("ascension"). It is
   normatively **on-device** and **network-prohibited** — no party but the holder may
   compute or store the holder's inner state. This forecloses a "spiritual credit score".

## Contracts

| Schema | Layer | Purpose |
|---|---|---|
| `IdentitySpine` | identity (public-shared) | canonical 64-gate lattice + inner axes + one-way projections |
| `DigitalSoulIdentity` | identity (agent-held-private) | per-subject given inputs + gate-state; default disclosure none |
| `AscensionReading` | bridge (agent-held-private) | on-device works→inner-axes reading; replayable |
| `ReputationDimension` | reputation | community-authored context-local dimension + optional spine binding |
| `SacredCapitalLedger` | reputation (agent-held-portable) | evidence-backed capital per (neighbourhood, dimension); no global score |
| `PortableReputationClaim` | reputation | holder-minted, signed, selective disclosure; optional witnessed ascension |

## URN identifiers

| Type | URN prefix |
|---|---|
| `IdentitySpine` | `urn:srcos:identity-spine:` |
| `DigitalSoulIdentity` | `urn:srcos:digital-soul:` |
| `AscensionReading` | `urn:srcos:ascension-reading:` |
| `ReputationDimension` | `urn:srcos:reputation-dimension:` |
| `SacredCapitalLedger` | `urn:srcos:sacred-capital:` |
| `PortableReputationClaim` | `urn:srcos:reputation-claim:` |

## Binding to the evidence fabric

Reputation is evidence-backed by reuse, not by a new receipt type:

- works/acts in the knowledge commons are recorded as `ReasoningReceipt`
  (`urn:srcos:reasoning-receipt:`) on the existing v2 reasoning-evidence fabric;
- `ReputationDimension.computedOver` scores those receipts/`ReasoningEvent` types;
- `SacredCapitalLedger.entries[].evidenceRefs` and
  `PortableReputationClaim.*.evidenceRefs` point at those receipts;
- `AscensionReading.replayPlanRef` may bind to a `ReasoningReplayPlan` so a reading
  is replayable like any reasoning run.

## Enforced invariants (machine-checked)

`tools/validate_digital_soul_examples.py` (wired into `make validate` via
`validate-digital-soul-examples`) checks, beyond JSON Schema:

- **Privacy boundary** — no reputation document may contain any given-identity key
  (`birthdate` / `faith` / `personality*` / `givenInputs`). The boundary holds by
  construction: the reputation schemas provide no field able to carry them.
- **Directionality** — `AscensionReading` must be on-device, `networkServiceProhibited`,
  and declare works→inner-axes `allowed` / identity-inputs→reputation `forbidden`.
- **Evidence backing** — capital entries and claimed dimensions must each reference
  at least one works-receipt; no document asserts a global score.
- **Spine integrity** — exactly 64 unique gates.

## Validate

```bash
make validate-digital-soul-examples
```

## CHANGELOG entry (ready to merge into [Unreleased] → Added)

- Digital-soul contract family — identity (`IdentitySpine`, `DigitalSoulIdentity`)
  and reputation (`ReputationDimension`, `SacredCapitalLedger`,
  `PortableReputationClaim`) plus the one-way on-device bridge (`AscensionReading`),
  with canonical examples and a privacy-boundary + directionality validator
  (`tools/validate_digital_soul_examples.py`). Reputation binds to the
  reasoning-evidence fabric via `ReasoningReceipt`/`ReasoningReplayPlan`; the
  canonical spine is locked to the 64-gate yi-globe with all other traditions as
  one-way projections.
