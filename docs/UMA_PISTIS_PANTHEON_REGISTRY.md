# UMA Pistis Pantheon Registry

This document records the current human-readable naming registry for the local-first SourceOS/SociOS execution model discussed across the SourceOS-Linux and SociOS-Linux repos. It is intentionally *descriptive first* and is meant to guide follow-on contract work in `schemas/`, `openapi*.yaml`, and `asyncapi*.yaml`.

The registry does **not** replace typed contracts. It explains where named platform concepts belong in the ecosystem and how they should map into the canonical contract layer.

---

## Why this document exists

The current SourceOS/SociOS spec already defines the two-plane model, typed governance objects, workflow/provenance primitives, and the agent plane. What it does **not** yet do is capture the naming and repo-placement decisions for the local-first Linux platform being assembled across:

- `SourceOS-Linux/sourceos-spec`
- `SociOS-Linux/source-os`
- `SociOS-Linux/agentos-spine`
- `SociOS-Linux/workstation-contracts`
- `SociOS-Linux/socios`

This document makes those boundaries explicit so that future schema work stays additive and lands in the right repo.

---

## Canonical naming registry

| Surface | UI name | Code slug | Primary role | Upstream home |
|---|---|---|---|---|
| Platform | UMA Pistis | `uma-pistis` | Local-first platform shell and trust posture | `source-os` + `agentos-spine` |
| Identity / keys | MICHAEL | `micha137` | Proof-of-life, device attestation, countersign identity layer | `sourceos-spec` contracts + `source-os` substrate enforcement |
| Ingress / gateway | ANSER | `anser` | User-facing edge ingress and local-first service entry | `agentos-spine` |
| Overlay mesh / bridge | IANUS | `ianus` | Domain and lane bridge across local, mesh, and cluster surfaces | `sourceos-spec` contracts + `agentos-spine` runtime |
| Event fabric | PHAROS | `pharos` | Event backbone, watermarks, durable publication | `sourceos-spec` AsyncAPI + `agentos-spine` |
| Threading conventions | ARIADNE | `ariadne` | Thread, retry, deadline, and dedupe conventions layered on PHAROS | `sourceos-spec` AsyncAPI + shared SDKs |
| Consensus engine | ASHAMAAT | `ashamaat` | Human proof-of-life / proof-of-deed consensus engine | `sourceos-spec` contracts + future runtime repo |
| Immutable action log | PRAXIS | `praxis` | Signed action stream for acts/words/deeds/will/events | `sourceos-spec` contracts |
| Immutable roots | Arbor | `arbor` | OSTree-backed immutable system and agent roots | `source-os` |
| Object/edition layer | Codex | `codex` | Content-addressed objects and edition manifests | `sourceos-spec` contracts + `source-os` runtime |
| Federated codex | Codex Alexandrius | `codex-alexandrius` | Higher-order shared codex across lanes/tenants/sites | `sourceos-spec` + `agentos-spine` |
| Knowledge corpus | Sophia Alexandria | `sophia-alexandria` | Curated world-knowledge / pedagogical corpus | `agentos-spine` + future app layer |
| Cold archive | Serapeum | `serapeum` | Deep archive / anchor destination | `source-os` policy + backup/archive lane |
| Search | Mnemosyne | `mnemosyne` | Search/index and recall layer | `sourceos-spec` + app/runtime repos |
| Viewer / inspector | Hypethia | `hypethia` | Evidence viewer, diff/proof presentation, provenance inspector | `agentos-spine` + app/runtime repos |
| Observability / guard | ARGUS PHYLAX | `argus-phylax` | Observability, guard, SLOs, proofs, anomaly attestation | `agentos-spine` + workstation/CI conformance |
| Time / cadence | Kairos | `kairos` | Time windows, deadlines, SLO cadence, promotion timing | `sourceos-spec` policy + runtime policy |
| Quorum / promotion | Shiloh | `shiloh` | Promotion gating from local-first to shared mesh | `sourceos-spec` policy + `agentos-spine` |

---

## Repo placement rules

### 1. `sourceos-spec` is the canonical contract home

Anything that needs a stable machine-readable shape belongs here first:

- identity and attestation payloads for MICHAEL
- PRAXIS action envelopes, verbs, witnesses, and replay semantics
- ASHAMAAT consensus receipts, validator set records, and anchors
- PHAROS / ARIADNE event channels and headers
- IANUS corridor and path policy objects
- Codex manifests, object references, anchors, and visibility labels
- Kairos and Shiloh policy documents

### 2. `source-os` is the immutable substrate

Anything that is about Linux host posture, persistent encrypted volumes, OSTree roots, or local-first fallback posture belongs in `source-os` rather than the spec repo.

### 3. `agentos-spine` is the integration/workspace assembly repo

Anything that composes services, binds the UI shell, routes runtime surfaces, or assembles local-first + shared-mesh behavior belongs in `agentos-spine`.

### 4. `workstation-contracts` is the lane and conformance gate

Anything that defines execution-lane shape, validation, conformance, evidence collection, and build/release admissibility belongs in `workstation-contracts`.

### 5. `socios` is opt-in automation only

Anything involving community automation, CI/CD automation, catalog publication, signatures, or optional AI-assisted automation belongs in `socios` and must remain opt-in.

---

## Build and orchestration placement

The upstream lane split should be treated as:

- **Argo / Tekton**: orchestration and execution-lane control-plane tooling for GitOps, workflow execution, and pipeline admission.
- **Foreman / Katello**: content, provisioning, build promotion, repository/content views, and image/package lifecycle management.

These are complementary roles, not replacements for one another.

### Practical interpretation

- `workstation-contracts` should describe *what* a valid lane looks like.
- Argo / Tekton should execute validated lanes.
- Foreman / Katello should manage image/content promotion and provisioning inputs that validated lanes consume.
- `socios` may automate portions of this stack, but only under Proof-of-Life + signed intent.

---

## Privacy and local-first stance

The registry assumes the following operating posture:

- local-first by default
- shared mesh promotion only when human quorum and platform health gates pass
- privacy-preserving analytics only when opt-in, with both k-anonymity and differential privacy controls
- content-addressed and immutable history rather than destructive overwrite
- proofs, provenance, and attestation always visible in viewer/search layers

---

## Follow-on contract work implied by this registry

This document implies future additive contract work in `sourceos-spec` for at least:

1. MICHAEL identity/attestation document(s)
2. PRAXIS action/verb schemas
3. ASHAMAAT receipt / validator / anchor schemas
4. PHAROS/ARIADNE AsyncAPI channels + headers
5. IANUS corridor/path/bridge policy shapes
6. Codex manifest / edition / visibility contracts
7. Kairos / Shiloh policy and gate objects
8. ARGUS PHYLAX evidence / SLO / anomaly-attestation records

---

## Status

This registry is a docs-first landing artifact. It is not yet normative over the existing schema catalog. It is intended to guide the next additive spec PRs.
