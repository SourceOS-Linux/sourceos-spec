# Glossary Alignment Contract (v0.1) — vocabulary as governance substrate

Language establishes meaning and regulates state. A term is only usable to reason about
governance when it is **captured, vector-aligned, and implemented** — so an `approved`
`GlossaryTerm` must, fail-closed, carry all three (validator):

1. **Capture** — `alignment.ontologyClassRef`: a formal ontology/KKO class.
2. **Vector-align** — `alignment.vectorLink`: an NP↔VP link in the SOVEREIGN space
   (model + dimension pinned to the `EmbeddingRequest` const, 768), reciprocated by the peer.
3. **Implement** — `alignment.estateBinding`: a real estate entity/service (NP→entity, VP→action|service, Tesnière).

## Typed relations (reasoner substrate)

`relations` carry a CLOSED predicate set (RDF/RDFS/SKOS/FOAF): `is-type`/`has-type`,
`is-a`, `has-a`, `is-member`/`has-member`, `skos:broader`/`skos:narrower`, `skos:related`,
`foaf:member`, `has-datatype`. The validator enforces the constraints a reasoner needs:
inverse pairs reciprocate, `skos:related` is symmetric, and `is-a` subsumption is **acyclic**
(a cycle is an unsatisfiable constraint). This is what lets a reasoner derive dependencies
and constraints from the vocabulary.

## Currency (follow-up) & agreement (follow-up)

- **Currency**: the glossary is a closed fixed set (LSA/LSI); the live estate generates an
  open topic space (LDA). The LSA↔LDA divergence flags new/optimal vocab not yet captured.
- **Agreement**: a standard test cross-checks these relations against the **governed
  blast-radius graph** (dependencies) and the **neurosymbolic agent's domain + symbols**,
  with follow-up automation to remediate and keep the three consistent.

## Conformance
`make validate-glossary-alignment-examples` (in `make validate`).
