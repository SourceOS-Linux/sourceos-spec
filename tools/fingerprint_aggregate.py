#!/usr/bin/env python3
"""Reference semantics for the six-layer fingerprint stack (SP-FPRINT-STACK-001).

Everything here is RECOMPUTABLE: pooling, guard application, quantization, and effective
independence. The stored fields in ColumnFingerprint / ClassificationStance are caches, and
the validator recomputes them so an asserted stance cannot outrun its evidence.

Order matters and is the safety property. Pool -> guard -> quantize. Guards can only lower
stance in the knowledge order, and quantization to the four-valued stance happens LAST, so
no composition of guards can raise necessity or turn ZERO into POS.

This module also carries the M5 property test AND a deliberately non-monotone aggregator
used to prove that test bites. A monotonicity test that only ever sees a monotone model is
vacuous — that is not hypothetical here, it is the exact defect found in the trained
DataClass classifiers (#265), where the fixture held the monotone feature constant and the
constraint therefore had no teeth.
"""
from __future__ import annotations

from itertools import product

# Knowledge order <=_k on FOUR, as (support, refute) bits.
# ZERO=(0,0) <=_k POS=(1,0), NEG=(0,1) <=_k INADMISSIBLE=(1,1); POS and NEG incomparable.
BITS: dict[str, tuple[int, int]] = {
    "ZERO": (0, 0),
    "POS": (1, 0),
    "NEG": (0, 1),
    "INADMISSIBLE": (1, 1),
}
FROM_BITS = {v: k for k, v in BITS.items()}

TOL = 1e-9


def leq_k(a: str, b: str) -> bool:
    """a <=_k b — componentwise on the support/refute bits."""
    (a1, a2), (b1, b2) = BITS[a], BITS[b]
    return a1 <= b1 and a2 <= b2


def quantize(alpha: float, beta: float, tau_pos: float, tau_neg: float) -> str:
    """Q_{tau+,tau-}(alpha, beta) = (1[alpha >= tau+], 1[beta >= tau-]).

    Q commutes with negation iff tau_pos == tau_neg. Asymmetric thresholds break
    negation-equivariance: deny-rules stop coming free by negating allow-rules and a
    separate deny path has to be maintained. The validator therefore requires an
    attestation for any asymmetry.
    """
    return FROM_BITS[(int(alpha >= tau_pos - TOL), int(beta >= tau_neg - TOL))]


def pool(pairs: list[tuple[float, float]], operator: str = "frechet-max") -> tuple[float, float]:
    """Pool evidence across ADMISSIBLE layers.

    Default is the Frechet bound (max alpha, max beta), which assumes nothing about
    dependence. Its known cost is idempotence — ten corroborating layers buy nothing over
    one — and that is deliberate: corroboration pays only where the right to claim it has
    been earned via a certified independence model, which licenses probabilistic sum for
    the specific layer pair it certifies.
    """
    if not pairs:
        return (0.0, 0.0)
    if operator == "frechet-max":
        return (max(a for a, _ in pairs), max(b for _, b in pairs))
    if operator == "probabilistic-sum":
        a = b = 0.0
        for pa, pb in pairs:
            a = a + pa - a * pa
            b = b + pb - b * pb
        return (min(a, 1.0), min(b, 1.0))
    raise ValueError(f"unknown pooling operator: {operator!r}")


def admissible_pairs(layer_evidence: list[dict]) -> list[tuple[float, float]]:
    """Only admissible layers contribute. An inadmissible layer contributes ZERO — the
    tensor annihilator — never a guessed or imputed value."""
    out = []
    for le in layer_evidence:
        if (le.get("admissibility") or {}).get("admissible"):
            ev = le.get("evidence") or {}
            out.append((float(ev.get("alpha", 0.0)), float(ev.get("beta", 0.0))))
    return out


def n_eff(spectrum: list[float]) -> float:
    """Effective number of independent layers = participation ratio of the layer
    covariance spectrum, (sum lambda)^2 / sum lambda^2.

    NOT the Herfindahl index. H measures concentration of MAGNITUDE, not dependence: two
    perfectly correlated layers contributing equally give H = 0.5, which looks healthy,
    while supplying one layer's worth of information. H catches 'one layer dominates'; it
    does not catch 'my layers are secretly the same layer', which is the failure that
    matters for quorum.
    """
    s1 = sum(spectrum)
    s2 = sum(x * x for x in spectrum)
    if s2 <= 0:
        return 0.0
    return (s1 * s1) / s2


def monotone_aggregate(pairs: list[tuple[float, float]]) -> tuple[float, float]:
    """Reference aggregator satisfying M1/M2/M4/M5 STRUCTURALLY.

    M1 alpha non-decreasing in each input alpha; M2 beta non-decreasing in each input beta;
    M4 all-ZERO in => ZERO out; M5 knocking a layer out never RAISES the result.

    Structural, not regularization-encouraged: a penalty term makes M5 probabilistic, which
    voids the gate-soundness argument. A library offering only soft monotonicity is rejected
    on exactly those grounds.
    """
    return pool(pairs, "frechet-max")


def NON_MONOTONE_AGGREGATE(pairs: list[tuple[float, float]]) -> tuple[float, float]:
    """A deliberately BROKEN aggregator, used only to prove the M5 test has teeth.

    It subtracts a corroboration penalty, so adding a supporting layer can LOWER alpha and
    removing one can RAISE it — precisely the M5 violation. If check_m5_binds() ever passes
    this function, the property test is vacuous and the validator fails.
    """
    if not pairs:
        return (0.0, 0.0)
    a = max(p[0] for p in pairs) - 0.15 * (len(pairs) - 1)
    b = max(p[1] for p in pairs)
    return (max(a, 0.0), min(b, 1.0))


def m5_violations(aggregate, grid: int = 3) -> list[str]:
    """Property-test M5 over a grid of evidence vectors: for every layer set and every
    single-layer knockout, the knocked-out result must be <=_k the full result.

    Returns the violations found. An aggregator is M5-sound iff this is empty.
    """
    steps = [i / (grid - 1) for i in range(grid)]
    violations: list[str] = []
    for n in (2, 3):
        for combo in product(product(steps, steps), repeat=n):
            pairs = [tuple(c) for c in combo]
            full = aggregate(pairs)
            for i in range(n):
                knocked = [p for j, p in enumerate(pairs) if j != i]
                out = aggregate(knocked)
                # Lowering in the knowledge order is componentwise <= on (alpha, beta).
                if out[0] > full[0] + TOL or out[1] > full[1] + TOL:
                    violations.append(f"knockout of layer {i} from {pairs} RAISED {full} -> {out}")
    return violations


def check_m5_binds() -> tuple[bool, str]:
    """Prove the M5 property test BITES before trusting a pass from it.

    The reference monotone aggregator must produce no violations, AND the deliberately
    broken one must produce some. A test that cannot fail is not evidence.
    """
    good = m5_violations(monotone_aggregate)
    bad = m5_violations(NON_MONOTONE_AGGREGATE)
    if good:
        return False, f"reference monotone aggregator VIOLATES M5: {good[0]}"
    if not bad:
        return False, "M5 property test is VACUOUS — it did not catch the known non-monotone aggregator"
    return True, f"M5 test binds ({len(bad)} violations caught on the broken aggregator, 0 on the reference)"
