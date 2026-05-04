# SourceOS State Integrity Layer

Status: draft architecture contract
Owner: SourceOS / SocioProphet platform architecture
Implementation target: `SourceOS-Linux/sourceos-syncd` once the repository is created

## Purpose

The SourceOS State Integrity layer is the local-first substrate for durable user, workspace, agent, model, memory, repository, policy, and device state. It is not a commodity drive-sync feature. It is the control plane for local autonomy, provenance, repair, explainability, and policy-governed replication across SourceOS devices, workspaces, agents, and organizations.

The triggering lesson is that hidden sync systems fail poorly when schema, client identity, derived state, and repair semantics are implicit. SourceOS must invert that pattern. All local-first state must be inspectable, typed, repairable, observable, and governed.

## Product Principle

SourceOS state must remain useful offline, safe under concurrent agent/device writes, portable across environments, and explainable under failure. Derived state may be discarded and rebuilt. Durable user and system-of-record state must be preserved, signed where appropriate, and recoverable.

The user-facing product language should avoid exposing `syncd` as the conceptual primitive. Internally the daemon may be named `sourceos-syncd`; externally this capability should surface as SourceOS State, SourceOS Continuity, SourceOS Workspace Integrity, or SourceOS Local Control Plane.

## Architectural Placement

The layer sits below workspace, agents, memory, Git, Matrix, models, and product UI.

```
SourceOS Boot / OS Services
        ↓
sourceos-syncd
        ↓
Local Event Log + Object Store + Schema Registry
        ↓
Policy Fabric / Guardrail Fabric
        ↓
Adapters: Git, Matrix, Drive-like storage, Memory, Models, Workspace, Browser, Agents
        ↓
Surfaces: SourceOS Workspace, SocioSphere, TurtleTerm, Neovim, Agent-Term, Lampstand, Sherlock, Holmes
```

## Core Components

`sourceos-syncd` should own the following modules:

- Actor Registry
- Identity and Device Trust Registry
- Schema Registry
- Object Registry
- Local Event Log
- Object Store
- Sync Planner
- Conflict Engine
- Repair Engine
- Policy Adapter
- Transport Adapter Framework
- Profile Boundary Engine
- Backup / Restore Engine
- Observability API
- Agent Diagnostic API

## Durable vs Rebuildable State

The system must classify state explicitly.

Durable state:

- user documents and workspace objects
- object event history
- signed policy documents
- schema declarations and signed migrations
- memory facts and invalidations
- model artifact metadata and provenance
- identity, device, and actor registrations
- audit and repair reports

Rebuildable state:

- search indexes
- sync plans
- pending queues where derivable from the event log
- projections
- previews
- thumbnails
- agent summaries

Disposable state:

- transient locks
- temporary batches
- ephemeral sessions
- retry scratch state

A corrupted derived index must trigger rebuild, not data reset. A repair operation must state what was modified, preserved, rebuilt, or quarantined.

## Object Model

Minimum first-class object types:

- workspace
- file
- folder
- note
- task
- calendar/event where applicable
- browser session/bookmark/history object where BearBrowser participates
- agent session
- agent patch
- memory fact
- memory invalidation
- policy document
- schema
- schema migration
- device
- identity
- model artifact
- prompt
- eval result
- repository
- branch
- issue
- pull request
- Matrix room reference
- Matrix message reference

Every object should have:

```yaml
object_id: string
object_type: string
schema_version: string
workspace_id: string
profile_id: string
owner_identity: string
created_by_actor: string
last_modified_by_actor: string
created_at: timestamp
updated_at: timestamp
privacy_class: public | personal | work | confidential | regulated | secret
sync_visibility: local_only | profile | workspace | org | public
retention_class: ephemeral | normal | retained | legal_hold
policy_tags: []
provenance: []
content_hash: optional string
state: active | deleted | tombstoned | quarantined | conflicted
```

## Actor Model

Every process that can read, write, sync, repair, migrate, or replicate durable state must register as an actor.

Actor types:

- human
- app
- agent
- device
- service
- import_bridge
- export_bridge
- model_runtime
- remote_relay

Actor fields:

```yaml
actor_id: string
actor_type: human | app | agent | device | service | import_bridge | export_bridge | model_runtime | remote_relay
display_name: string
identity_id: string
workspace_scope: []
profile_scope: []
capabilities:
  - read
  - write
  - delete
  - merge
  - repair
  - migrate_schema
  - export
  - replicate
trust_level: local | user | workspace | org | external | quarantined
policy_subject: string
signing_key_ref: string
created_at: timestamp
revoked_at: optional timestamp
```

Agents must be treated as explicit sync actors, not as anonymous file writers.

## Identity, Keys, and Device Trust

The layer requires explicit identity boundaries:

- user identity
- device identity
- agent identity
- workspace identity
- organization identity
- profile identity

Required capabilities:

