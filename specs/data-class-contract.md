# DataClass Contract (v0.1) — OntoDT / OntoDQ, the data side of governance

The business vocabulary (`GlossaryTerm`) says what a thing MEANS; the `DataClass` says what
its DATA is, ontologically — so data quality can be inferred and enforced, not asserted.

A `DataClass` binds four things and is fail-closed if any is missing:
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
