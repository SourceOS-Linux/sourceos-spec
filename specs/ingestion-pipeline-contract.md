# Ingestion-Pipeline Contract (v0.1)

Status: normative · Contract version pinned at `specVersion: "0.1.0"` per the
policy-integrity tranche-0001 discipline.

## Why this family exists

The estate's document ingestion / retrieval pipeline — parse a source, chunk it,
embed each chunk, store the vectors, retrieve by cosine — lived in exactly one
place: `Noetica/agent-machine/lib/doc-store.ts` (`extractText` →
`chunkTextWithSpans` → `embedText` (an ollama `nomic-embed-text` client) →
`hgPutChunk`). Meanwhile `prophet-platform` already ran a first-party sovereign
embedding service, `apps/embeddings` (FastAPI serving
`nomic-ai/nomic-embed-text-v1.5` over an OpenAI-compatible `/v1/embeddings`), and
its own document parsers in `compute-gateway`. Two embedders, two parser sets,
**no guarantee the vectors were even in the same space** — the same
platform-services-not-Noetica-only failure mode already fixed once for other
capabilities.

This contract does not move the code. It defines the *seam* the code must meet,
so the pipeline stops being Noetica-private and — the reason the family exists —
so two producers can never write into two silently-incomparable vector spaces.

## The grains

| Schema | Generalizes (Noetica) | The grain |
| --- | --- | --- |
| `IngestedDocument` | `extractText` / `extractTextWithPages` | one source parsed to a single canonical plaintext offset space |
| `Chunk` | `chunkTextWithSpans` / `hgPutChunk` | a span of one document's text, with an optional embedding |
| `ExtractedEntity` | `linkDocGrounds` | an entity mention grounded at exact document spans |
| `EmbeddingRequest` | `embedText` ↔ `apps/embeddings` `/v1/embeddings` | the one embedding-call shape for the whole estate |

## Normative invariants

Beyond the strictness bar (top-level `additionalProperties: false`, `specVersion`
const, anchored `urn:srcos:` id, `type` const = title), the contract is only as
strong as the checks that recompute it. `tools/validate_ingestion_pipeline_examples.py`
enforces:

1. **Document integrity.** `IngestedDocument.extractionDigest` is the sha256 of
   the document's own `text`, **recomputed**, never read back. The text is the
   shared coordinate system every span indexes into.

2. **Span soundness — a chunk cannot misquote its source.** Every `Chunk`
   resolves to a real `IngestedDocument`; its span is in-bounds
   (`0 <= start < end <= len(text)`); **`documentText[start:end]` equals the
   chunk's own `text`**; and `contentHash` is the sha256 of that text. A chunk
   that survives all four is a faithful, content-addressed quotation of the
   document it cites.

3. **Shared vector space — the invariant this family exists for.**
   `EmbeddingRequest` pins the sovereign `model`
   (`nomic-ai/nomic-embed-text-v1.5`) and `dimension` (`768`) **by `const`** —
   not a free string a caller may vary. Every embedded `Chunk` must name that
   same model, that same dimension, and carry a vector of exactly that length. A
   request for any other model, or a Matryoshka-truncated dimension, fails
   validation *by construction*; a chunk embedded in a different space is refused
   here rather than compared silently downstream. This is what makes the Noetica
   embedder and the `apps/embeddings` service one space instead of two.

4. **Grounding soundness.** Every `ExtractedEntity` resolves to a real document
   and each mention span selects the entity's `surface` form out of the document
   text — a claimed grounding always points at real evidence (the ingestion
   analog of the `KnowledgeNugget` derivation-grounding invariant).

Negative conformance vectors (`fixtures/ingestion-pipeline/conformance.json`)
pin the reject side, including the two that give the family its teeth: a request
for a non-sovereign model, and a truncated dimension, must both fail.

## Conformance

`make validate-ingestion-pipeline-examples` (included in `make validate`).

## Intended reference implementations

- Producer: `Noetica/agent-machine/lib/doc-store.ts`, rewired to call the shared
  `apps/embeddings` service through the `EmbeddingRequest` shape instead of its
  own ollama client (a later PR — this is the contract that makes that safe).
- Service: `prophet-platform/apps/embeddings`, which already serves exactly this
  model and dimension.

Read-only shapes at v0.1: this family describes what a governed ingestion
produces, not how retrieval ranks it.