- signed writes for privileged actors
- signed schema migrations
- key rotation
- device revocation
- actor revocation
- profile isolation
- workspace membership checks
- remote wipe / local purge when policy permits
- audit trail for key and trust changes

No object may cross profile or organization boundaries without policy approval.

## Profile Boundaries

Profiles are hard state boundaries, not UI filters.

Initial profile classes:

- personal
- work
- client/org-specific
- air-gapped
- lab
- public/open-source

Objects, indexes, model artifacts, memory facts, and agent sessions inherit profile boundaries unless explicitly reclassified through policy.

## Schema Registry

Every local-first object type must have a versioned schema contract.

Schema contracts must include:

- object type
- schema version
- core fields
- extension fields
- field owner
- migration rules
- downgrade behavior
- conflict policy
- tombstone policy
- sync visibility
- encryption classification
- retention classification
- indexing classification

Unknown fields must be preserved when safe, namespaced, and policy-checked. Unknown fields must not silently disappear. Schema drift must produce structured compatibility warnings or quarantine decisions.

Schema migrations must support:

- signed migration manifests
- migration dry-run
- compatibility matrix
- rollback or forward-repair path
- per-client support declarations
- failure report

## Sync Plan Model

Sync plans are first-class objects, not hidden background magic.

```yaml
plan_id: string
source_actor: string
target_actor: string
profile_id: string
workspace_id: string
object_ids: []
operation_class: replicate | import | export | repair | migrate | delete | restore
dependencies: []
policy_decision_ref: string
retry_policy: string
conflict_policy: string
status: planned | blocked | running | failed | completed | cancelled
last_error: optional string
user_explanation: string
created_at: timestamp
updated_at: timestamp
```

The product must be able to answer: why is this object not synced, who modified it, what policy blocked it, and what repair is safe?

## Conflict Model

Conflict semantics are object-specific. There must not be one global merge strategy.

Initial merge drivers:

- files: content hash, chunk tree, rename detection, binary-safe conflict handling
- documents/notes: CRDT or operational event model where appropriate
- Git repositories: Git-native branch and merge semantics
- tasks: field-level merge with status transition validation
- memory facts: append-only facts with invalidation and provenance scoring
- policy documents: signed versions with explicit promotion gates
- model artifacts: content-addressed, metadata-merged, license-aware
- Matrix references: immutable external reference plus local annotation model
- browser state: source-aware history/bookmark/session merge

Agent writes should be reviewable as object transactions:

- draft object changes
- agent-owned branches or object branches
- proposed patches
- human approval gates
- merge queue
- rollback
- attribution

## Deletion and Retention

Deletion must be explicit and policy-aware.

Supported states:

- soft delete
- hard delete
- tombstone
- retention hold
- legal hold
- memory invalidation
- remote wipe
- per-device purge

Deletes must carry actor, policy, timestamp, target scope, and restoration semantics.

## Repair Model

Repair must be staged and auditable.

Required sequence:

1. detect
2. classify
3. snapshot
4. isolate or quarantine
5. rebuild derived state
6. reconcile with durable event log
7. produce repair report
8. resume eligible sync plans

A repair report must state:

- what failed
- affected objects
- affected actors
- what was preserved
- what was rebuilt
- what was quarantined
- unresolved conflicts
- policy decisions
- next user action, if any

User-facing example:

```
Workspace index was corrupted.
User data was not modified.
Rebuilt 18,422 index entries from the local event log.
Replanned 37 pending sync operations.
3 conflicts require review.
Repair report saved.
```

## Policy Integration

`sourceos-syncd` must use Policy Fabric and Guardrail Fabric before sensitive state changes.

Policy questions:

- Can this actor read this object?
- Can this actor write this object?
- Can this actor delete this object?
- Can this object leave this device?
- Can this object sync to this workspace, org, or remote?
- Can this field be indexed?
- Can this memory become durable?
- Can this model artifact be shared?
- Can this schema migration apply?
- Can this repair operation modify durable state?

Policy denials must be structured events, not opaque errors.

## Network, Mesh, and Enterprise Firewall Modes

The transport layer must support:

- local-only mode
- LAN mode
- personal relay mode
- corporate relay mode
- VPN mode
- firewall-constrained mode
- zero-trust mode
- air-gapped export/import
- rclone/WebDAV-style bridge mode where appropriate

State replication must be profile-aware and policy-bounded. Transport availability must never imply permission.

## Backup, Restore, and Disaster Recovery

Required capabilities:

- local snapshots
- object-level restore
- workspace restore
- profile restore
- signed repair reports
- export bundles
- encrypted off-device backup
- cold backup
- verifiable restore test

A restore path is not complete until it can be tested and produce an integrity report.

## Import / Export Bridges

Compatibility bridges should help users migrate from incumbent systems without making those systems authoritative.

Initial bridge targets:

- Google Drive
- iCloud Drive
- OneDrive
- Dropbox
- Notion
- WebDAV
- rclone-compatible remotes
- Git-backed workspace export
- local archive bundles

Bridge actors must be registered, scoped, policy-controlled, and auditable.

