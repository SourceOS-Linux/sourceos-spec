# Learned spell-correction + user dictionary (v0.1) — from context, not dictionary matching

A static wordlist flags every domain term (`epistemiclevel`, `srcos`, `governedloop`) as a
misspelling and corrects it away — the estate's own vocabulary treated as errors. So what counts as
a "correct" word must be LEARNED from context, not matched against a list. For each UNKNOWN token
`tools/learned_dictionary.py` decides from a skip-gram word-sense predictor:

- **learn** (add to the user dictionary) — the token RECURS with a COHERENT context (its context
  windows cluster into one stable word-sense); a real term the dictionary simply hadn't seen.
- **correct** (to a known word) — the token is RARE and both spelling-near (small edit distance)
  AND sense-near (high skip-gram cosine) to a known word. **Sense — not edit distance alone —
  picks the target**, so a token spelled near a known word but used in a different sense is not
  auto-corrected.
- **unknown** — neither coherent enough to learn nor sense-close to a known word: left for a human.

The predictor is a count-based skip-gram — PPMI over a co-occurrence window + truncated SVD
(Levy-Goldberg: SGNS factorises shifted PPMI, so this is the same word-sense family). No wordlist
decides correctness; context does. **Fail-closed:** every decision is a PROPOSAL (add / correct-to),
never a silent rewrite — a human or the superconscious admits it.

`make validate-learned-dictionary` proves it: a novel domain term (`epistemiclevel`) is learned, a
typo (`reciept`) is corrected to `receipt` by sense, garbage (`qwzptl`) is left unknown, and a
learned term is never auto-corrected away. Same doctrine as the stopword analysis and glossary
currency: replace static membership tests with learned, context-driven predictors.
