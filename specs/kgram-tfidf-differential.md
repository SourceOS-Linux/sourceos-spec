# k-gram TF-IDF / LSA differential (v0.1) — confirm stopword candidates by compositional scale

The stopword deviation analysis flags a dropped word as a term-candidate when it is concentrated in
a domain AND recurs in repeated bigram collocations. That is the **bigram floor**. This is the
confirmation: it measures the candidate's domain-specificity across n-gram **orders 3..7** and takes
the **differential**.

Per order `n`, over the domain corpora:
1. build the n-gram × domain count matrix (n-grams over RAW tokens, so a stopword that is part of a
   real phrase — "held to maturity", "empty set of states" — is captured);
2. weight it **TF-IDF** (documents = domains): a phrase frequent in ONE domain and rare across the
   rest scores high — it is domain-specific;
3. take the **LSA** (truncated SVD): the top singular component is the dominant axis of cross-domain
   variation, and a domain-specific n-gram loads heavily on it.

A candidate's per-order signal is the strongest domain-specific TF-IDF among the n-grams containing
it, **discounted by its intrinsic unigram specificity** — a stopword embedded in a domain phrase
("the state machine") would otherwise borrow the phrase's specificity; the discount strips that so
only intrinsically domain-specific words persist.

**The differential across 3..7 is the discriminator:**
- a **true domain term PERSISTS** — it keeps heading domain-specific n-grams as `n` grows, so its
  signal stays high across orders → **confirmed-term** (the strongest un-stoplist proposal);
- a **stylistic / noise word DECAYS or is discounted** — its longer n-grams become unique and
  diffuse, or its signal was borrowed → **unconfirmed** (stays stoplisted).

`make validate-kgram-differential` proves it: real terms (`set`/`class`/`state`) are confirmed
across all orders; a concentrated-but-diffuse word (`and`) is not; a word that only borrows phrase
specificity (`the`) is stripped by the unigram discount. This closes the two-stage design — stopword
deviation (candidates) → k-gram differential (confirmation).