## Observability Events

Structured event names:

- `sync.actor.registered`
- `sync.actor.revoked`
- `sync.device.registered`
- `sync.device.revoked`
- `sync.schema.registered`
- `sync.schema.migrated`
- `sync.object.created`
- `sync.object.changed`
- `sync.object.deleted`
- `sync.object.tombstoned`
- `sync.plan.created`
- `sync.plan.started`
- `sync.plan.blocked`
- `sync.plan.failed`
- `sync.plan.completed`
- `sync.conflict.created`
- `sync.conflict.resolved`
- `sync.repair.started`
- `sync.repair.completed`
- `sync.policy.denied`
- `sync.profile.boundary_violation`
- `sync.transport.unavailable`

Sherlock indexes these events. Holmes reasons over causality. Lampstand visualizes health, lineage, warnings, policy posture, and repair reports.

## OS Integration

Linux-first implementation requirements:

- systemd user and system service support
- D-Bus API
- XDG portal hooks where appropriate
- inotify/fanotify watchers
- optional FUSE or virtfs layer where appropriate
- keyring integration
- polkit authorization for privileged operations
- journald structured logs
- desktop notification bridge
- CLI-first operation through `sourceos-devtools`

## CLI Contract

Initial CLI surface:

```bash
sourceos sync status
sourceos sync doctor
sourceos sync explain <object>
sourceos sync plans
sourceos sync actors
sourceos sync schemas
sourceos sync conflicts
sourceos sync repair --dry-run
sourceos sync repair --apply
sourceos sync profiles
sourceos sync devices
sourceos sync export <workspace|profile|object>
sourceos sync import <bundle>
```

The CLI must be safe-by-default. Destructive operations require explicit target scope and dry-run output.

## Product Surfaces

Required surfaces:

- SourceOS Workspace: sync health, conflict inbox, provenance, repair reports
- SocioSphere: object graph, workspace/world controller, people/agents/devices/tasks/files/memory composition
- TurtleTerm: terminal-native state health, policy blocks, agent patch state, repair commands
- Neovim: local sync state, agent patch review, conflict resolution, memory lookup, policy warnings
- Agent-Term: ChatOps for sync events, conflicts, repairs, and agent write review
- Lampstand: observability, lineage, repair visualizations, posture dashboards
- Sherlock: searchable evidence feed for state and sync events
- Holmes: causal reasoning over state failures, conflicts, and repair plans

## Repository Integration Targets

Canonical spec:

- `SourceOS-Linux/sourceos-spec`

Implementation:

- `SourceOS-Linux/sourceos-syncd` once created

Boot and developer surfaces:

- `SourceOS-Linux/sourceos-boot`
- `SourceOS-Linux/sourceos-devtools`
- `SourceOS-Linux/sourceos-shell`
- `SourceOS-Linux/TurtleTerm`
- Neovim integration repo or package to be established

Workspace and product surfaces:

- `SocioProphet/sourceos-workspace`
- `SocioProphet/sociosphere`
- `SocioProphet/cloudshell-fog`

Agent plane:

- `SocioProphet/agentplane`
- `SocioProphet/agent-registry`
- `SourceOS-Linux/agent-machine`
- `SourceOS-Linux/agent-term`

Policy and guardrails:

- `SocioProphet/policy-fabric`
- `SocioProphet/guardrail-fabric`
- `SocioProphet/prophet-core-policy`

Memory:

- `SocioProphet/memory-mesh`
- `SocioProphet/mem0`
- `SocioProphet/supermemory`
- `SocioProphet/supermemory-mcp`

Diagnostics and observability:

- `SocioProphet/sherlock`
- `SocioProphet/sherlock-search`
- `SocioProphet/holmes`
- `SocioProphet/lampstand`

Models and artifacts:

- `SourceOS-Linux/sourceos-model-carry`
- `SocioProphet/model-router`
- `SocioProphet/hermes-agent`

## MVP Cut

The first implementation cut should prove state integrity rather than full cloud-drive parity.

MVP requirements:

1. local object registry
2. actor registry
3. schema registry
4. append-only local event log
5. status and doctor CLI
6. one file/workspace object adapter
7. one agent actor path
8. one policy decision hook
9. one conflict type
10. one repair path for derived index corruption
11. structured observability events
12. basic SourceOS Workspace and TurtleTerm status surfaces

## Acceptance Criteria

The system is not acceptable until it can answer these questions from structured state:

- What is this object?
- Which schema governs it?
- Who or what last changed it?
- Which device and profile own it?
- Is it safe to sync?
- Why is it blocked?
- What conflicts exist?
- What can be repaired automatically?
- What requires human review?
- What data is durable vs rebuildable?
- Can we prove restore integrity?

## Strategic Thesis

This layer is the difference between another cloud-drive clone and a credible local-first operating system. SourceOS should make local state trustworthy by default: durable, explainable, repairable, portable, profile-aware, policy-governed, and agent-operable.
