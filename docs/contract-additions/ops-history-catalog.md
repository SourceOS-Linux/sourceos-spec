# OpsHistory Contract Catalog

Status: additive contract catalog for OpsHistory, BearHistory, local-first service manifests, operational receipts, context-pack references, and redaction tombstones.

This catalog supplements `schemas/README.md` and `examples/README.md` while the schema index is being normalized.

## Schema additions

| File | Type | URN prefix |
| --- | --- | --- |
| `OpsHistoryEvent.json` | OpsHistoryEvent | `urn:srcos:ops-history-event:` |
| `OpsHistorySyncPolicy.json` | OpsHistorySyncPolicy | `urn:srcos:ops-history-sync-policy:` |
| `LocalFirstServiceManifest.json` | LocalFirstServiceManifest | `urn:srcos:local-first-service:` |
| `BearHistoryEvent.json` | BearHistoryEvent | `urn:srcos:bearhistory-event:` |
| `BearHistorySyncPolicy.json` | BearHistorySyncPolicy | `urn:srcos:bearhistory-sync-policy:` |
| `ShellReceiptEvent.json` | ShellReceiptEvent | `urn:srcos:shell-receipt-event:` |
| `OpsHistoryContextPackRef.json` | OpsHistoryContextPackRef | `urn:srcos:context-pack:` |
| `RedactionTombstone.json` | RedactionTombstone | `urn:srcos:redaction-tombstone:` |

## Example additions

| File | Schema type | Description |
| --- | --- | --- |
| `ops-history-event.json` | OpsHistoryEvent | Bounded agent handoff event with summary payload mode and policy/evidence refs. |
| `ops-history-sync-policy.json` | OpsHistorySyncPolicy | Topology-aware local-first propagation policy with redaction-priority lane. |
| `local-first-service-manifest.json` | LocalFirstServiceManifest | `ops-historyd` user service manifest with D-Bus endpoints, durable store, subscription posture, and redaction priority. |
| `bearhistory-event.json` | BearHistoryEvent | BearBrowser agent-runtime navigation metadata with profile-boundary assertions. |
| `bearhistory-sync-policy.json` | BearHistorySyncPolicy | Human-secure deny-by-default and agent-runtime policy-gated browser sync/export posture. |
| `shell-receipt-event.json` | ShellReceiptEvent | Metadata-only operational receipt with content capture disabled by default. |
| `ops-history-context-pack-ref.json` | OpsHistoryContextPackRef | Bounded context-pack reference for Memory Mesh and AgentPlane handoff. |
| `redaction-tombstone.json` | RedactionTombstone | Critical-priority invalidation object for context, memory, artifact, and replica cleanup. |

## Validation

Run:

```bash
make validate-ops-history-examples
```

or:

```bash
python3 tools/validate_ops_history_examples.py
```

The root `make validate` target includes the OpsHistory validator.

## Consumer repos

The intended first consumers are:

- `SourceOS-Linux/agent-term`
- `SourceOS-Linux/BearBrowser`
- `SourceOS-Linux/sourceos-shell`
- `SocioProphet/memory-mesh`
- `SocioProphet/policy-fabric`
- `SocioProphet/agent-registry`
- `SocioProphet/agentplane`

## Contract discipline

These contracts are safe-default scaffolds. They do not authorize live sync, browser export, memory writeback, bridge/export, artifact exposure, or agent context hydration by themselves. Those actions require Policy Fabric decisions and Agent Registry authority.
