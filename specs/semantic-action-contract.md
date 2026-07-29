# SemanticAction Contract v0.1 — the declarative typed-action registry

Status: v0.1.0 (normative for `schemas/SemanticAction.json`)
Provenance: the NL→plan compiler lane — actions registered as typed,
declarative signatures the planner searches over, in the STRIPS tradition of
typed operators rather than executable tool lists.
Validation: `make validate-semantic-action-examples`
(tools/validate_semantic_action_examples.py).

## 1. Scope

A `SemanticAction` is a declarative registration: name + version + typed
inputs + typed output + subsumption constraints + executor binding + effect
posture + registry metadata. The NL→plan compiler grounds a natural-language
request into a goal type, then searches the registry for action compositions
whose type signatures chain from what it has to what it needs. Discovery and
composition are **by type only** — the planner never executes anything to find
a plan.

## 2. Typing and polymorphism (normative)

- `inputs[].typeRef` / `output.typeRef` are ontology concept URIs (KKO
  reference concepts recommended — the same URI vocabulary
  `KnowledgeNugget.kkoTypeRefs` uses, so nuggets are directly bindable as
  typed planner values).
- **Binding rule: a value binds a slot when its type is a subclass of (or
  equal to) the slot's `typeRef`.** This is how polymorphism works: an action
  over `kko:Organization` accepts a value typed `kko:Business` without a
  per-subtype registration.
- `constraints[]` add further requirements, each checked at plan-search time
  against the ontology: `subClassOf` (subject's type specializes `typeRef`),
  `instanceOf` (bound value is an instance of `typeRef`), `sameAs` (subject
  denotes the same individual as `typeRef`). The kind taxonomy is closed at
  v0.1; `subject` is a declared input name or the literal `"output"`
  (resolution validator-enforced).
- Input signatures are total: every slot declares `name`, `typeRef`,
  `required`, and `cardinality` (`one|many`) — a planner must never meet a
  partially declared slot.

## 3. Search-time purity and B-after-A (normative)

**Actions are side-effect-free at plan-search time.** Search may instantiate,
bind, and score any action with zero world change. That is why the whole
registry can be searched exhaustively and adversarially without governance
hops.

`sideEffects` declares the executor's run-time posture, and its vocabulary is
exactly two values (validator-pinned so a third value can never land
silently):

- `"none"` — a pure lookup/computation; safe to execute without governance
  hops.
- `"effect-request"` — the executor does **NOT** change the world itself; it
  emits an MPCC `EffectRequest`, and any actual change happens only after an
  `EffectDecision` approves it, recorded as an `EffectRecord` (decision before
  action — B-after-A).

There is deliberately **no `"direct"` value**: an action that would mutate the
world without the effect lifecycle is unregistrable, and the negative
conformance vectors keep that executable. The canonical effect-request example
makes the posture structural: its `output.typeRef` is the `EffectRequest`
contract itself — at plan time the action's output IS the proposal, never the
effect.

## 4. Overlap decisions (spec-first conformance)

| Existing contract | Decision |
|-------------------|----------|
| `EffectRequest` / `EffectDecision` / `EffectRecord` | Not duplicated. `sideEffects: "effect-request"` defers to that lifecycle by posture; the effect-request example's output is typed by the `EffectRequest` contract URI. |
| `SkillManifest` | Runtime skill activation/requirements stay there. `executorRef` may point at a SkillManifest; `SemanticAction` is the plan-search type surface over it. |
| `LauncherAction` | Workstation launcher/command-bus surface stays there; not a planner registry. |
| `WorkflowSpec` / `WorkflowNode` | A compiled plan may materialize as a `WorkflowSpec`; `SemanticAction` is the search-time vocabulary the compiler draws from, not the executed DAG. |
| `ExecutionDecision` / `PolicyDecision` | Governance verdicts stay there; the effect lifecycle referenced above already grounds in them. |
| `CapabilityContract` / `CapabilityToken` | Authority to *run* an executor is the capability plane's concern; the registry only declares the typed surface and effect posture. |

## 5. Versioning

The family versions as one contract, pinned by the `specVersion` const
`0.1.0`. Each registration additionally carries its own semver `version` for
its signature; any signature change bumps it. Additive optional fields or
widened enums bump the family minor; anything that can invalidate an existing
document bumps the major, with CHANGELOG + ADR per CONTRIBUTING.md.

## 6. Known gaps (deliberate, v0.1)

- No OpenAPI/AsyncAPI operations or semantic-context mappings yet (matches how
  recent contract families landed; wiring follows once names have settled).
- Subsumption checking (`subClassOf` resolution against KKO or another
  ontology) happens in the planner, not in CI — CI validates structure and
  subject resolution only.
- One output per action; multi-output actions decompose into multiple
  registrations.
- Preconditions/postconditions beyond type constraints (guards, cost models,
  quality profiles) are future work; `deprecated` is the only lifecycle flag
  at v0.1.
