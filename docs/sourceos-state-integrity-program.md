# SourceOS State Integrity Implementation Program

## Decision: Implementation Home

**`SourceOS-Linux/sourceos-syncd`** is the implementation home for the SourceOS State Integrity daemon (`sourceos-syncd`). The repo exists and is seeded. MVP scope is locked below.

## What This Is

Not commodity file sync. The local-first state integrity layer: provenance, repair, profile isolation, policy-governed replication, and agent-operable state. Every object the SourceOS estate manages — files, packages, configs, models, agent sessions, boot profiles — has a record that answers the ten questions below. No object is mutable by model inference alone.

## The Ten Questions Every Object Must Answer

1. What is this object? (identity + schema)
2. Which schema governs it? (schema registry)
3. Who or what last changed it? (actor registry + provenance)
4. Which device and profile own it? (device identity + enrollment profile)
5. Is it safe to sync? (conflict record + stale-state record)
6. Why is it blocked? (policy decision + diagnostic record)
7. What conflicts exist? (sync conflict record)
8. What can be repaired automatically? (repair plan, autoRepairEligible)
9. What requires human review? (repair plan, requiresHumanReview)
10. What data is durable vs rebuildable? (durability classification)

## MVP Scope (locked)

The MVP can be declared done when it can answer all ten questions for at least one file object and one agent actor path from structured state (not filesystem scan).

### MVP Object Model
- **LocalObjectRecord**: id, schemaRef, actorRef, deviceRef, durabilityClass, syncPolicy, stalenessRisk
- **ActorRecord**: id, kind (human | agent | daemon | ci), identityRef, sessionRef
- **SchemaRecord**: id, $id (JSON Schema), version, governingPolicy
- **LocalEventLog**: append-only JSONL, one entry per mutation, keyed by objectId + actorId + timestamp
- **ConflictRecord**: uses `SyncConflictRecord` from sourceos-spec
- **RepairPlan**: id, objectRef, steps[], autoRepairEligible, requiresHumanReview

### MVP CLI Surface
```
sourceos-syncd status          # overall estate health
sourceos-syncd doctor          # per-object staleness report
sourceos-syncd object <id>     # answer the ten questions for one object
sourceos-syncd repair <id>     # execute autoRepairEligible repair plans
sourceos-syncd log <id>        # show append-only event log for one object
```

### MVP Adapters (one each)
- **File/workspace object adapter**: index a file under `~/.sourceos/objects/`
- **Agent actor path**: record agent session mutations via `AgentSession` + `ProvenanceRecord`

### MVP Policy Hook (one)
- On mutation attempt: check `ExactnessArtifactRecord.admissionPolicy`; if `verifier-required`, demand a `ValidatorReceipt` before committing

### MVP Conflict Type (one)
- `checksum-mismatch` on a local file — detected on read, resolved by re-download or user review

### MVP Repair Path (one)
- Derived index corruption: re-index from source file, emit `StaleStateRecord` with `autoRepairEligible: true`, execute repair, emit `ValidatorReceipt`

### MVP Observability
- Emit `OpsHistoryEvent` on every state transition
- Emit `DiagnosticStormRecord` on repeated failures (> 3 in 60s window)

### MVP Status Surfaces
- `SourceOS-Linux/TurtleTerm`: show per-object status in agent reliability session monitor
- `SourceOS-Linux/sourceos-shell`: `sourceosctl status` reads from `sourceos-syncd status`

## Lane Ownership

| Lane | Repo |
|---|---|
| Boot integrity | `SourceOS-Linux/sourceos-boot` |
| Developer tooling | `SourceOS-Linux/sourceos-devtools` |
| Workspace surface | `SocioProphet/sourceos-workspace` |
| Agent plane | `SocioProphet/agentplane` |
| Policy | `SocioProphet/policy-fabric` |
| Memory | `SocioProphet/memory-mesh` |
| Cloud/fog shell | `SocioProphet/cloudshell-fog` |
| Terminal | `SourceOS-Linux/TurtleTerm` |
| Observability | `SourceOS-Linux/sourceos-syncd` |
| Model artifacts | `SourceOS-Linux/sourceos-model-carry` |

## Typed Contract References (all in sourceos-spec)

- `StaleStateRecord` — staleness detection
- `ExactnessArtifactRecord` — exactness-sensitive field admission
- `LocalReasoningFailure` — reasoning-derived errors, suppression
- `SyncConflictRecord` — conflict representation
- `SyncCycleReceipt` — sync operation evidence
- `ValidatorReceipt` / `ValidatorDecision` — deterministic verification
- `ProvenanceRecord` — actor + mutation lineage
- `OpsHistoryEvent` — state transition observability
- `DiagnosticStormRecord` — repeated failure suppression
- `AgentCapabilityLease` — agent mutation scope
- `PolicyDecision` — admission gate decisions
- `DeviceIdentity` — per-device object ownership
- `RepairPlan` — (to be added as thin wrapper over existing repair schemas)

## What Is Not MVP

- Multi-device sync (post-MVP)
- Full estate rollout (post-MVP: `sourceos-syncd #2`)
- Noise-budget engine (`sourceos-syncd #8`)
- Operator narrative dashboard (`sourceos-syncd #9`)
- Metadata Coherence Plane epic (`sourceos-syncd #23`)
