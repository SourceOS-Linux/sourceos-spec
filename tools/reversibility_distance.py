#!/usr/bin/env python3
"""Reference estimator for the reversibility distance D (reidentification-economy Appendix A).

Reversibility distance is the civic primitive of the reidentification economy: for a
population of N, singling one subject out costs budgetBits = log2(N) bits of distinguishing
information. D = E[log2 k] is the *residual* identity entropy — the bits an adversary must
still acquire to reidentify. D == 0 means the release is fully reversible. D is the same
number as a MultiversealTwin's epsilon-unlinkability budget: privacy, capacity and
reidentifiability are one ledger.

This module is self-contained (numpy only — no pandas). Three primitives:
  * unicity_closed_form(N, S): Poisson approximation of uniqueness. With S distinguishable
    signatures spread over N subjects, the expected collision rate is lambda = N / S and the
    fraction of *unique* subjects is epsilon ~= exp(-lambda). Returns (epsilon, lambda).
  * reversibility_distance(counts): D = mean(log2(k)) over the per-row anonymity-set sizes k.
  * fit_unicity_exponent(p_values, eps_values): least-squares fit of the unicity curve
    ln(-ln epsilon_p) = ln N - p * ln r, recovering the per-point distinguishability r
    (and bits_per_point = log2 r) and the implied population.

The __main__ SELF-TEST reproduces the appendix's worked examples with asserts. The numbers
are the appendix's; this proves the estimator against the source math rather than inventing.
"""
from __future__ import annotations

import math
import sys

import numpy as np


def unicity_closed_form(N: float, S: float) -> tuple[float, float]:
    """Poisson closed-form uniqueness.

    lambda = N / S is the mean number of subjects sharing a signature; the fraction of
    subjects that are unique is epsilon ~= exp(-lambda). Returns (epsilon, lambda).
    """
    if S <= 0:
        raise ValueError("S (number of distinguishable signatures) must be > 0")
    lam = N / S
    eps = math.exp(-lam)
    return eps, lam


def reversibility_distance(counts) -> float:
    """D = mean(log2(k)) — the residual identity entropy in bits.

    `counts` is the anonymity-set size k for each row (k = 1 means already singled out,
    contributing 0 bits). D == 0 iff every row is unique.
    """
    c = np.asarray(counts, dtype=float)
    if c.size == 0:
        raise ValueError("counts must be non-empty")
    if np.any(c < 1):
        raise ValueError("anonymity-set sizes k must be >= 1")
    return float(np.mean(np.log2(c)))


def fit_unicity_exponent(p_values, eps_values) -> dict:
    """Least-squares fit of the unicity curve.

    Model: epsilon_p = exp(-N * r**-p), so ln(-ln epsilon_p) = ln N - p * ln r.
    We regress y = ln(-ln epsilon_p) on x = p: slope = -ln r, intercept = ln N.
    Returns ln_r, bits_per_point = ln_r/ln2, ln_N_est and implied_N.
    """
    p = np.asarray(p_values, dtype=float)
    eps = np.asarray(eps_values, dtype=float)
    if p.size != eps.size or p.size < 2:
        raise ValueError("need >= 2 matched (p, epsilon) points")
    if np.any(eps <= 0) or np.any(eps >= 1):
        raise ValueError("epsilon_p must lie strictly in (0, 1) to fit the double-log")
    y = np.log(-np.log(eps))
    slope, intercept = np.polyfit(p, y, 1)
    ln_r = -float(slope)
    ln_N_est = float(intercept)
    return {
        "ln_r": ln_r,
        "bits_per_point": ln_r / math.log(2),
        "ln_N_est": ln_N_est,
        "implied_N": math.exp(ln_N_est),
    }


def _selftest() -> int:
    failures: list[str] = []

    def check(label: str, got: float, want: float, tol: float) -> None:
        ok = abs(got - want) <= tol
        print(f"  {'OK ' if ok else 'FAIL'} {label}: got {got:.6g}, want {want:g} (+/- {tol:g})")
        if not ok:
            failures.append(label)

    print("Example A (Sweeney): N=2.48e8, H_Q=31.51 bits -> S=2**31.51")
    N_a = 2.48e8
    S_a = 2 ** 31.51
    eps_a, lam_a = unicity_closed_form(N_a, S_a)
    check("A lambda", lam_a, 0.0818, 0.005)
    check("A epsilon", eps_a, 0.921, 0.01)

    print("Example B (de Montjoye baseline): N=1.5e6, epsilon=0.95 at p=4")
    N_b = 1.5e6
    lam_b = -math.log(0.95)
    check("B lambda(from eps=0.95)", lam_b, 0.05129, 0.001)
    r_b = (N_b / lam_b) ** (1.0 / 4.0)
    check("B r (per-point distinguishability)", r_b, 73.5, 1.0)

    # Coarsen the resolution: halve r, re-evaluate the same p=4 join depth.
    r_coarse = r_b / 2.0
    lam_c4 = N_b * r_coarse ** (-4)
    eps_c4 = math.exp(-lam_c4)
    check("B epsilon at p=4, r/2", eps_c4, 0.44, 0.03)

    # One more join at the coarsened resolution.
    lam_c5 = N_b * r_coarse ** (-5)
    eps_c5 = math.exp(-lam_c5)
    check("B epsilon at p=5, r/2", eps_c5, 0.978, 0.01)

    print("Sanity: fit_unicity_exponent recovers the coarsened r from its own two points")
    fit = fit_unicity_exponent([4, 5], [eps_c4, eps_c5])
    check("fit implied r", math.exp(fit["ln_r"]), r_coarse, 1.0)

    print("Sanity: reversibility_distance is 0 for unique rows, log2 k otherwise")
    check("D([1,1,1])", reversibility_distance([1, 1, 1]), 0.0, 1e-12)
    check("D([4,4])", reversibility_distance([4, 4]), 2.0, 1e-12)

    if failures:
        print(f"\nSELF-TEST FAILED: {failures}")
        return 1
    print("\nAll reversibility-distance self-tests passed (reproduce Appendix A).")
    return 0


if __name__ == "__main__":
    sys.exit(_selftest())
