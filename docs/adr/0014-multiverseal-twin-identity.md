# ADR-0014: Multiverseal Twin — the federation-facing identity/reputation projection

Status: Accepted
Date: 2026-08-01
Extends: ADR-0013 (digital-soul identity & reputation)

## Context

ADR-0013 gave us the private core (`DigitalSoulIdentity`), the reputation plane
(`ReputationDimension` / `SacredCapitalLedger` / `PortableReputationClaim`), and the
on-device `AscensionReading`. What it lacked was a principled, hardened object for the part
that actually touches the untrusted, federated world and carries imported non-first-party
reputation. The Multiverseal Twin spec supplies exactly that, on a single reference-gated
holographic substrate, with rigor-tiered guarantees. It also unifies three loose threads:
the "bind reputation to evidence" rule, the reversibility-distance privacy metric (from the
reidentification-economy dossier), and the "read movement not score" ambition.

## Decisions

1. **Core vs twin.** `DigitalSoulIdentity` is the sovereign, private, authoritative core.
   `MultiversealTwin` is its federation-facing projection — the only object relying parties
   watch. The core is never embedded in the twin; only reference-gated projections are.

2. **Reference-at-ingest (Powell–Stetson) is mandatory.** A foreign attestation is admitted
   only as `TwinAttestation` = `bind(object, r_c)` with a provenance envelope; a bare score is
   never summed into reputation. Reconcilability is manufactured at ingest. This is the
   holographic form of the capture-time receipt, and — per reidentification-economy §A.5 — the
   *only* place the purpose/authorization bit can live, because it is provably unrecoverable
   from the signal afterward.

3. **One budget: ε = capacity = crosstalk = unlinkability = reversibility distance.**
   `MultiversealTwin.unlinkability.epsilon` (Johnson–Lindenstrauss almost-orthogonality) is the
   single knob. It is explicitly the reversibility-distance ledger from the reidentification
   appendix — there is no separate "privacy parameter."

4. **Access control is the code threshold.** QEC `[[n,k,d]]` sharing: `d` = policy. Any region
   above `n−d` shares reconstructs; below reveals nothing. Resilience and privacy are one dial.

5. **Mint/verify asymmetry via VRF, anchored to the verified core.** Only the subject's master
   key mints; anyone verifies. The anchor is a `ProofOfSelfToken` (Identity-Is-Prime), tying
   "who may mint this twin" to a proven subject. Forgery reduces to breaking VRF.

6. **The impersonation wall is the top invariant.** A watchable persona of subject `u` mints
   only under `u`'s key or a `u`-signed capability; phase-retrieval hardening is mandatory
   (measurement starvation, per-view nonce, per-session references). This is the hard stop
   against "author a replayable someone-else."

7. **The primary read is the fringe, not the score.** `InterferometricDiff` reads phase drift
   (`Δφ`) between two twin states — a leading indicator that moves below scalar-score
   sensitivity, with global tamper-evidence for free. `AscensionReading` (ADR-0013) is the
   on-device, self-directed special case: a live diff of the holder's own twin over time. This
   is the operation that earns the name "prophet."

## Consequences

- New conformant contracts: `TwinAttestation`, `MultiversealTwin`, `InterferometricDiff`, with
  canonical examples and an invariant validator wired into `make validate`.
- Reputation's "bind to the fabric" rule (ADR-0013) is sharpened to "bind-at-ingest against a
  VRF reference," and `AscensionReading` is reframed as an interferometric read.
- The substrate is **linear by design**; Sybil-resistance and nonlinear trust policy stay in a
  separate layer that never leaks back into the holographic medium (open problem, tracked).
- Rigor is tiered per the source spec: holographic⇄QEC isomorphism and VRF forgery-reduction
  are theorems; the HRR/VSA substrate and coherence-length horizon are constructions/heuristics
  to quantify before production trust.
