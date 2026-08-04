#!/usr/bin/env python3
"""pytest wiring for the reversibility-distance reference estimator (E13/WS-D).

`reversibility_distance.py` ships a `__main__` self-test that reproduces the
reidentification-economy appendix's worked examples (Sweeney, de Montjoye) with
asserts — but nothing invoked it: it was not on any Makefile target and, living
outside a `test_*.py` name, `pytest tools/ -q` (.github/workflows/tools-tests.yml)
silently skipped it too. A verification argument that is never executed proves
nothing about the PR that shipped it. This file makes the appendix math a real,
CI-collected pytest suite: the worked-example checks as individual assertions
(so a regression names the specific broken number, not just "self-test failed"),
plus the guard clauses (division-by-zero / log-of-non-positive) the estimator
relies on to stay well-defined, plus the `__main__` entry point itself.
"""
from __future__ import annotations

import math

import pytest

from reversibility_distance import (
    _selftest,
    fit_unicity_exponent,
    reversibility_distance,
    unicity_closed_form,
)


# --------------------------------------------------------------------------- #
# Appendix A worked examples — pinned as individual assertions
# --------------------------------------------------------------------------- #


def test_example_a_sweeney_lambda_and_epsilon():
    N_a, S_a = 2.48e8, 2**31.51
    eps_a, lam_a = unicity_closed_form(N_a, S_a)
    assert lam_a == pytest.approx(0.0818, abs=0.005)
    assert eps_a == pytest.approx(0.921, abs=0.01)


def test_example_b_de_montjoye_lambda_and_r():
    N_b = 1.5e6
    lam_b = -math.log(0.95)
    assert lam_b == pytest.approx(0.05129, abs=0.001)
    r_b = (N_b / lam_b) ** (1.0 / 4.0)
    assert r_b == pytest.approx(73.5, abs=1.0)


def test_example_b_coarsened_resolution_epsilon_curve():
    """Halve r (coarsen the resolution) and re-evaluate at p=4 and p=5."""
    N_b = 1.5e6
    lam_b = -math.log(0.95)
    r_coarse = ((N_b / lam_b) ** (1.0 / 4.0)) / 2.0

    eps_c4 = math.exp(-N_b * r_coarse ** (-4))
    assert eps_c4 == pytest.approx(0.44, abs=0.03)

    eps_c5 = math.exp(-N_b * r_coarse ** (-5))
    assert eps_c5 == pytest.approx(0.978, abs=0.01)


def test_fit_unicity_exponent_recovers_the_coarsened_r():
    """The fit is exercised against its own two generated points, not invented data."""
    N_b = 1.5e6
    lam_b = -math.log(0.95)
    r_coarse = ((N_b / lam_b) ** (1.0 / 4.0)) / 2.0
    eps_c4 = math.exp(-N_b * r_coarse ** (-4))
    eps_c5 = math.exp(-N_b * r_coarse ** (-5))

    fit = fit_unicity_exponent([4, 5], [eps_c4, eps_c5])
    assert math.exp(fit["ln_r"]) == pytest.approx(r_coarse, abs=1.0)


def test_reversibility_distance_zero_for_unique_rows():
    assert reversibility_distance([1, 1, 1]) == pytest.approx(0.0, abs=1e-12)


def test_reversibility_distance_is_log2_of_anonymity_set_size():
    assert reversibility_distance([4, 4]) == pytest.approx(2.0, abs=1e-12)


# --------------------------------------------------------------------------- #
# Guard clauses — division by zero / log of non-positive must not crash silently
# --------------------------------------------------------------------------- #


def test_unicity_closed_form_rejects_zero_signatures():
    """S=0 would divide by zero (lambda = N/S); must raise, not return inf/nan."""
    with pytest.raises(ValueError):
        unicity_closed_form(1000.0, 0.0)


def test_unicity_closed_form_rejects_negative_signatures():
    with pytest.raises(ValueError):
        unicity_closed_form(1000.0, -5.0)


def test_reversibility_distance_rejects_empty_counts():
    """An absent probe must not silently read as D=0 (fully reversible)."""
    with pytest.raises(ValueError):
        reversibility_distance([])


def test_reversibility_distance_rejects_anonymity_set_below_one():
    """k < 1 is not a valid anonymity-set size and would make log2(k) negative/undefined."""
    with pytest.raises(ValueError):
        reversibility_distance([0.5])


def test_fit_unicity_exponent_rejects_fewer_than_two_points():
    with pytest.raises(ValueError):
        fit_unicity_exponent([4], [0.5])


def test_fit_unicity_exponent_rejects_epsilon_at_the_boundary():
    """epsilon_p must be strictly in (0, 1): log(-log(eps)) is undefined at 0 or 1."""
    with pytest.raises(ValueError):
        fit_unicity_exponent([4, 5], [0.0, 0.5])
    with pytest.raises(ValueError):
        fit_unicity_exponent([4, 5], [0.5, 1.0])


# --------------------------------------------------------------------------- #
# The __main__ self-test entry point itself — the thing the PR/ADR cites as
# "proves the estimator against the source math" must actually run in CI.
# --------------------------------------------------------------------------- #


def test_the_selftest_entry_point_passes():
    assert _selftest() == 0
