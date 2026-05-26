# Sync Engine Registry Specification

Status: draft
Scope: SourceOS local-first graph sync engines and implementation repos.

## Purpose

The Sync Engine Registry prevents every repository from inventing its own sync model. Each syncable domain must declare a manifest that identifies its collection, schema version, merge rule, policy class, encryption scope, dangerous fields, audit events, and implementation owner.

A sync engine is not just a transport adapter. It owns domain semantics.

## Required engine manifest

```json
{
  "$schema": "https://sourceos-linux.github.io/sourceos-spec/schemas/SyncEngineManifest.json",
  "engineId": "sourceos.sync.workspace",
  "collection": "workspace",
  "schemaVersion": "0.1.0",
  "ownerRepo": "SocioProphet/prophet-workspace",
  "defaultEnabled": true,
  "policyClass": "high",
  "encryptionScope": "workspace",
  "mergeStrategy": "graph_merge",
  "supportsTombstones": true,
  "supportsRollback": true,
  "supportsExport": true,
  "dangerousFields": [],
  "auditEvents": []
}
```

## Required fields

- engineId: stable engine identifier
- collection: canonical SourceGraph collection
- schemaVersion: semantic version of the engine object model
- ownerRepo: repo responsible for implementation and contract evolution
- defaultEnabled: whether engine is enabled by default
- policyClass: low, medium, high, or critical
- encryptionScope: public, profile, workspace, org, device, or vault
- mergeStrategy: crdt, graph_merge, append_only, manual_review, strongest_policy_wins, signed_authority_required, never_merge, or quarantine
- supportsTombstones: whether deletion is represented with tombstones
- supportsRollback: whether local rollback is supported
- supportsExport: whether records are exportable
- dangerousFields: field names requiring review, redaction, or policy gating
- auditEvents: events emitted by the engine

## Canonical engines

| Engine | Owner | Collection | Policy | Encryption | Merge |
|---|---|---|---|---|---|
| `sourceos.sync.clients` | SourceOS core | clients | high | profile | signed_authority_required |
| `sourceos.sync.workspace` | `SocioProphet/prophet-workspace`, `SocioProphet/sociosphere` | workspace | high | workspace | graph_merge |
| `sourceos.sync.shell` | `SourceOS-Linux/sourceos-shell`, `SourceOS-Linux/TurtleTerm` | shell | high | profile | manual_review |
| `sourceos.sync.agent-registry` | `SocioProphet/agent-registry` | agents | critical | workspace/org | signed_authority_required |
| `sourceos.sync.policy-fabric` | `SocioProphet/policy-fabric` | policy | critical | org/workspace | strongest_policy_wins |
| `sourceos.sync.memory-mesh` | `SocioProphet/memory-mesh` | memory | high | profile/workspace | manual_review |
| `sourceos.sync.browser` | `SourceOS-Linux/BearBrowser` | browser | high | profile/workspace | manual_review |
| `sourceos.sync.secrets` | SourceOS core, Policy Fabric | secrets | critical | vault | never_merge |
| `sourceos.sync.audit` | SourceAudit, Sherlock/Holmes | audit | critical | profile/workspace/org | append_only |
| `sourceos.sync.models` | `SourceOS-Linux/sourceos-model-carry`, `SourceOS-Linux/agent-machine` | models | high | profile/org | manual_review |
| `sourceos.sync.extensions` | SourceOS core, BearBrowser, TurtleTerm, Prophet Workspace | extensions | high | profile/workspace | manual_review |

## Merge strategy semantics

### crdt

For low-risk collaborative state such as presence, cursors, and layout hints.

### graph_merge

For typed graph objects with causal metadata, tombstones, and conflict handling.

### append_only

For audit and provenance. Records are never modified in place.

### manual_review

For changes that may alter agent behavior, memory, shell execution, browser bridge behavior, or workspace topology.

### strongest_policy_wins

For policy. A weaker remote policy cannot override a stronger local, enterprise, repo, or safety policy.

### signed_authority_required

For agent trust, org controls, remote commands, and policy-owned state.

### never_merge

For secrets, raw keys, credentials, private tokens, and device private material.

### quarantine

For unknown schemas, invalid signatures, untrusted relays, unexpected cross-profile writes, and suspected injection attempts.

## Required engine states

- disabled
- local_only
- not_configured
- missing_identity
- missing_device_key
- missing_workspace_key
- network_down
- network_untrusted
- relay_unreachable
- auth_pending
- policy_blocked
- engine_disabled
- engine_dirty
- engine_syncing
- engine_current
- conflict_detected
- review_required
- quarantined
- degraded
- healthy

## Required reason codes

- no_user_profile
- no_org_profile
- policy_denied
- signature_invalid
- schema_unknown
- migration_required
- secret_redacted
- remote_policy_weaker
- remote_policy_newer
- local_policy_stronger
- capability_expired
- agent_untrusted
- relay_untrusted
- workspace_scope_mismatch
- profile_boundary_violation
- manual_review_required

## Acceptance criteria

1. Every sync engine has a manifest.
2. Every engine declares its policy class and merge strategy.
3. Critical engines require signed authority.
4. Secrets use never_merge.
5. Audit uses append_only.
6. Memory, shell, browser, model, and extensions use review-aware strategies.
7. The estate scanner can report missing, invalid, partial, and compliant engine manifests.
