# Program Spec Register — 2026-07-31 intake

Durable capture of the spec corpus handed off on 2026-07-31. **Nothing is
processed inline** (to protect context); everything here is captured, hashed
(`MANIFEST.sha256`), and mapped to its target repo/program with a processing
status. This is the work-plan reference — process clusters into issues
incrementally, most-load-bearing first.

Intake root: `~/dev/spec-intake/2026-07-31/` · Integrity: `MANIFEST.sha256` (286 files)

## Status legend
- **CAPTURED** — copied + hashed; not yet triaged into issues.
- **TRIAGED** — read + mapped to concrete issues/tranches.
- **IN-PROGRESS** — issues filed / work started.

---

## Clusters

### 1. Substrates, Structures & Circuits — Governed Cognition Loop
- **Source:** pasted inline (2026-07-31) + `sources/SourceOS Spec/substrates-structures-circuits*` (if present)
- **Target repo:** `SocioProphet/superconscious`
- **What:** Architectural framework for the cognition loop — 4 axes (substrate ℝ/ℂ/ℍ/𝕆/𝕊/gcForest, structure Hopfield/TL/braid/tensor-net, mixture slots, discovered circuits), shared-trunk + per-adapter-heads, 3-regime approval handle, replay-determinism contract, circuit registry + forbidden-circuits enforcement, SAE/Procrustes alignment, TRUST_SURFACE.yaml + decision-emission event schema.
- **Maps to program:** Emergence stratum (SAE steering, circuit governance) + Exodus (approval gating). Extends the Superconscious cognition loop referenced in the [Agentic Stack spec](../../.claude memory: project_agentic_stack_integration_spec).
- **Status:** CAPTURED. Next: superconscious epic + issues for (a) decision-emission event schema, (b) TRUST_SURFACE additions, (c) circuit registry validators, (d) 3-regime approval.

### 2. SourceOS Spec doc folder (36 files)
- **Source:** `sources/SourceOS Spec/`
- **Targets (by file):** Prophet CLI & System Architecture → `prophet-cli`; OS Level Services and Service Spec → `source-os`/`sourceos-spec`; M2 Adapter IPC Spec v0.1 (JSON-over-stdio subprocess plugins) → `agent-machine`/model-carry; Slash Commands → `TurtleTerm`/agent-term; Prophet Platform Canonical Pane → `prophet-platform`; Campaign automation primitives + Adoption Spec (Foot-Traffic + Weather) → agentic-marketing/adoption; MCP end-to-end alignment → estate MCP; Model Zoo list → model-router/model-carry; Mentor's Guide (Part 3) → learning apparatus.
- **Status:** CAPTURED. Next: per-file triage → route each to its repo's tranche.

### 3. FSMS memory pack (10 files)
- **Source:** `sources/fsms_memory_pack/`
- **Target repo:** `SocioProphet/memory-mesh`
- **What:** Memory operator spec + integrated deployment plan; 6 schemas (episode_bundle, working_memory_state, semantic_memory_release, procedural_memory_bundle, forgetting_policy, promotion_rule); Track A (online LDA/HDP), Track B (incremental LSI + graph updates).
- **Maps to program:** memory-mesh 3-tier memory (episodic/semantic/profile) — directly extends the just-merged GatewayCallAudit work (#45) and the Exodus context-engineering layer.
- **Status:** CAPTURED. Next: memory-mesh epic — the 6 schemas are the highest-value, well-formed artifacts to land first (schema + validator pattern, like Tranche T0).

### 4. Agentic Forge — build-forge + gh-profile (12 files + 2 bundles)
- **Source:** `sources/agentic_forge_running_repo/`, `extracted/build_forge_contract_bundle_v0_1/`, `extracted/gh_profile_v1_contracts_and_actions_harness_bundle/`
- **Targets:** build_forge contract pack + `build_forge_tritrpc_v0_1.proto` → `TriTRPC`/build-forge; gh_profile v1 (local actions kernel, OpenAPI, webhooks schema, GraphQL subset, CLI conformance matrix, local-actions conformance harness) → sovereign SCM / a gh-profile surface (local GitHub-Actions-compatible kernel).
- **Status:** CAPTURED. Note: `build_forge_tritrpc_v0_1.proto` is a real proto contract; gh-profile is a full local-actions conformance suite (19 files).

### 5. SourceOS Obfuscation Genesis Spec v0.7 (10 files)
- **Source:** `extracted/SourceOS_Obfuscation_Genesis_Spec_v0.7/`
- **Target repo:** `source-os` / a genesis surface (relates to the "cybernetic agentic genesis inception spec")
- **What:** SBS braid metagraph, Hopf-fibration internal layers, multiscript letter projection, SIRDI journal framework, proof-of-life patterns, trust-flow handshake (whitehole broadcast), human-centric enforcement.
- **Status:** CAPTURED. Note: braid/Hopf themes align with the Substrates/Circuits structure axis (braid-equivariant retrieval) — cross-reference cluster 1.

### 6. Archive.zip — session/working archives (196 files, NESTED zips)
- **Source:** `extracted/Archive/` (contains nested archives: emvi_session_archive.zip, aht_triproof_vectors_v0_1_bundle, chat_cumulative_archive_bundle_v0_9, wordops_phase0_reference_pack, workspace-plane-v0-export)
- **What:** Mixed session/reference archives; aht_triproof_vectors = canonicalization + evidence-cover registry (relates to proof/evidence plane).
- **Status:** CAPTURED (top level). ⚠️ Nested zips NOT yet extracted — second-pass extract pending user go-ahead.

---

## Recommended processing order (highest load-bearing first)
1. **FSMS memory schemas (cluster 3)** → memory-mesh: 6 well-formed schemas, same schema+validator pattern as Tranche T0, directly extends merged #45.
2. **Substrates/Circuits (cluster 1)** → superconscious: the decision-emission event schema + TRUST_SURFACE additions are concrete, schema-shaped deliverables.
3. **gh-profile local-actions (cluster 4)** → sovereign SCM: a complete conformance suite, ready to stand up.
4. **build-forge + TriTRPC proto (cluster 4)** → TriTRPC.
5. **Obfuscation Genesis (cluster 5)** + **SourceOS Spec docs (cluster 2)** → triage per-file.
6. **Archive nested zips (cluster 6)** → extract + triage.
