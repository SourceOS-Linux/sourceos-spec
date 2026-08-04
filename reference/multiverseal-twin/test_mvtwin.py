"""Self-test proving the twin substrate's load-bearing properties (WS-C).

Run: python3 test_mvtwin.py   (asserts + prints the measured numbers)
"""
from __future__ import annotations
import numpy as np
import mvtwin as mv


def build_twin(D, N, rng):
    objs = [mv.obj(D, rng) for _ in range(N)]
    refs = [mv.reference(D, rng) for _ in range(N)]
    ts = [mv.bind(o, r) for o, r in zip(objs, refs)]
    return objs, refs, ts, mv.bundle(ts)


def main() -> int:
    D, N = 8192, 8
    rng = np.random.default_rng(0)
    objs, refs, ts, H = build_twin(D, N, rng)

    # 1) Recovery: unbind with the right reference recovers the object, far above baseline.
    rec = mv.similarity(mv.unbind(H, refs[0]), objs[0])
    wrong = mv.similarity(mv.unbind(H, mv.reference(D, rng)), objs[0])   # un-authored angle
    opaque = mv.similarity(H, objs[0])                                    # no reference at all
    print(f"[1] recover={rec:.3f}  wrong-ref={wrong:.3f}  opaque(no-ref)={opaque:.3f}")
    assert rec > 0.20, "authored reference must reconstruct"
    assert abs(wrong) < 0.05 and abs(opaque) < 0.05, "opaque/un-authored angles must be noise"
    assert rec > 10 * max(abs(wrong), abs(opaque)), "recovery must dominate noise"

    # 2) ε-unlinkability: two VRF-style references are near-orthogonal (small leakage).
    leak = mv.unlinkability_leakage(refs[0], refs[1])
    print(f"[2] cross-context leakage L={leak:.4f}  (ε-unlinkable for ε≳{leak:.3f})")
    assert leak < 0.05, "distinct context references must be near-orthogonal"

    # 3) Interferometric diff is a LEADING indicator: a small phase drift on ONE attestation
    #    barely moves the scalar score, but shows clearly in the fringe.
    delta = 0.05  # radians
    ts2 = list(ts); ts2[0] = ts[0] * np.exp(1j * delta)
    H_live = mv.bundle(ts2)
    score_move = 1.0 - mv.similarity(H_live, H)
    fringe = mv.interferometric_diff(H_live, H)
    fringe_signal = float(np.mean(np.abs(fringe)))
    print(f"[3] scalar-score move={score_move:.5f}   mean|fringe|={fringe_signal:.5f}")
    assert score_move < 0.02, "scalar score should barely move (lagging)"
    assert fringe_signal > 5 * score_move, "fringe must lead the scalar score"

    # 4) Holographic tamper-evidence: a LOCAL write (one time-domain sample) perturbs the
    #    fringe GLOBALLY across the spectrum — tamper detectable without knowing what changed.
    H_time = np.fft.ifft(H)
    H_time[123] += 0.5 + 0.5j          # single local unauthorized write
    H_tampered = np.fft.fft(H_time)
    tamper_fringe = np.abs(mv.interferometric_diff(H_tampered, H))
    frac_global = float(np.mean(tamper_fringe > 1e-6))
    print(f"[4] fraction of spectrum perturbed by ONE local write={frac_global:.3f}")
    assert frac_global > 0.9, "a local write must perturb the fringe globally (holographic)"

    print("\nALL PROPERTIES HOLD — reference-gating, ε-unlinkability, fringe-as-leading-indicator, holographic tamper-evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
