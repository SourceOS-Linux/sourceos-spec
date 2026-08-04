# Contract percolation — making sourceos-spec the *actuated* single authority

The estate is designed so every contract has ONE canonical home here, and consumers vendor
copies. The design existed (`SourceOSRepoManifest.ownedSchemas` / `authorityRepos`, and
`auditEvents: [spec.schema.added]`) — but it was **validated, never actuated**. So contracts got
authored elsewhere and never percolated back: `AutonomyAdmissionReceipt` and `QuorumProof` are
live in services yet **absent from this spec**. This directory closes that, two layers per gap.

## The registry (single authority)
`registry/contract-registry.json` is the generated canonical index: every `$id`'d schema this
repo owns, with its sha256. `tools/reconcile_contracts.py --emit-registry` regenerates it; CI
fails if a schema change didn't (the registry can never go stale).

## Gap → two layers

| Gap | Detection layer | Actuation layer |
|---|---|---|
| **1 — no upstream percolation** (consumer→spec) | `reconcile_contracts.py --check-consumer` flags an **ORPHAN**: a schema a consumer vendors that no authority repo owns → it has no canonical home | consumer CI that hits an orphan opens an **upstream PR to this repo** adding the contract (the reverse of the one-way sync) |
| **2 — no propagation on merge** (spec→consumer) | the **STALE** check: a vendored copy whose sha256 ≠ canonical → a propagation was missed | `propagate-contracts-on-merge.yml`: a merge changing `schemas/**` **dispatches a re-sync to every registered consumer** (`registry/consumers.json`), which the self-heal responder lands |
| **3 — no canonical-origin authority** | the **UNREGISTERED** check + `check_duplicate_schema_ids.py`: every live `$id` must resolve to a registry entry owned by an authority repo | `registry/contract-registry.json` + `ownedSchemas`/`authorityRepos` in each manifest make "authored in spec" the single source of truth; CODEOWNERS routes contract changes here |

## Adopting it (consumer side)
Add the repo to `registry/consumers.json`, drop a `.sourceos/manifest.json` declaring
`ownedSchemas` + `authorityRepos`, and run in CI:
`python3 reconcile_contracts.py --check-consumer .sourceos/manifest.json <vendored-schemas-dir>`.
An orphan or stale copy fails the build — the drift that stopped the canon self-updating can no
longer land silently.
