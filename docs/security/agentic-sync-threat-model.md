# Agentic Sync Threat Model

Status: draft
Scope: SourceOS local-first graph, sync engines, SourceChannel, agent registry, memory mesh, policy fabric, shell, browser, terminal, and workspace surfaces.

## Security thesis

In an agentic operating environment, synced configuration can become execution control. A remote graph write that changes an agent instruction, shell profile, model route, tool grant, memory object, MCP endpoint, extension state, browser bridge, or policy bundle can directly alter what the system does.

Therefore, agentic sync is a control-plane security boundary, not convenience replication.

## Primary assets

- User identity and device identity
- Workspace graph state
- Agent manifests and capability leases
- Policy bundles and policy decisions
- Memory objects and memory provenance
- Shell profiles, aliases, environment templates, and command templates
- Browser workspace sessions and extension metadata
- Model/provider routing preferences
- Secret references and vault leases
- Audit events and provenance records
- Relay peer identities
- SourceChannel bridge envelopes

## Threat actors

- Malicious remote relay
- Compromised user device
- Compromised enterprise profile
- Malicious browser extension
- Malicious workspace web app
- Malicious or confused agent
- Poisoned memory source
- Malicious repo dependency
- Malicious MCP server
- Network attacker
- Insider with partial repo or policy access
- Stale device replaying old graph writes

## Threats and controls

### Remote graph poisoning

Threat: an attacker submits graph objects that alter agent, memory, policy, shell, browser, or model state.

Controls:

- Require signatures on graph writes.
- Validate schema version and collection ownership.
- Quarantine unknown schemas and unsigned writes.
- Enforce per-engine policy classes.
- Require manual review for dangerous merge classes.
- Emit audit events for accepted, rejected, and quarantined writes.

### Agent capability escalation

Threat: an agent gains tool, model, memory, shell, network, or MCP access through synced configuration.

Controls:

- Represent every privilege as an expiring capability lease.
- Bind leases to agent ID, workspace ID, tool scope, policy bundle hash, and grantor.
- Deny leases without a valid policy decision and audit pointer.
- Revoke leases through SourcePolicy and Agent Registry.
- Never trust agent self-declared capabilities without registry validation.

### Memory injection

Threat: remote or agent-generated memory silently changes long-term behavior.

Controls:

- Use lifecycle states: observed, proposed, scoped, approved, promoted, synced, expired, revoked.
- Require provenance, confidence, sensitivity, retention, mutability, and scope.
- Default agent writes to proposed memory only.
- Require review for global or cross-profile memory promotion.
- Quarantine memory from untrusted agents, browser surfaces, and unknown relays.

### Shell profile injection

Threat: synced shell aliases, functions, PATH changes, env templates, or startup scripts execute attacker-controlled commands.

Controls:

- Treat shell profile sync as high-risk.
- Block raw shell history sync by default.
- Redact secret-bearing environment state.
- Require policy review for executable shell profile changes.
- Emit SourceAudit events for every profile change.
- Make TurtleTerm and sourceos-shell request changes through SourceChannel.

### Browser-to-local bridge abuse

Threat: a web origin, browser extension, or workspace UI controls local agents or shell through a localhost bridge.

Controls:

- Use SourceChannel envelopes for every privileged bridge request.
- Bind requests to origin, profile, workspace, capability, nonce, expiry, and policy bundle hash.
- Deny raw localhost trust.
- Require explicit capability grants for browser-to-agent and browser-to-shell paths.
- Audit every accepted and denied bridge call.

### Policy downgrade

Threat: remote policy weakens local, enterprise, repo, or safety controls.

Controls:

- Stronger policy wins.
- Enterprise restrictions beat personal convenience inside enterprise profiles.
- Local safety floor cannot be weakened remotely.
- Repo policy beats agent preference.
- Unsigned policy bundles are ignored or quarantined.
- Policy downgrade requires signed authority and audit visibility.

### Secret leakage

Threat: secrets are synced as ordinary graph state or leaked through command history, environment snapshots, memory, logs, or browser state.

Controls:

- Never store raw tokens, private keys, or passwords as SourceGraph values.
- Use SecretRef and vault-backed capability leases.
- Redact secret-bearing environment state.
- Block raw shell history sync by default.
- Mark secret references as never_merge.
- Audit secret lease issuance and revocation.

### Relay compromise

Threat: a sync relay observes, mutates, drops, replays, or reorders graph objects.

Controls:

- Encrypt payloads by profile, workspace, org, or device scope.
- Sign all graph objects.
- Use nonce, causal metadata, tombstones, and replay protection.
- Treat relay identity as transport metadata, not authority.
- Allow local-only operation when relay trust is insufficient.

### Model/provider route manipulation

Threat: synced model routing moves execution from local/private models to remote providers, or from approved providers to unapproved providers.

Controls:

- Treat model provider enablement as policy-controlled.
- Bind model route changes to policy decisions.
- Require approval for remote provider enablement in sensitive profiles.
- Audit route changes and provider decisions.
- Support local-only mode and enterprise firewall profiles.

### Audit tampering

Threat: attackers erase or rewrite audit records.

Controls:

- SourceAudit is append-only.
- Deletion is handled through retention policy, not ordinary mutation.
- Audit records should include hash-linked provenance where supported.
- Sherlock/Holmes must surface gaps, invalid chains, and rejected audit writes.

## Required security classifications

Low risk:

- View layout
- Presence
- Cursors
- Non-executable UI preferences

Medium risk:

- Workspace graph references
- Task metadata
- Artifact metadata
- Browser workspace sessions

High risk:

- Agent manifests
- Memory objects
- Shell profiles
- Model routing
- Extension enablement
- MCP server definitions

Critical risk:

- Policy bundles
- Capability leases
- Secret references
- Device keys
- Org keys
- Cross-device commands
- Wipe or replace commands

## Required audit events

- graph.write.accepted
- graph.write.rejected
- graph.write.quarantined
- sync.engine.started
- sync.engine.completed
- sync.conflict.detected
- sync.conflict.resolved
- policy.decision.allow
- policy.decision.deny
- policy.decision.require_review
- agent.lease.granted
- agent.lease.revoked
- agent.execution.started
- agent.execution.denied
- memory.proposed
- memory.promoted
- memory.revoked
- shell.profile.changed
- browser.bridge.accepted
- browser.bridge.denied
- model.route.changed
- secret.lease.issued
- secret.lease.revoked

## Acceptance criteria

1. Every high-risk and critical-risk sync object has a policy class, merge rule, and audit event.
2. Every privileged bridge path uses SourceChannel.
3. Every agent privilege is represented as a capability lease.
4. Every memory mutation has provenance and lifecycle state.
5. Every policy decision has an explainable reason code.
6. Every relay-originated write can be traced to identity, signature, policy, and audit.
7. Every unsafe merge path has quarantine or review behavior.
