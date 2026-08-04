# Six-Layer Fingerprint Stack (v0.1) — classification that can say "I don't know"

Consumes SP-FPRINT-STACK-001. Assigns a business data class to a **column** from six
independent metadata fingerprint layers, pooled through a structurally-monotone aggregator,
gated so that the pipeline **cannot manufacture confidence**.

This lands the spine: the stance algebra, the layer witnesses, the admissibility gate, the
drift detector, and the enforcement policy. What it deliberately does not land is listed
under *Not in this contract* below.

## The one thing that is actually new

The 2018 source design already had the three-channel matcher, the datatype ontology
(OntoDT), the mereotopological framing (its own term), and the routing of data-quality
inference into access enforcement. It had no way to say **"I don't know"** distinctly from
**"my evidence contradicts itself"**.

Everything here follows from making those two different values:

| Stance | Support set | Plausibility set | Meaning | Remediation |
| --- | --- | --- | --- | --- |
| `POS` | {t} | {t} | supported, unrefuted | — |
| `NEG` | {f} | {f} | refuted, unsupported | — |
| `ZERO` | ∅ | {t,f} | **ignorance** | gather evidence |
| `INADMISSIBLE` | {t,f} | ∅ | **conflict** | resolve the contradiction |

A three-valued verdict collapses the last two into one amber, and they are not the same
problem: a gap wants more data, a glut wants a human. The empty conformal set **is** the
glut — one element, not two.

## Vocabulary boundary — read this before adding a verdict

This repo already carries two verdict vocabularies and holds them apart deliberately
(epistemic-kernel delta 6). `ClassificationStance` is a **third**, and it is declared here
rather than introduced silently:

| Vocabulary | Subject | Values |
| --- | --- | --- |
| Ops ternary | an **operation's** health | `ok` / `sad` / `bad` |
| `ReasoningAssay` | a **claim**, on 5 axes | projected to the ops ternary at render time |
| `ClassificationStance` | a **(column, candidate class) binding** | `POS` / `NEG` / `ZERO` / `INADMISSIBLE` |

They do not mix and none projects onto another: a column-class binding is not a claim and
not an operation. The nearest neighbour is the Assay's `verifier.judgment`
(`supported` / `refuted` / `abstained`) — which is three-valued with **no glut**, i.e. it is
FOUR minus exactly the value this stack exists to carry. That is a coincidence worth
noticing, not a mapping to build.

## The six layers, and why six

The argument is **independent failure**, not feature count.

| Layer | Signal | Fails when | Correlated with |
| --- | --- | --- | --- |
| L1 OntoDT type | type-path compatibility | everything declared `VARCHAR` | — |
| L2 OntoDQ profile | observed statistics (the only layer that reads values) | table empty / newly seeded | **anti**-correlated with L1 |
| L3 Business glossary | closed-vocabulary label match | glossary stale or absent | correlated with L4 |
| L4 Operational semantics | which operations are admissible | no query log (observed half) | correlated with L3 |
| L5 Table topic | bag of L3 labels across the header | junk-drawer staging; **silent repurpose** | depends on L3 |
| L6 Schema / key graph | PKs, FKs, inclusion dependencies | constraints undeclared in DDL | — |

L1 and L2 failing in opposite conditions is the ensemble working as designed: a
newly-declared table has good types and no data, a legacy estate has bad types and abundant
data. But L3–L4 and L3–L5 are **dependent**, which is why quorum is measured, not counted
(see `n_eff`).

L4 has no counterpart in commercial catalog tooling. If production takes `AVG()` of a column
the ontology declares a surrogate key, that is a detected conflict — and it is a **glut**,
not a weak match, because it means either the label is wrong or downstream code has a bug,
and both need a human.

## The five properties the validator enforces

Order is the safety property: **pool → guard → quantize**.

1. **Nothing manufactures confidence.** Guards are tensor factors; they can only lower
   stance in the knowledge order. Post-guard evidence never exceeds pooled evidence in
   either component. Because lowering widens the plausibility set, gated stances **retain**
   their conformal coverage — policy costs efficiency (more abstention), never validity.
2. **Every stored verdict is recomputed.** The stance from its evidence, the pooled evidence
   from the admissible layers, `n_eff` from the covariance spectrum, the drift flag from the
   measured distance. An asserted classification cannot outrun what produced it.
