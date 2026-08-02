# OperationalDAG / GovernedLoop (v0.1) — loops vs graphs, made mechanical

Identify where each wins, and govern both:

- **`OperationalDAG`** carries **identity / dependency / causality**, so it MUST be **acyclic** —
  `validate_dag_loop.py` refuses a cycle (a loop where a DAG belongs is unsatisfiable). Every node
  is **semantically grounded** (`semanticRef` → a GlossaryTerm / DataClass / service), so governance
  reasons about *what* is ordered, not opaque tasks. Placement is a field-calculus reference
  (`placementRef` → PlacementFact / phase-field), a gradient on the field, not ad-hoc.
- **`GovernedLoop`** is the ONLY place a cycle is legitimate — **correction / convergence /
  homeostasis** win as loops (vocab currency, self-heal, reasoner fixpoint, classifier retrain).
  A loop is admissible only if it is **bounded** (`maxIterations`), **convergent** (a measure),
  **fail-closed** (`onNonConvergence` ∈ {refuse, escalate-human}, never *continue*), and **admitted
  by the superconscious** (`admission.superconsciousRef` — the global governor holds the convergence
  budget + refusal authority; loops don't self-authorize).

The bug class this refuses: a **loop where a DAG belongs** (a cycle → refused) and a **DAG where a
loop belongs** (no self-correction). DAGs = identity/dependency; loops = correction; the
superconscious over the field decides *where* and *whether*.

## Conformance
`make validate-dag-loop` (in `make validate`).
