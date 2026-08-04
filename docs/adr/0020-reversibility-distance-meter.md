# ADR-0020: Reversibility Distance — the civic meter of the reidentification economy

Status: Accepted
Date: 2026-08-03
Relates-to: ADR-0014 (multiverseal-twin identity)

## Context

ADR-0014 unified privacy, capacity and cross-context unlinkability into a single number:
`MultiversealTwin.unlinkability.epsilon`, described there as "the reversibility-distance
ledger from the reidentification-economy appendix." That appendix (reidentification-economy
Appendix A) defines the primitive more concretely than any twin field can carry, and it is
worth publishing on its own so that a release — not just a twin — can be metered.

The primitive: to single one subject out of a population of `N`, an adversary needs
`log2 N` bits of distinguishing information (the *singling-out budget*). The **reversibility
distance** `D = E[log2 k]` is the *residual* identity entropy: the expected bits still needed
given the anonymity-set size `k` each subject sits in. `D == 0` means the release is fully
reversible — every subject is already unique. `D` is exactly the ε-unlinkability budget of the
twin: privacy, capacity and reidentifiability are one ledger, not three knobs. The appendix
also fixes the estimator math (Poisson unicity closed form, the unicity-exponent fit) against
the Sweeney and de Montjoye worked examples — so the meter can be *proved*, not asserted.

## Decisions

1. **Publish `ReversibilityDistance` as a first-class contract.** A per-release/per-twin
   reading carrying `populationN`, `budgetBits = log2 N`, `dBits = D`, the `reidentified`
   flag, the `unicityCurve`, the fitted `bitsPerPoint = log2 r` and implied `pStar = log_r N`,
   plus the estimator `method`. URN prefix `urn:srcos:reversibility-distance:`.

2. **`D` is not a new privacy parameter — it is the twin's ε.** `epsilonUnlinkabilityRef`
   points back at the `MultiversealTwin` whose `unlinkability.epsilon` this `D` budgets.
   There is one ledger; this contract is its published face.

3. **Two orthogonal controls act on the same ledger, and only these two.** `controlPoints`
   names them: a differential-privacy mechanism that *rate-limits ΔD per release*, and a
   *capture receipt* that gates whether the identifying query `Q` is produced at all. One
   bounds the spend rate; the other bounds whether spending happens. They are orthogonal and
   both live against `D`.

4. **The estimator ships and self-proves.** `tools/reversibility_distance.py` is the
   self-contained (numpy-only) Appendix-A estimator: `unicity_closed_form`,
   `reversibility_distance`, `fit_unicity_exponent`. Its `__main__` self-test reproduces the
   appendix's worked examples (Sweeney N=2.48e8 → ε≈0.921; de Montjoye N=1.5e6 → r≈73.5, and
   the coarsened p=4/p=5 unicity points) with asserts and exits nonzero on mismatch. The meter
   is validated against the source math, not invented.

5. **Invariant validator, wired into `make validate`.** Beyond JSON Schema:
   `dBits >= 0`; `reidentified == (dBits == 0)`; unicity-curve `p` positive integers and
   `epsilon_p ∈ [0, 1]`; and `budgetBits ≈ log2(populationN)` within 0.01 so `D` is always
   measured against the correct ceiling.

## Consequences

- New conformant contract `ReversibilityDistance` with a canonical example, an invariant
  validator (`tools/validate_reversibility_distance_examples.py`) wired into `make validate`,
  and a self-proving reference estimator (`tools/reversibility_distance.py`).
- The reidentification-economy privacy metric now has a published, machine-checkable home;
  the twin's ε and a release's `D` are one number with two witnesses.
- The estimator's closed forms (Poisson unicity) and the unicity-exponent fit are constructions
  calibrated to the published examples; production trust in a specific release's `D` still
  depends on the fidelity of the anonymity-set counts fed to it.