3. **Quorum is effective independence, not concentration.** The Herfindahl index measures
   concentration of *magnitude*: two perfectly correlated layers contributing equally give
   `H = 0.5`, which looks healthy while supplying one layer's worth of information. `n_eff`
   — the participation ratio of the layer covariance spectrum — is the sufficient statistic;
   `H` is retained only as a cheap precheck. Expect `n_eff < 6` on every real estate.
4. **Coverage does not compose.** A chain of `n` bindings each valid at `ε` gives at best
   `nε`. Composition depth and the honestly-loosened level ride on the stance.
5. **An inadmissible layer contributes ZERO** — the annihilator — never a guessed value.

Two structural details worth stating because they are easy to get wrong:

- **Guards are measurable with respect to evidence and witness only.** A guard that reads
  the outcome breaks exchangeability and voids the coverage guarantee, so guard input paths
  are restricted by pattern; `value.*` cannot be named.
- **The reading tag lives in the type**, not the witness (DR-5). Belnap support and conformal
  plausibility are conflates of one another; mixing them without applying `−` silently
  exchanges gap and glut. A lost tag is silently wrong; a missing required field is loudly
  absent.

## Axiom X1 — why parthood and subtyping are separate arrows

`∀x,y. x ≠ y → ¬(P(x,y) ∧ x ⊑ y)`, enforced as a CI invariant over the OntoDT fixture.

Slide 31 of the source deck asks two questions of one graph: *how many tables contain the
field "Email Address"* (a count over the **subtype** closure) and *what attributes can I
expect under "Client Address"* (an enumeration of **parts**). If `is_a` and `part_of` share
an arrow type, those answers cannot both be right. X1 is not a refinement of the original
design — it is the precondition for the original design's own questions being simultaneously
answerable. Count aggregation traverses `⊑` only; parthood does not roll up.

Under the open-world assumption an aggregate count is an **interval** `[N⁺, N⁺ + N⁰]`, and
`N^INADM` is reported separately — a contradiction is not a maybe.

## L5's drift detector is blocking, not advisory

The stability that makes the table-topic layer a good prior makes it a dangerous one. If a
column is silently repurposed without a rename, the schema does not change, so L5's evidence
is *precisely the unchanged schema* — **L5 asserts the stale semantics with maximum
confidence exactly when it is wrong.** That is the worst possible correlation between
confidence and error.

- **L5-D1** — drift above threshold with an unchanged `schemaVersion` puts L5 and L2 in
  conflict: the pair emits a glut and routes to a steward (with a queue reference, so
  "routes to a steward" is a behaviour rather than a claim).
- **L5-D2** — L5 may never outvote L2 under drift: the drift flag enters the aggregator as a
  guard and annihilates L5's contribution *before* pooling.

The 2018 architecture could not express this, having no glut value to route to.

## Cold start — the honest day-one output

L3 and L4 are exactly what a customer lacks when they engage; a customer with a maintained
glossary would not need this system. So their absence is the **normal state**, not an error,
and phase 0 ships something real without them:

| Phase | What runs | What ships |
| --- | --- | --- |
| 0 | L1, L2, L5 (degraded to raw header tokens), L6 | **Estate admissibility report** + candidate glossary; every assignment `ZERO`, but hard axioms carry `NEG` from day one |
| 1 | + steward adjudication of fingerprint clusters | glossary entries that are *simultaneously* calibration data |
| 2 | + per-class calibration floor cleared | `POS` becomes available |
| 3 | + query logs attached | L4's observed channel; declared-vs-observed conflicts as the highest-value steward queue |
| 4 | all six | steady state, `n_eff` reported, drift running |

**Refutation is available before assertion is.** Hard axioms need no calibration, so
"these columns are definitely not what they claim to be" is a genuine phase-0 deliverable.

*Resolved ambiguity:* SP-FPRINT-STACK-001 §8 runs L5 at phase 0 while §4 preconditions L5 on
having L3-labelled columns, which do not exist yet. Here L5 is admissible at phase 0 but
`degraded: true`, running on raw header tokens rather than glossary-resolved labels.

## DR-4 — what a PEP does with ZERO

Settled by `ClassificationEnforcementPolicy`. This was latent in the 2018 design, which
already routed data-quality inference into access enforcement and had nowhere for "we do not
know" to live, so it silently became either over-blocking or a leak.

