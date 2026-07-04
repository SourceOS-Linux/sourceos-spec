# ADR-0013: Digital soul — identity and reputation planes

Status: Accepted
Date: 2026-06-29

## Context

The platform is adding a "digital soul" capability: a per-person identity model
drawn from a syncretic correspondence map (yi-globe, sefirot, zodiac, enneagram,
chakra, the twelve senses) plus a reputation model in the Neighbourhoods + Sacred
Capital lineage (distributed, portable, privacy-preserving). The source is a visual
map, not a written spec, so the contracts had to make the implicit architecture
explicit and safe.

Two distinct identity senses already exist in the estate and must not be conflated:

- **Verified identity** — `ProofOfSelfToken` / Identity Is Prime: *am I a real,
  deduplicated subject?* (proof and entity-resolution plane).
- **Constitutional identity** — the digital soul: *who am I inwardly?* (given,
  symbolic plane).

## Decisions

1. **Lock the spine.** The canonical inner object is the 64-gate yi-globe
   (`IdentitySpine.canonicalSpine = "yi-globe-64gate"`, exactly 64 gates). Every
   other tradition is a registered **one-way projection** (`oneWay: true`,
   `sourceOfTruth: false`, `symbolic: true`) — presentation only, never writable,
   never a measured or physically derived value. This honors the settled
   matter/form premise without faked numeric derivations.

2. **Two planes, opposite truth-makers.** Identity is *given* and asserted
   (`DigitalSoulIdentity`, private, default disclosure none). Reputation is *earned*
   and witnessed (`ReputationDimension`, `SacredCapitalLedger`,
   `PortableReputationClaim`). Reputation's truth-maker is the existing
   reasoning-evidence fabric — attestations reference `ReasoningReceipt` /
   `ReasoningReplayPlan`; no parallel receipt type is introduced.

3. **Privacy boundary by construction.** No reputation contract has any field able
   to carry a given identity input (birthdate / faith / personality). The boundary
   cannot be crossed by mistake; it is also machine-checked
   (`tools/validate_digital_soul_examples.py`).

4. **One on-device, one-way bridge.** `AscensionReading` reads the holder's own
   works-receipts back onto private inner axes ("ascension"). It is normatively
   on-device and `networkServiceProhibited`: no party but the holder may compute or
   store inner state. Inner state reaches the outside world only via a deliberate,
   holder-minted `PortableReputationClaim`. This forecloses a "spiritual credit
   score".

5. **Portable meaning, not a global score.** `ReputationDimension.latticeBinding`
   expresses a community's subjective dimension in the shared spine vocabulary, so
   capital is legible across neighbourhoods when bound and opaque when not.
   `SacredCapitalLedger.noGlobalScore = true`; aggregation is only within a
   (neighbourhood, dimension) or via a declared binding.

6. **Cross-plane anchoring is optional and pseudonymous.**
   `DigitalSoulIdentity.proofOfSelfRef` may anchor the constitutional soul to a
   `ProofOfSelfToken` so reputation is sybil-resistant. The anchor is pseudonymous
   and carries no given-identity data. Identity Is Prime remains the proof/evidence
   layer (see `identity-is-prime-reference/docs/70_PLATFORM_IDENTITY_CONTRACT_ADAPTER`);
   the digital soul is a separate constitutional layer that may reference it.

## Consequences

- Conformant new schemas under `schemas/` with canonical examples, a validator wired
  into `make validate`, and a contract-additions note.
- The full per-tradition correspondence tables (gate → sign/sefira/enneatype/…) are
  deliberately **not** committed here: they are frontier-authored canon to be added
  as separate, sourced projection data files and validated independently, rather than
  fabricated inline.
- Home is `sourceos-spec` (the canonical typed-contracts repo), not
  `identity-is-prime-reference` (a mathematical reference implementation).
