# Glossary term promotion (v0.1) — the governed draft→approved alignment pass

The vocab-currency loop ingests terms as `draft`; a draft term names something but does not yet
regulate state. It becomes `approved` — able to regulate governance — only through the 3-method
alignment from the GlossaryTerm contract, and only if all three hold as a **fail-closed meet**
(the same shape as DAR promotion = governance ∧ IP/legal):

1. **capture** — `alignment.ontologyClassRef` (bound to a formal ontology class)
2. **vector-align** — `alignment.vectorLink` (an NP↔VP link in the sovereign 768 space, pinned to
   `nomic-ai/nomic-embed-text-v1.5` / dim 768, and **reciprocated** by the named peer — a one-way
   link is not an alignment)
3. **implement** — `alignment.estateBinding` (bound to a real estate entity / service / action)

`tools/promote_glossary_term.py` recomputes the meet (never trusts a declared flag) and promotes
ONLY if all three hold; otherwise it **refuses** and names the unaligned method(s), leaving the
term `draft`. It never approves on a partial alignment — an approved-but-unaligned term is a
governance hole, exactly what the #250 drift-guard rejects. `validate-glossary-promotion`
(in `make validate`) proves the loop closes: the promoted output PASSES that same #250 guard, so
promotion is consistent-by-construction with the alignment contract; and missing / non-reciprocal /
off-space alignments are each refused.

This closes the vocabulary lifecycle: currency-detect → propose draft → ontogenesis-ingest →
**governed alignment promotion → approved** (regulates state).
