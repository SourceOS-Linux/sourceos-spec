# KnowledgeNugget Contract v0.1 — the estate's L2 content grain

Status: v0.1.0 (normative for `schemas/KnowledgeNugget.json`)
Provenance: the production IFM warrant-typed extraction (document → typed
values), generalized into a universal content-grain contract.
Validation: `make validate-knowledge-nugget-examples`
(tools/validate_knowledge_nugget_examples.py).

## 1. Scope

A `KnowledgeNugget` is one warrant-typed fragment of knowledge lifted from a
governed source. It is the L2 content grain: the smallest unit that retrieval,
ranking, planning, and rendering surfaces exchange. Every nugget answers three
questions, all machine-checkable:

- **WHERE** — `sourceRef`: source document URN + character span + the
  `sha256-<64hex>` content hash of the source state the span was read from, so
  offsets can never silently drift.
- **HOW** — `warrant`: one of `direct-quote | computed | inferred |
  model-generated`, plus evidence refs and producer confidence.
- **WHAT** — `text`, optional `canonicalPayload` (normalized machine form),
  and optional `kkoTypeRefs` (ontology concept URIs for typed retrieval and
  planner binding — the same URI vocabulary `SemanticAction` types its slots
  with).

## 2. Warrant taxonomy and admissibility (normative)

The four-kind warrant taxonomy is closed at v0.1 (enum-enforced); widening it
is a minor contract bump.

1. `direct-quote` — text IS the exact source span; warranted by `sourceRef`
   itself. Exactness is executable: `span.end - span.start` must equal the
   length of `text` (validator-enforced across examples).
2. `computed` — derived by deterministic computation over cited source values.
   Must cite at least one evidence ref (schema-enforced via `if/then`): a
   derivation with no cited inputs is not a derivation.
3. `inferred` — follows by stated inference from cited premises. Same
   evidence-grounding rule as `computed`.
4. `model-generated` — produced by a model conditioned on the source window;
   NOT warranted by it. May be evidence-free — which is exactly why it is
   discounted.

**Design rule (normative): `warrant.type = model-generated` MUST remain
visibly distinguishable on every downstream surface.** Retrieval, ranking,
rendering, and admissibility weighting all discount model-generated nuggets
relative to source-warranted ones, and no downstream transform may launder a
model-generated nugget into a source-warranted one. Admissibility is a
function of warrant type first and stated confidence second — a
model-generated nugget at confidence 0.99 still ranks below a direct quote.
The example set must always exercise both poles of this contrast
(validator-enforced).

`sourceRef` is required for every warrant type: even a model-generated nugget
must pin the source window it was conditioned on. The span then records the
conditioning window, not a warrant.

## 3. One time vocabulary, not two

`wallTime` and `logicalTime` are carried **verbatim** from the MPCC
`ConversationEvent` envelope, with deep-equality parity enforced by
`tools/validate_knowledge_nugget_examples.py` — the same discipline the MPCC
trading profiles use. A nugget is not an event, but its creation instant lives
on the same clocks as the conversation fabric that produced it, so nuggets and
events order consistently in provenance chains.

## 4. Overlap decisions (spec-first conformance)

| Existing contract | Decision |
|-------------------|----------|
| `ConversationEvent` | A nugget is content, not a communicative act. Extraction runs may emit events whose `provenanceLinks` reference nuggets; the nugget's `provenance` links back. No envelope duplication beyond the parity-enforced time vocabulary. |
| `ProvenanceRecord` | Not duplicated. `provenance` carries typed `{rel, ref}` chain links (same link shape as the MPCC `provenanceLinks`); a full W3C PROV chain lives in `ProvenanceRecord` and is referenced, not embedded. |
| `MemoryEntry` | Agent memory (`rule`/`learned`/`recap`) stays there. Nuggets are source-warranted content grains; a memory may cite nuggets as evidence. |
| `GlossaryTerm` | Definitions of terms stay there. Nuggets carry content about the world, typed by `kkoTypeRefs`. |
| `ContentRef` | Digest-based blob addressing stays there. `sourceRef.contentHash` pins the hashed source text state; a `ContentRef` may be what `docRef` resolves through. |
| `ReasoningAssay` | Claim verdicts stay there. `warrant.evidence` may cite assays/reasoning events as grounding for `inferred` nuggets. |

## 5. Versioning

The family versions as one contract, pinned by the `specVersion` const
`0.1.0`. Additive optional fields or widened enums bump the minor; anything
that can invalidate an existing document bumps the major, with CHANGELOG + ADR
per CONTRIBUTING.md.

## 6. Known gaps (deliberate, v0.1)

- No OpenAPI/AsyncAPI operations or semantic-context mappings yet (matches how
  recent contract families landed; wiring follows once names have settled).
- `docRef` is a generic `urn:srcos:` URN pending a dedicated document-identity
  contract; `warrant.evidence` entries are free-form stable references
  (URNs recommended, run/step-scoped references permitted).
- Span offsets are character-based over the hashed source text; a
  byte-offset/encoding profile for binary sources is future work.
- Supersession (`provenance` rel `supersedes`) is a convention at v0.1, not
  yet a typed lifecycle.
