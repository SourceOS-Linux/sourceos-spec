# Table Keys as Set-Identifiers / Ranks / Biperpedia Bipartite / Primitives (v0.1)

Every table KEY and INDEX identifies a **set** of rows by an **attribute set**. `SchemaDefinition.keys`
carries them; `tools/validate_key_bipartite.py` is the **live** tool that, fail-closed:

- recomputes each key's **rank** = arity, and **primitive** = (rank == 1, an atomic identity);
- checks the key's attributes are real fields of the table;
- requires **exactly one primary** key (the primary set-identifier);
- resolves every **foreign** key to a real key in the referenced entity — a **Biperpedia-style
  bipartite line** (entity ↔ entity via a shared attribute set);
- and **emits** the entity↔attribute bipartite graph (`--emit`): entities on one side, attributes
  on the other, keys as the lines — the substrate a reasoner walks for dependencies + constraints.

## Conformance
`make validate-table-keys` (in `make validate`; also `--emit` for the graph).
