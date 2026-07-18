# SourceOS Interaction Runtime Bridge Ledger

Status: implementation ledger  
Last updated: 2026-06-02

## Purpose

This ledger records the bounded runtime bridge work added after the original SourceOS interaction substrate contract/reference wave.

The bridge remains pull/import oriented:

```text
Noetica typed transport / local-service boundary
  -> bounded SourceOSInteractionEvent JSON artifact export
  -> optional AgentTerm import/render
```

It does not introduce live service coupling, event streaming, OpsHistory authority, AgentTerm default dependency, or production runtime authority.

## Completed bridge tranches

| Repository | PR | Merge commit | Role |
| --- | --- | --- | --- |
| `SocioProphet/Noetica` | `#45` | `986059dbe7fc5bf8435c784ad5adbf4230dfca78` | Added transport/local-service placement guidance and fixture-only SourceOS interaction examples. |
| `SourceOS-Linux/sourceos-spec` | direct + `#122` | `87d66e8160b55d9fabaacb4140bac339dc6de312`, `c23db7c7736e114cb753c26f867cef7590666e1a` | Added and indexed the Noetica placement addendum. |
| `SocioProphet/Noetica` | `#47` | `60b720f5c43f4fe2b315a9e81078b3c48b1e5160` | Added ADR-0001 selecting bounded local artifact/export as the first runtime bridge target. |
| `SocioProphet/Noetica` | `#48` | `b09a7bbf4a843dd9cd7b54a80537d7dc8b551302` | Added SourceOS interaction event builders, deterministic fixture-backed artifact export, package script, and CI validation. |
| `SourceOS-Linux/agent-term` | `#50` | `61870a9dff19c93cceeb0c521d008e041214140a` | Added opt-in Noetica artifact import from file/directory into AgentTerm's local event log. |

## Current implementation shape

Noetica owns bounded artifact export from its transport/local-service boundary:

- `lib/sourceos/interactionEvent.ts`
- `scripts/export-sourceos-interaction-events.mjs`
- `npm run sourceos:events:export`
- CI validation through `validate.yml`

AgentTerm owns opt-in artifact import/render:

- `src/agent_term/noetica_import.py`
- `agent-term-interaction import-noetica <file-or-directory>`
- import tests for single-file and directory imports

## Validation lanes

| Repository | Validation |
| --- | --- |
| `SocioProphet/Noetica` | `validate` passed for `#45`, `#47`, and `#48`. |
| `SourceOS-Linux/agent-term` | `CI` passed for `#50`. |
| `SourceOS-Linux/sourceos-spec` | `SVF Validation` and `validate-ops-history` passed for `#122` and `#123`. |

## Boundary posture

The bridge is intentionally bounded:

- No live Noetica-to-AgentTerm stream was added.
- No AgentTerm dependency was added to Noetica's default runtime path.
- No local endpoint serving was added.
- No SSE/WebSocket path was added.
- No OpsHistory append-only authority was added.
- No Policy Fabric, Agent Registry, Memory Mesh, Superconscious, or AgentPlane authority moved into Noetica or AgentTerm.
- Events remain summary/ref-oriented and must not carry private reasoning, raw transcripts, raw shell output, browser history, credentials, secrets, unrestricted provider payloads, or raw execution logs.

## Follow-up issue routing

| Owner | Issue | Scope |
| --- | --- | --- |
| `SocioProphet/Noetica` | `#49` | Select production app-data export path once the local service install/runtime contract stabilizes. |
| `SocioProphet/Noetica` | `#50` | Evaluate an optional local recent-event endpoint after artifact export remains stable. |
| `SocioProphet/Noetica` | `#51` | Decide whether OpsHistory becomes the durable event store after artifact export/import is proven. |
| `SocioProphet/policy-fabric` | `#94` | Bind Policy Fabric decision refs and admission semantics into the runtime bridge. |
| `SocioProphet/agent-registry` | `#48` | Bind identity, grant, session, and revocation refs into the runtime bridge. |
| `SocioProphet/memory-mesh` | `#37` | Bind context-pack and durable memory refs into the runtime bridge. |

## Remaining work

1. Complete the issue-routed follow-up items above.
2. Replace pinned vendoring with a managed package, subtree, or submodule strategy.
3. Add a replay demo that consumes the canonical reference-flow packet without live service dependencies.
4. Defer SocioSphere manifest/lock mutation until network-aware materializer supports live commit SHA resolution.
