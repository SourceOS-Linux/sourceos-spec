# Stopword deviation analysis (v0.1) — the words we DROP are governed vocabulary too

The vocab-currency loop drops a fixed stoplist so domain terms surface. But that list is itself an
ungoverned governance decision: a word that is filler in one domain ("set", "class", "state",
"required", "value") is a real TERM in another (math, OOP, state machines, config). Dropping it
universally erases signal where it matters. So we audit the dropped words the same way we audit the
kept ones — frequency, connections, compositional density — ACROSS domains, using TWO signals
because frequency alone lies:

- **cross-domain deviation** (`concentration`) — is the word's relative-frequency mass concentrated
  in a subset of domains?
- **compositional density** — of the word's content-neighbour adjacencies in that domain, what
  fraction are REPEATED collocations? A term recurs in fixed phrases ("empty set", "state machine");
  a stylistic word ("and") glues arbitrary, unique content.

Verdicts: **term-candidate** (concentrated AND compositional → a domain term hiding in the stoplist,
propose un-stoplisting it there), **stylistic** (concentrated by style only → keep, but flagged),
**noise** (uniform → true stopword everywhere). The stoplist becomes an auditable, per-domain
artifact instead of a hard-coded assumption; term-candidates are a remediation signal like the
currency loop's candidate terms and the agreement test's drift.

`make validate-stopword-analysis` proves the two-signal discrimination on fixtures (real domain
terms surfaced; a stylistically-concentrated word is NOT wrongly promoted — the trap frequency alone
falls into; a uniform word is noise). `make stopword-analysis-live` audits the shipped stoplist over
`specs/*.md`.

Compositional density here is the **bigram floor** of the deeper follow-on: the **k-gram TF-IDF/LSA
differential** over orders 3..7, which confirms a candidate by showing its signal GROWS with n-gram
order (it participates in domain-specific higher-order collocations) rather than staying diffuse.
