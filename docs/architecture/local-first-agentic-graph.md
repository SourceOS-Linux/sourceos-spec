# Local-First Agentic Graph Architecture

Status: draft
Spec family: SourceOS/SociOS contract layer
Primary owners: SourceOS core, Policy Fabric, Agent Registry, Memory Mesh, Prophet Workspace

## Purpose

SourceOS and the SociOS agent plane require a governed, encrypted, local-first, agent-aware graph substrate. The goal is not ordinary settings sync. The goal is to let the trusted computing environment move across devices, workspaces, repos, agents, terminals, browsers, relays, and organizations without losing local authority.

## Design thesis

SourceOS should sync the whole trusted computing environment as a governed local-first graph.

This means:

- Developer and workspace environment state is product surface.
- Sync is decomposed by engine, not implemented as one opaque blob replicator.
- Agent settings are execution policy, not ordinary configuration.
- Memory is governed graph state, not automatic durable truth.
- Relays transport signed/encrypted objects; relays are not authority.
- Secrets are never ordinary graph values.
- Every privileged bridge must be origin-bound, scope-bound, signed, auditable, revocable, and policy checked.

## Core layers

### SourceIdentity

Owns user, device, workspace, organization, repo, agent, relay, and model/provider identities. It issues signing keys, device records, scoped tokens, workspace keys, organization policy authority keys, and agent identity references.

Agents never own root identity. Agents request scoped capabilities from SourceIdentity and SourcePolicy.

### SourceGraph

The canonical typed graph substrate. SourceGraph stores nodes and edges for users, devices, repos, workspaces, agents, tools, memories, policies, terminal sessions, browser sessions, models, relays, artifacts, tasks, and audit events.

Every node and edge carries an ID, schema version, owner, author, origin device, workspace scope, policy domain, encryption scope, timestamp, causal metadata, signature, and audit pointer.

### SourceStore

The local durable state layer. It must work offline, support encrypted collections, tombstones, local indexes, schema migration, sync cursors, and policy-aware read/write APIs.

### SourceSync

The engine registry, scheduler, and relay protocol. SourceSync includes SyncSupervisor, SyncEngineRegistry, per-domain SyncEngine implementations, SyncTrackers, SyncMirrors, SourceRelay transport, and a Conflict Workbench.

### SourcePolicy

The policy evaluation and enforcement layer. It evaluates device policy, user policy, workspace policy, repo policy, enterprise policy, agent policy, model policy, network/firewall policy, and compliance policy.

Precedence rule: stronger safety, enterprise, repo, and local policy wins. Remote policy cannot silently weaken a local or enterprise restriction.

### SourceChannel

The secure bridge between UI, web, terminal, browser, MCP, local daemons, and agent runtimes. SourceChannel requests are origin-bound, profile-bound, workspace-bound, capability-bound, signed, auditable, revocable, replay-protected, and human-readable.

No surface is trusted merely because it runs on localhost.

### SourceAudit

Append-only operational memory. SourceAudit records graph writes, sync decisions, policy decisions, agent grants, tool execution, memory proposal/promotion/revocation, shell profile changes, browser bridge calls, model route changes, remote commands, and conflict resolution.

Sherlock and Holmes consume SourceAudit to explain why a state transition happened.

## Canonical graph objects

- User
- Device
- Organization
- Workspace
- Repo
- Agent
- Tool
- CapabilityLease
- PolicyBundle
- PolicyDecision
- MemoryObject
- TerminalSession
- ShellProfile
- BrowserSession
- ModelProvider
- SecretRef
- RelayPeer
- Artifact
- Task
- AuditEvent

## Canonical sync engines

- sourceos.sync.clients
- sourceos.sync.workspace
- sourceos.sync.shell
- sourceos.sync.agent-registry
- sourceos.sync.policy-fabric
- sourceos.sync.memory-mesh
- sourceos.sync.browser
- sourceos.sync.secrets
- sourceos.sync.audit
- sourceos.sync.models
- sourceos.sync.extensions

## Merge strategy classes

- crdt: low-risk collaborative state such as presence and cursors
- graph_merge: workspace graph, tasks, artifact references
- append_only: audit and provenance records
- manual_review: memory conflicts, shell profile changes, workspace destructive changes
- strongest_policy_wins: security and enterprise policy
- signed_authority_required: policy bundles, agent trust grants, org controls
- never_merge: raw secrets, private keys, device keys, credential material
- quarantine: unknown schemas, unsigned agent instructions, unexpected remote writes

## Required state machine

Canonical states:

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

Canonical reason codes:

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

## Product integration

- Prophet Workspace is the cockpit for graph state, sync health, policy explanations, memory review, agent capabilities, conflicts, and audit timelines.
- Policy Fabric is the policy authority.
- Agent Registry owns signed manifests, trust tiers, and capability leases.
- Memory Mesh owns proposed, scoped, approved, promoted, synced, expired, and revoked memory states.
- Mesh Rush transports signed and encrypted graph objects without becoming authority.
- TurtleTerm and sourceos-shell own terminal and shell surfaces but request privileges through SourceChannel and Policy Fabric.
- BearBrowser owns browser/workspace state and must enforce personal, workspace, and enterprise profile boundaries.
- Sherlock/Holmes explain decisions, diff graph state, inspect quarantine, and surface suspicious mutations.

## Acceptance criteria

1. Every implementation repo declares its SourceOS ownership through `.sourceos/manifest.json`.
2. Every sync engine has a manifest, schema version, merge rule, policy class, encryption scope, and audit model.
3. Every agent capability is represented as a scoped, expiring, revocable lease.
4. Memory has a proposal/review/promote lifecycle and cannot silently globalize.
5. Shell profile changes and executable sync objects require policy review.
6. Secrets sync only as references or vault-backed leases.
7. SourceChannel mediates all privileged UI/web/local/agent bridges.
8. Sherlock can explain accepted, rejected, merged, quarantined, and downgraded graph writes.
