# Agreement test (v0.1) — declared relations vs observed dependencies

The neurosymbolic check that the vocabulary tells the truth about structure. Two independent views
of the same estate:

- **symbolic** — the glossary's typed `relations` between terms (composition: `has-a`, `has-member`);
- **observed** — the blast-radius / dependency graph over estate entities (as a governed GBRG
  analysis emits it).

Projected onto each other via `alignment.estateBinding`, they must **agree**:

- **overclaim** — a term declares `A has-a B` (both bound) but the graph shows no edge → the
  vocabulary asserts a dependency the estate doesn't exhibit. **Fail-closed** (governance hole).
- **drift** — the graph shows an edge between two bound entities that no relation names → the estate
  has a dependency the vocabulary hasn't captured. Surfaced as a **remediation candidate** (a
  proposed `has-a` relation), not a hard failure — same treatment as the vocab-currency loop's
  candidate terms.

`tools/agreement_test.py` CONSUMES a blast-radius graph (GBRG owns that graph; this only compares).
Only composition predicates (`has-a`, `has-member`) imply runtime dependencies; `is-a`/`skos:*` are
subsumption/lexical and excluded. `make validate-agreement` proves: aligned agrees, overclaim is
refused, drift is reported as a candidate.
