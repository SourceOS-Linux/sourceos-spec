# Data-Acquisition Governance Contract (v0.1)

Status: normative.

## What it governs

Every document, dataset, and collection a user uploads is **auto-catalogued** as a
`CatalogEntry` at the scope it was created in — `user`, `project`, or `chat` —
owned (`ownerRef`) by that user/project/chat and visible only in that owner's
catalogue view. **Only `platform` scope is estate-wide**, and reaching it is not
automatic: an object is promoted to `platform` **only** by an approved
`DataAcquisitionRequest` (DAR).

## The gate (fail closed)

A DAR's approval is the **meet** of two independent gates:

```
state == "approved"  ⇔  governanceReview.decision == "approved"
                         ∧  ipLegalReview.decision == "approved"
```

Either gate `pending` or `denied` ⇒ the request is **not** approved, and the
object stays at its origin scope. This is the estate's `Truth = Law × Evidence`
meet applied to acquisition: absence of a decision is `pending`, never approval.

The meet is enforced two ways:

- **Schema** — `DataAcquisitionRequest.json` carries an `allOf`/`if`-`then` that
  forbids `state: approved` unless both gate decisions are `approved`.
- **Validator** — `tools/validate_data_acquisition_examples.py` **recomputes**
  the meet from the two gate decisions and fails if `state` disagrees in *either*
  direction, so neither a rubber-stamp `approved` nor a single-gate approval
  survives.

## The binding invariant

A `CatalogEntry` at `scope: platform` **must** carry `promotion.state: promoted`
and a `promotion.darRef` that resolves to an **approved** DAR whose `subjectRef`
is that entry. A non-platform entry may not claim `promoted`. So no object is at
platform scope without an approved request behind it — verified across the
example set (`promotion binding`, `no orphan promotions`).

## Grains

| Schema | Role |
| --- | --- |
| `CatalogEntry` (extended) | the auto-catalogued index record + `scope` / `ownerRef` / `promotion` |
| `DataAcquisitionRequest` | the governed request to promote to platform, gated on governance ∧ IP/legal review |

The `CatalogEntry` additions are **optional** and backward-compatible. A legacy
index record that omits `scope` is **grandfathered**: it is treated as `platform`
for discovery, but the platform binding invariant is *not* applied retroactively —
the schema-level `allOf` fires **only when `scope: "platform"` is explicitly
declared**. New entries that opt into scoping and reach `platform` must carry
`promotion.state: promoted` + a `darRef`; legacy entries are not forced to migrate.

## Conformance

`make validate-data-acquisition-examples` (included in `make validate`).

## Intended reference implementation

`catalog-gateway` (prophet-platform): auto-catalogue on upload at owner scope,
serve the per-owner catalogue view, and expose DAR submit / review / decide
endpoints whose promotion path is gated on this contract.
