# Trained DataClass classifiers (v0.1) — specified → trained → registered → reproduced

The DataClass contract (#251) specifies a TF-Lattice classifier and references a `ModelManifest` +
train/eval `RunRecord` by URN. Those URNs pointed at nothing — the model was *specified, not
trained*. This closes that gap with real, verifiable artifacts.

`tools/train_dataclass_classifiers.py` trains, on a labelled fixture, **per-class LOGISTIC** heads
(one-vs-rest, individually testable per glossary-term) and a **per-table SOFTMAX** (the n-ary head),
a monotone-logistic **realisation** of the declared `tf-lattice-wide-and-deep` contract (a faithful monotonicity-satisfying model, not a full calibrated lattice), both **MONOTONE-constrained** in the declared `monotonicFeatures` — the TF-Lattice essence: the
weight on a monotone feature is projected `>= 0` each gradient step, so raising that feature never
lowers the class score. Deterministic (seeded, full-batch GD) so the weights — and thus the
`ModelManifest.modelDigest` — are reproducible. It emits the trained weights, a conformant
`ModelManifest` (id = the DataClass `modelRef`), and train + eval `RunRecord`s (ids = `runRef` /
`evalRunRef`), so the DataClass reference now RESOLVES.

`make validate-trained-classifiers` is recompute-don't-trust: the manifest digest must match the
weight bytes; the eval accuracy claimed in the RunRecord is **reproduced** from the weights + fixture
(an inflated claim fails); the model is verified genuinely **monotone** (perturb a monotone feature
up → score never drops); the DataClass refs resolve; and every emitted artifact is schema-conformant.
This is the fail-closed closure of the vocabulary/data-governance program's last owed thread.
