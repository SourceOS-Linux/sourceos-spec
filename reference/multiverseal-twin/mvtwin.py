"""Multiverseal Twin — reference implementation of the holographic substrate.

Epoch E13 / WS-C. Executable substrate for the contracts in
schemas/{MultiversealTwin,TwinAttestation,InterferometricDiff}.json (ADR-0014).

Instantiated on FHRR (Fourier Holographic Reduced Representations, Plate): the twin space
is V = C^D of unit-modulus phasors, so *phase = provenance* is literal. Three operators:

    bind(o, r)   = o ⊙ r            record object o against reference r
    bundle(ts)   = Σ t_k            superpose records into the opaque twin medium H
    unbind(H, r) = H ⊙ conj(r)      correlate with the reference to reconstruct

Reference-gating: without r_j, H is a sum of pseudo-random phasors — a hiding commitment;
reconstruction requires the reference (the public-twin / private-reconstruction primitive).
The primary read is the fringe (Δφ), not the score. This module is the linear substrate ONLY;
Sybil-resistance and nonlinear trust policy live in a separate layer (twin spec §H / WS-F).
"""
from __future__ import annotations
import numpy as np


def reference(D: int, rng: np.random.Generator) -> np.ndarray:
    """A near-orthogonal, high-entropy unit-modulus reference r_c.

    Stands in for a VRF-derived context reference: VRF outputs are pseudorandom, hence the
    near-orthogonal references §A/§1 of the spec assume. Mint/verify and the ε-budget share
    this one primitive.
    """
    return np.exp(1j * rng.uniform(0.0, 2.0 * np.pi, size=D))


def obj(D: int, rng: np.random.Generator) -> np.ndarray:
    """An attestation's object beam o_k (a claim vector), as a unit-modulus phasor."""
    return np.exp(1j * rng.uniform(0.0, 2.0 * np.pi, size=D))


def bind(o: np.ndarray, r: np.ndarray) -> np.ndarray:
    """t = bind(o, r). Reference-at-ingest: a foreign claim is admitted only bound."""
    return o * r


def bundle(ts: list[np.ndarray]) -> np.ndarray:
    """H = Σ t_k. The superposed, opaque-without-a-reference twin medium."""
    return np.sum(np.stack(ts, axis=0), axis=0)


def unbind(H: np.ndarray, r: np.ndarray) -> np.ndarray:
    """ô = unbind(H, r) = H ⊙ conj(r); returns o + crosstalk η."""
    return H * np.conjugate(r)


def similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Normalized real correlation in [-1, 1]; the 'magnitude' (raw score) read."""
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.real(np.vdot(a, b)) / (na * nb))


def interferometric_diff(H_live: np.ndarray, H_stored: np.ndarray) -> np.ndarray:
    """The primary read: the fringe Δφ = arg(H_live ⊙ conj(H_stored)).

    Phase moves below the magnitude at which a scalar score would move (leading indicator).
    A local unauthorized write perturbs the fringe globally (tamper-evident for free).
    """
    return np.angle(H_live * np.conjugate(H_stored))


def unlinkability_leakage(r_a: np.ndarray, r_b: np.ndarray) -> float:
    """L(c,c') = |<r_c, r_c'>| / D. Two contexts are ε-unlinkable iff this ≤ ε.

    The SAME ε bounds crosstalk, capacity, and unlinkability — and is the reversibility-
    distance budget of the reidentification economy.
    """
    D = r_a.shape[0]
    return float(np.abs(np.vdot(r_a, r_b)) / D)
