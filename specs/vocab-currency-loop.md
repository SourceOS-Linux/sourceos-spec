# Vocab-currency loop (v0.1) — a GovernedLoop, made LIVE

Vocabulary is the governance substrate: if the approved glossary doesn't name what the estate
actually does, we can't reason about the state of governance. That currency can't be a one-shot
DAG — the estate keeps moving — so it's a **loop**. And per the loops-vs-graphs doctrine a loop
is admissible only when **governed**. `tools/vocab_currency_loop.py` is that loop, made live and
governed BY a `GovernedLoop` contract (it reads bound + tolerance + `onNonConvergence` + admission
from the document and obeys them — the contract governs the runtime).

- **Fixed set (LSA side)** = the tokens named by *approved* `GlossaryTerm`s. A draft term does
  not regulate state, so it does not count as coverage.
- **Open set (LDA side)** = the corpus token distribution `Q` — what the estate actually discusses.
- **Divergence / currency signal** = uncovered probability mass `Σ Q(t)` over tokens the vocab
  doesn't name. This is the "LSI drive": the fixed set lags the current optimal vocab, and the gap
  is exactly the **new fields that became new vocab but aren't connected yet**.
- **Remediation step** = connect the highest-mass uncovered token (propose it as a new
  `GlossaryTerm`), which lowers `D` by exactly `Q(t)` — strictly monotone, so `monotone-decrease`
  convergence is real, not decorative.

**Governed / fail-closed:** the loop runs at most `bound.maxIterations` (never spins); if it can't
reach `tolerance` within the bound it applies `onNonConvergence` (**escalate-human**, exit non-zero)
rather than declaring the vocab current; and a loop with no `admission.superconsciousRef` is
**refused** (loops don't self-authorize). `make validate-vocab-currency-loop` asserts all three.

Next: feed the estate's real corpus + glossary, and route the emitted `candidateNewVocab` into
ontogenesis / the prophet-ontology as draft terms for the 3-method alignment pass.

## Remediation artifacts

Each connected token is emitted as a conformant status:`draft` `GlossaryTerm` in `result.proposedTerms` — the loop's output is directly ingestible by ontogenesis for the 3-method alignment pass. The loop only proposes: `partOfSpeech`, `alignment`, and approval are downstream. `make validate-vocab-currency-loop` refuses any proposed term that fails `GlossaryTerm.json` or that is not `draft` (the loop may not self-approve).

## Live dogfood (`make vocab-currency-dogfood`)

`tools/dogfood_vocab_currency.py` runs the governed loop over THIS repo's real vocabulary — every
approved `GlossaryTerm` in `examples/` (fixed/LSA) vs `specs/*.md` (open/LDA) — answering honestly
whether our own approved vocab is current with our own specs. On today's estate (2 approved terms
vs 14 specs) it is not: divergence starts ~0.98 and the governed loop, unable to reach currency in
its 8-iteration bound, **escalates-human** with concrete draft proposals rather than pretending
currency. It writes each proposed draft `GlossaryTerm` to `build/vocab-currency-proposals/<slug>.json`
— the exact artifacts ontogenesis ingests. Informational (exit 0), corpus-configured (Markdown
cleaned, generic prose words stoplisted so DOMAIN terms surface); the ENFORCEMENT stays in
`validate-vocab-currency-loop` on known-good fixtures.
