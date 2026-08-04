# Multiverseal Twin — reference implementation (WS-C)

Executable substrate for `schemas/{MultiversealTwin,TwinAttestation,InterferometricDiff}.json`
(ADR-0014), Epoch E13 / WS-C. Instantiated on **FHRR** (Fourier Holographic Reduced
Representations): the twin space is `V = C^D` of unit-modulus phasors, so *phase = provenance*
is literal.

```
bind(o, r)   = o ⊙ r          record object against reference (reference-at-ingest)
bundle(ts)   = Σ t_k          superpose into the opaque twin medium H
unbind(H, r) = H ⊙ conj(r)    reconstruct — requires the reference
```

## Run the self-test

```bash
python3 test_mvtwin.py
```

It proves, with measured numbers, the four load-bearing properties:

| Property | Measured (D=8192, N=8) |
|---|---|
| **Reference-gating** — authored reference reconstructs; un-authored/absent = noise | recover **0.348** vs wrong-ref **0.003**, opaque **−0.009** (~100× SNR) |
| **ε-unlinkability** — distinct context references are near-orthogonal | cross-context leakage **L=0.004** |
| **Fringe is the leading indicator** — a small drift barely moves the score but shows in the fringe | score move **0.00016** vs mean\|fringe\| **0.020** (~125×) |
| **Holographic tamper-evidence** — one local write perturbs the fringe globally | **100%** of spectrum perturbed |

## Scope

This is the **linear substrate only**. Reference-at-ingest, the ε-budget, VRF mint/verify,
and the impersonation wall are enforced at the contract/policy layer (ADR-0014); Sybil-
resistance and nonlinear trust weighting live in a **separate** layer that must not leak back
into this medium (twin spec §H / WS-F). Next increments: wire `bind` to a real VRF reference;
QEC `[[n,k,d]]` sharing; the `InterferometricDiff` replay (Fresnel forward-propagation).
