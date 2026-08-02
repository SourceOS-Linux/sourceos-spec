# DataClass Contract (v0.1) — OntoDT / OntoDQ, the data side of governance

The business vocabulary (`GlossaryTerm`) says what a thing MEANS; the `DataClass` says what
its DATA is, ontologically — so data quality can be inferred and enforced, not asserted.

A `DataClass` binds three things and is fail-closed if any is missing, plus an optional fourth (assignment):
- **OntoDT** — `ontologyClassRef`: the datatype-ontology class (capture; enables reusable,
  inferable data-quality logic — IBM OntoDT).
- **biz↔data** — `glossaryTermRef`: the business `GlossaryTerm` this data class realizes.
- **domain** — `domain` ($ref `ValidValues`): enumeration / range / regex (valid values,
  bounds, pattern), the same constraint an `EntityField` carries.
- **assignment** (optional) — a **TF-Lattice wide-and-deep** `classifier` that assigns this
  class by inference (OntoDQ). It is a first-class **cataloged model**: `modelRef` →
  `ModelManifest`, `runRef` → `RunRecord`, `compute.platform` ∈ {ray, tritfabric} with an
  asset/service ref, `monotonicFeatures` for the lattice shape constraint, and `labels` that
  are **`GlossaryTerm` URNs** (labels are assigned in the glossary).

`EntityField` gains an optional `dataClassRef`. The validator enforces field↔class conformance:
a field bound to a DataClass must share its `domain.kind` — a field cannot claim a class it
does not fit.

## Conformance
`make validate-data-class-examples` (in `make validate`).

## Two-level classifier architecture

Assignment is tested at two granularities, so each class is verifiable on its own and the
table is verifiable as a whole:

- **Per-class — LOGISTIC** (`DataClass.classifier`, `head: logistic`): a one-vs-rest binary
  classifier per class / glossary term, with a required `evalRunRef` — the **individual test**
  for that class (per-class precision/recall). A class with no eval run is untestable and refused.
- **Per-table — SOFTMAX** (`TableClassifier`, `head: softmax`): the n-ary multinomial that
  assigns each column to one of N `DataClass`es. It must **align two representations** of each
  column — an **LSA bag-of-words** embedding (the closed fixed vocabulary) and a **doc2vec
  sentence-encoder** (contextual) — because these are the n-ary examples of the logit→class
  assignment. A cataloged model (`ModelManifest`) with a run on Ray/TritFabric.
