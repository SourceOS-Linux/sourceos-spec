# ADR: Evidence Fabric Boundaries and Contract Ownership (v0.1)

## Status

Proposed.

## Context

`sourceos-spec` already defines the umbrella metadata-plane and governance vocabulary for SourceOS/SociOS. Existing first-class semantic concepts include dataset, field, policy, workflow specification, run record, agreement, glossary terms, and related contract families.

At the same time, the broader platform now needs a distinct evidence fabric for ingesting and preserving large mixed-format corpora from local disks and external drives such as Google Drive and iCloud Drive.

Without an explicit boundary, the following risks emerge:

- the metadata plane absorbs operational evidence-custody contracts and becomes muddled,
- the evidence plane redefines governance and provenance concepts that should remain canonical at the SourceOS metadata-plane level,
- desktop integration, storage, and runtime broker work blur together.

This ADR freezes the boundary.

## Decision

### 1. `sourceos-spec` remains the umbrella metadata-plane contract layer

`sourceos-spec` SHALL continue to own:

- top-level semantic context and JSON-LD/Hydra overlays,
- generic governance and policy vocabulary,
- provenance and agreement families,
- workflow and run-record umbrella semantics,
- connector/asset/schema families at the metadata-plane level.

It SHALL NOT become the direct implementation home for the operational evidence-plane runtime contracts.

### 2. The evidence fabric becomes a distinct operational contract family

A separate evidence-plane contract family SHALL be implemented in a dedicated SocioProphet repo family.

The initial evidence-plane object families are expected to include:

- `ConnectorProfile`
- `AcquisitionRun`
- `EvidenceBlob`
- `EvidenceItem`
- `EvidenceEntity`
- `EvidenceEvent`
- `ParserRun`
- `ValidationResult`

These names are intentionally distinct from existing `sourceos-spec` umbrella names such as `RunRecord`.

### 3. Reserved boundaries

The following semantic names remain reserved to the existing umbrella or adjacent systems and SHOULD NOT be reused as canonical evidence-plane runtime object names:

- `Dataset`
- `Field`
- `Policy`
- `WorkflowSpec`
- `RunRecord`
- `Agreement`
- `GlossaryTerm`

Likewise, traversal-native names owned by the CairnPath family SHOULD NOT be reused for evidence runtime objects:

- `Context`
- `Step`
- `Line`
- `Result`
- `Materialize`

### 4. `kind` not `type` for operational evidence contracts

Operational evidence-plane contracts SHOULD use `kind` as their runtime discriminator rather than `type`.

Rationale:

- `type` is already semantically overloaded in JSON-LD style overlays and metadata-plane contexts,
- `kind` avoids ambiguity between runtime contract discrimination and semantic linked-data typing.

### 5. Repo ownership split

#### SourceOS-Linux

SourceOS-Linux SHALL own umbrella metadata-plane, governance, and semantic overlay contracts.

#### SocioProphet

SocioProphet SHALL own the operational evidence-plane implementation repos, including the planned families:

- `evidence-contracts`
- `evidence-broker`
- `evidence-connectors-gdrive`
- `evidence-connectors-icloud`
- `evidence-validator`
- `evidence-storage-infra`

#### SociOS-Linux

SociOS-Linux SHALL own desktop-facing account UX, mounted filesystem surfaces, operator-facing file access, and local capture pathways.

## Consequences

### Positive

- the metadata plane remains clean and composable,
- the evidence plane can move quickly without redefining SourceOS governance primitives,
- connector/runtime/storage work can be implemented in SocioProphet without polluting the semantic overlay layer,
- desktop and operator surfaces remain free to evolve in SociOS-Linux.

### Negative

- cross-repo coordination is mandatory,
- some provenance and connector concepts will need explicit mapping between `sourceos-spec` and the evidence-plane contract set,
- implementation cannot rely on a single monorepo or one oversized schema package.

## Required interoperability rule

All evidence-plane repos SHALL align upward to `sourceos-spec` for umbrella governance and provenance semantics, but SHALL keep their runtime object names and schemas in the dedicated evidence-plane contract family.

In short:

**`sourceos-spec` defines the umbrella metadata plane; the evidence fabric implements custody and normalization beneath it.**
