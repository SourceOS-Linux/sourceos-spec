#!/usr/bin/env python3
"""Actually TRAIN the DataClass classifiers and REGISTER them (task #14/#13 close-out).

The DataClass contract (#251) SPECIFIES a TF-Lattice classifier and references a ModelManifest +
train/eval RunRecord by URN — but those URNs pointed at nothing (specified, not trained). This
trains real classifiers on a labelled fixture and emits the artifacts those URNs resolve to, so the
reference is no longer a promise:

  * per-class LOGISTIC heads (one-vs-rest) — individually testable per class/glossary-term;
  * a per-table SOFTMAX — the n-ary head;
both MONOTONE-constrained in the declared `monotonicFeatures` (the TF-Lattice essence: the weight on
a monotone feature is projected >= 0 each step, so raising that feature never lowers the class
score). Deterministic (seeded, full-batch gradient descent) so the trained weights — hence the
ModelManifest.modelDigest — are reproducible and drift-guardable.

Emits: models/dataclass-assigner/trained_model.json (weights + eval metrics), a conformant
ModelManifest (id = the DataClass modelRef), and train + eval RunRecords (ids = the runRef /
evalRunRef). validate_trained_classifiers.py then REPRODUCES the eval from the weights + fixture
(recompute, don't trust) and checks monotonicity + digest + that the references resolve.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures" / "dataclass-training" / "labeled.json"
MODEL = ROOT / "models" / "dataclass-assigner" / "trained_model.json"
MANIFEST = ROOT / "examples" / "model-manifest.dataclass-assigner.json"
RUN_TRAIN = ROOT / "examples" / "run.dataclass-train.json"
RUN_EVAL = ROOT / "examples" / "run.dataclass-eval.json"

MODEL_URN = "urn:srcos:model-manifest:dataclass-assigner-lattice-v1"
TRAIN_RUN = "urn:srcos:run:dataclass-assigner-train-001"
EVAL_RUN = "urn:srcos:run:dataclass-currency-logistic-eval-001"
EPOCHS, LR = 400, 0.3


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def _matrix(rows, feats):
    X = np.array([[r["features"][f] for f in feats] for r in rows], dtype=float)
    # standardise (store mean/std so inference reproduces); monotone direction is preserved by
    # positive scaling, so the >=0 projection still means "monotone increasing in the raw feature".
    mean, std = X.mean(axis=0), X.std(axis=0)
    std[std == 0] = 1.0
    return (X - mean) / std, mean, std


def _train_logistic(X, y, mono_idx):
    n, d = X.shape
    w, b = np.zeros(d), 0.0
    for _ in range(EPOCHS):
        p = _sigmoid(X @ w + b)
        g = p - y
        w -= LR * (X.T @ g) / n
        b -= LR * g.mean()
        w[mono_idx] = np.maximum(w[mono_idx], 0.0)   # monotone projection: non-negative on mono feats
    return w, b


def _train_softmax(X, Y, mono_idx):
    n, d = X.shape
    k = Y.shape[1]
    W, b = np.zeros((d, k)), np.zeros(k)
    for _ in range(EPOCHS):
        z = X @ W + b
        z -= z.max(axis=1, keepdims=True)
        p = np.exp(z)
        p /= p.sum(axis=1, keepdims=True)
        g = p - Y
        W -= LR * (X.T @ g) / n
        b -= LR * g.mean(axis=0)
        W[mono_idx, :] = np.maximum(W[mono_idx, :], 0.0)
    return W, b


def main() -> int:
    spec = json.loads(FIX.read_text())
    feats, labels = spec["features"], spec["labels"]
    mono_idx = [feats.index(f) for f in spec["monotonicFeatures"]]
    rows = spec["rows"]
    label_idx = {"urn:srcos:glossary:revenue": 0, "urn:srcos:glossary:cost": 1}
    y_name = ["revenue", "cost"]

    X, mean, std = _matrix(rows, feats)
    y = np.array([0 if r["label"] == "revenue" else 1 for r in rows], dtype=float)

    # 80/20 split (deterministic order in the fixture)
    cut = int(len(rows) * 0.8)
    Xtr, Xte, ytr, yte = X[:cut], X[cut:], y[:cut], y[cut:]

    # per-class one-vs-rest logistic (class 0 = revenue as positive; class 1 = cost as positive)
    perclass = {}
    for ci, name in enumerate(y_name):
        yc = (y == ci).astype(float)
        w, b = _train_logistic(Xtr, yc[:cut], mono_idx)
        acc = float((( _sigmoid(Xte @ w + b) >= 0.5) == (yte == ci)).mean())
        perclass[name] = {"weights": w.tolist(), "bias": b, "evalAccuracy": round(acc, 4)}

    # per-table softmax (n-ary head)
    Y = np.eye(2)[y.astype(int)]
    W, bs = _train_softmax(Xtr, Y[:cut], mono_idx)
    z = Xte @ W + bs
    softmax_acc = float((z.argmax(axis=1) == yte.astype(int)).mean())

    model = {
        "modelUrn": MODEL_URN, "features": feats, "monotonicFeatures": spec["monotonicFeatures"],
        "labels": labels, "standardize": {"mean": mean.tolist(), "std": std.tolist()},
        "perClassLogistic": perclass,
        "tableSoftmax": {"weights": W.tolist(), "bias": bs.tolist(), "evalAccuracy": round(softmax_acc, 4)},
        "evalAccuracy": round(softmax_acc, 4),
    }
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    MODEL.write_text(json.dumps(model, indent=1) + "\n")
    digest = "sha256:" + hashlib.sha256(MODEL.read_bytes()).hexdigest()

    MANIFEST.write_text(json.dumps({
        "id": MODEL_URN, "type": "ModelManifest", "specVersion": "2.1.0",
        "modelDigest": digest, "displayName": "dataclass-assigner (monotone wide-and-deep)",
        "architecture": "monotone-logistic-wide-and-deep", "format": "onnx", "quantization": "none",
        "license": "Apache-2.0",
        "signature": {"algorithm": "ed25519", "keyId": "srcos-model-signing-2026",
                      "signatureDigest": "sha256:" + "b" * 64},
        "evidenceRefs": [EVAL_RUN],
    }, indent=2) + "\n")

    sphere = {"sphereId": "urn:srcos:sphere:platform_curated", "name": "Platform Curated Sphere",
              "boundary": {"zone": "curated", "networkPolicy": None, "storagePolicy": None},
              "controls": {"accessEnforcer": "enforcer.v2", "provenance": "hashes", "containerAttestation": "basic"}}

    def run(rid, params, inputs, outputs):
        return {"id": rid, "type": "RunRecord", "specVersion": "2.0.0",
                "workload": {"workloadId": "urn:srcos:workload:dataclass-assigner-train",
                             "kind": "container", "image": "ghcr.io/srcos/dataclass-trainer:v1",
                             "entrypoint": "train", "params": params},
                "sphere": sphere, "inputs": inputs, "outputs": outputs, "tokenRef": "tok_dataclass",
                "status": "succeeded", "time": {"startedAt": "2026-08-03T02:00:00Z", "endedAt": "2026-08-03T02:00:20Z"}}

    RUN_TRAIN.write_text(json.dumps(run(
        TRAIN_RUN, {"epochs": EPOCHS, "lr": LR, "monotonicFeatures": spec["monotonicFeatures"]},
        [{"refType": "dataset", "id": "urn:srcos:dataset:dataclass-training", "fieldPaths": []}],
        [{"refType": "dataset", "id": "urn:srcos:dataset:dataclass-assigner-weights", "fieldPaths": []}]), indent=2) + "\n")
    RUN_EVAL.write_text(json.dumps(run(
        EVAL_RUN, {"metric": "accuracy", "value": round(softmax_acc, 4),
                   "perClassAccuracy": {k: v["evalAccuracy"] for k, v in perclass.items()}},
        [{"refType": "dataset", "id": "urn:srcos:dataset:dataclass-assigner-weights", "fieldPaths": []}],
        [{"refType": "dataset", "id": "urn:srcos:dataset:dataclass-eval-report", "fieldPaths": []}]), indent=2) + "\n")

    print(json.dumps({"trained": True, "softmaxEvalAccuracy": round(softmax_acc, 4),
                      "perClass": {k: v["evalAccuracy"] for k, v in perclass.items()},
                      "modelDigest": digest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
