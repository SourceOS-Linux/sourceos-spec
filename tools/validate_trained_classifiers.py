#!/usr/bin/env python3
"""CI teeth for the TRAINED DataClass classifiers (task #14 close-out) — recompute, don't trust.

Proves the model is trained + registered + honest: the ModelManifest digest matches the actual
weights; the eval accuracy claimed in the RunRecord is REPRODUCED from the weights + fixture (a
tampered claim would be caught); the model is genuinely MONOTONE in the declared monotonicFeatures
(perturb up -> class score never drops); and the DataClass classifier's modelRef/runRef/evalRunRef
resolve to these artifacts, which are themselves schema-conformant.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import jsonschema
import numpy as np
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures" / "dataclass-training" / "labeled.json"
MODEL = ROOT / "models" / "dataclass-assigner" / "trained_model.json"
MANIFEST = ROOT / "examples" / "model-manifest.dataclass-assigner.json"
RUN_EVAL = ROOT / "examples" / "run.dataclass-eval.json"
RUN_TRAIN = ROOT / "examples" / "run.dataclass-train.json"
DATACLASS = ROOT / "examples" / "data_class.currency.json"

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def load(p):
    return json.loads(Path(p).read_text())


def _registry():
    res = []
    for f in (ROOT / "schemas").glob("*.json"):
        s = json.loads(f.read_text()); r = Resource.from_contents(s)
        res += [(s.get("$id", f.name), r), (f.name, r)]
    return Registry().with_resources(res)


def _features(rows, feats, mean, std):
    X = np.array([[r["features"][f] for f in feats] for r in rows], dtype=float)
    return (X - mean) / std


def main() -> int:
    spec = load(FIX); model = load(MODEL)
    feats = spec["features"]
    mean = np.array(model["standardize"]["mean"]); std = np.array(model["standardize"]["std"])
    rows = spec["rows"]
    cut = int(len(rows) * 0.8)
    test = rows[cut:]
    yte = np.array([0 if r["label"] == "revenue" else 1 for r in test])
    Xte = _features(test, feats, mean, std)

    # 1. digest: the manifest describes THIS model file (byte-exact).
    digest = "sha256:" + hashlib.sha256(MODEL.read_bytes()).hexdigest()
    if load(MANIFEST)["modelDigest"] != digest:
        FAILURES.append("ModelManifest.modelDigest does not match the trained_model.json bytes")
    else:
        CHECKS["digest:matches-weights"] = True

    # 2. reproduce the softmax eval accuracy from the weights (recompute, don't trust the claim).
    W = np.array(model["tableSoftmax"]["weights"]); b = np.array(model["tableSoftmax"]["bias"])
    recomputed = float((( Xte @ W + b).argmax(axis=1) == yte).mean())
    claimed = load(RUN_EVAL)["workload"]["params"]["value"]
    # Compare at the stored precision (claims are recorded rounded to 4 decimals); a real
    # discrepancy is >> this, an inflated claim (+0.1) is far outside it.
    if round(recomputed, 4) != round(claimed, 4):
        FAILURES.append(f"eval accuracy not reproduced: recomputed {recomputed} != claimed {claimed}")
    else:
        CHECKS["eval:reproduced-from-weights"] = True
    # teeth on the teeth: an inflated claim must NOT reproduce (guards against trusting the number)
    if round(recomputed, 4) == round(claimed + 0.1, 4):
        FAILURES.append("reproduction check is not discriminating (would accept an inflated claim)")
    else:
        CHECKS["eval:inflated-claim-would-fail"] = True

    # 3. per-class logistic accuracy reproduced too (individually testable per class).
    ok_pc = True
    for ci, name in enumerate(["revenue", "cost"]):
        pc = model["perClassLogistic"][name]
        w = np.array(pc["weights"]); bb = pc["bias"]
        acc = float((((1 / (1 + np.exp(-(Xte @ w + bb)))) >= 0.5) == (yte == ci)).mean())
        if round(acc, 4) != round(pc["evalAccuracy"], 4):
            FAILURES.append(f"per-class '{name}' accuracy not reproduced ({acc} != {pc['evalAccuracy']})")
            ok_pc = False
    if ok_pc:
        CHECKS["per-class:reproduced"] = True

    # 4. MONOTONE in the declared features, for EVERY per-class head: raise each monotone feature ->
    #    the class logit never drops. Checked on both revenue and cost heads (not just one).
    mono = spec["monotonicFeatures"]
    mono_ok = True
    for name in ("revenue", "cost"):
        w = np.array(model["perClassLogistic"][name]["weights"]); bb = model["perClassLogistic"][name]["bias"]
        base = Xte @ w + bb
        for f in mono:
            bumped = [dict(r, features={**r["features"], f: r["features"][f] + 1.0}) for r in test]
            if np.any((_features(bumped, feats, mean, std) @ w + bb) < base - 1e-9):
                FAILURES.append(f"'{name}' head NOT monotone in '{f}' — raising it lowered the score")
                mono_ok = False
    if mono_ok:
        CHECKS["monotone:constraint-holds"] = True

    # 4b. The monotone constraint must actually BIND — at least one monotone feature carries a
    #     non-trivial positive weight on the revenue head — otherwise the monotone check is vacuous
    #     (a constant/ignored feature would pass trivially). Guards against a toothless fixture.
    wr = np.array(model["perClassLogistic"]["revenue"]["weights"])
    mono_w = [wr[feats.index(f)] for f in mono]
    if max(mono_w) < 0.1:
        FAILURES.append(f"monotone constraint does not bind — all monotone weights ~0 {mono_w} (vacuous)")
    else:
        CHECKS["monotone:constraint-binds"] = True

    # 5. DataClass classifier refs resolve to the emitted artifacts.
    clf = load(DATACLASS)["classifier"]
    ids = {load(MANIFEST)["id"], load(RUN_TRAIN)["id"], load(RUN_EVAL)["id"]}
    if {clf["modelRef"], clf["runRef"], clf["evalRunRef"]} <= ids:
        CHECKS["refs:resolve"] = True
    else:
        FAILURES.append("DataClass classifier modelRef/runRef/evalRunRef do not resolve to emitted artifacts")

    # 6. emitted artifacts are schema-conformant.
    REG = _registry()
    conform = True
    for schema, ex in (("ModelManifest", MANIFEST), ("RunRecord", RUN_TRAIN), ("RunRecord", RUN_EVAL)):
        errs = sorted(jsonschema.Draft202012Validator(load(ROOT / "schemas" / f"{schema}.json"), registry=REG).iter_errors(load(ex)), key=str)
        if errs:
            FAILURES.append(f"{ex.name}: {errs[0].message}")
            conform = False
    if conform:
        CHECKS["artifacts:schema-conform"] = True

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS, "reproducedAccuracy": recomputed}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