- `POS → allow`, `NEG → deny`. Not knobs.
- `INADMISSIBLE → fail-closed`, **deliberately not configurable**. A glut means two layers
  disagree about what the column *is*, and one reading may well be "personal data". Serving
  it would let a contradiction resolve itself in the requester's favour — the one resolution
  nobody chose.
- `ZERO` is the knob, **per resource class**, and constrained: fail-open requires an
  attestation, and is unavailable at `confidential`/`restricted` sensitivity regardless of
  attestation. Over-blocking a public reference table is a nuisance; over-sharing an
  unclassified column is a breach.
- An **abstention budget** keeps governed abstention from quietly becoming a system that has
  stopped answering.

## On the aggregator library

`DataClass.classifier.kind` was pinned by a `const` to `tf-lattice-wide-and-deep`. **The
TensorFlow Lattice repository was archived by its owner in April 2026** and is read-only;
its last release was July 2024. Its late releases moved Keras imports to `tf_keras` and
deprecated Estimators — it migrated *onto* the Keras 3 era via a compatibility shim and was
then archived. It did not become part of Keras.

The pin is now an enum. `monotone-logistic` is what this estate actually trains and ships
(#264/#265); `monotone-lattice-hll` is the successor path, whose Hierarchical Lattice Layer
trains with standard SGD rather than projected gradient descent under many constraints and
accepts high-dimensional input the older lattice layer could not hold in memory — which is
exactly the 6-layer × 2-component input here. The deprecated value is retained so existing
documents stay valid.

**Monotonicity must be structural, never regularization-encouraged.** A penalty term makes
M5 probabilistic, which voids the gate-soundness argument; a library offering only soft
constraints is rejected on those grounds, and the schema refuses `monotonicityEnforcement:
regularized`.

## Conformance

```
make validate-fingerprint-stack
```

Two tools, and the second is the point:

- `tools/validate_fingerprint_stack.py` — 81 checks over the examples, the OntoDT graph
  fixture, and 9 schema negative vectors.
- `tools/test_fingerprint_stack_teeth.py` — mutates each conformant example one invariant at
  a time and **requires the validator to reject it, for the stated reason**. 25 gates proven
  to bite. A gate that stays green under its own mutation is reported as a failure of the
  *checker*.

Plus `check_m5_binds()`, which runs the monotonicity property test against a deliberately
non-monotone aggregator and fails if the test does not catch it.

This discipline is not decorative. Its nearest precedent in this repo shipped the exact
defect it guards against: #264's monotone classifier had a fixture holding the monotone
feature constant, so the constraint bound nothing and the test passed vacuously — found and
fixed in #265. A green check is not evidence until you have watched it go red.

## Not in this contract

Named so the gaps are visible rather than assumed closed:

- **WO-15 justification-scoped `INADMISSIBLE`** — required before production. Without it,
  one bad axiom makes everything derivable and every query returns `INADMISSIBLE`. Note the
  architectural point: this is **classical inference over justified fragments** with the
  bilattice used for *bookkeeping the outcomes* — it is **not** paraconsistent inference, and
  that is the most likely misreading of this design.
- **Cold-start phases 1–4** as executable pipeline (phase 0 artifacts are contracted here).
- **KKO cross-domain transfer** — a hypothesis with a test protocol, not a capability. It
  must not appear in customer-facing material until the held-out-domain label-efficiency
  measurement returns a number, and the ablation arm (layers concatenated, no upper-ontology
  mediation) must run: if the ablation matches, KKO is not doing the work.
- **DR-2** (marginal vs. Mondrian coverage, per-class calibration floor), **DR-7** (cascade
  with early exit — must be calibrated as a unit, never per-stage), **DR-8** (constraint M3),
  **DR-9** (independence-certificate schema, required before any layer pair is granted
  probabilistic-sum pooling).

## A note on the source

Slides 28–30 of the 2018 deck embed the entire OntoDT/OntoDQ argument as three TIFFs — 95 MB
of a 120 MB file. It is un-indexable, un-greppable, un-diffable, and invisible to text
extraction. The knowledge-management architecture was stored in a form that defeats
knowledge management. Every diagram in this stack is committed as source (Mermaid, Graphviz
or TTL) with rendering as a build artifact.
