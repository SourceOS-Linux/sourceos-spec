# SourceChannel Bridge Contract

Status: draft
Scope: privileged bridge between SourceOS UI, browser, terminal, shell, MCP, agents, local daemons, and enterprise/workspace consoles.

## Purpose

SourceChannel is the mandatory bridge contract for privileged communication between product surfaces and local or remote authority-bearing services.

It exists because browser UIs, workspace UIs, terminal UIs, MCP servers, extensions, and local web apps must not receive ambient authority merely because they run locally or are presented inside a trusted product.

No surface is trusted because it can reach `localhost`. No web origin controls agents directly. No terminal UI bypasses policy. No MCP server receives secrets or tool access without a scoped capability lease.

## Required envelope

```json
{
  "$schema": "https://sourceos-linux.github.io/sourceos-spec/schemas/SourceChannelEnvelope.json",
  "channelId": "urn:srcos:channel:example",
  "requestId": "urn:srcos:request:example",
  "origin": "https://workspace.example",
  "surface": "prophet-workspace",
  "profileId": "urn:srcos:profile:user",
  "workspaceId": "urn:srcos:workspace:example",
  "deviceId": "urn:srcos:device:example",
  "agentId": "urn:srcos:agent:example",
  "capability": "agent.execute.tool",
  "scope": {
    "repo": "owner/name",
    "paths": [],
    "tools": [],
    "memoryScopes": []
  },
  "policyBundleHash": "sha256:example",
  "nonce": "example-nonce",
  "issuedAt": "2026-05-04T00:00:00Z",
  "expiresAt": "2026-05-04T00:05:00Z",
  "reason": "Human-readable reason for this privileged request.",
  "auditId": "urn:srcos:audit:example",
  "signature": "base64url-signature"
}
```

## Surfaces

- prophet-workspace
- turtleterm
- bearbrowser
- agent-term
- mcp
- daemon
- admin-console

## Capability classes

Low-risk:

- graph.read.metadata
- workspace.view.status
- sync.read.health

Medium-risk:

- workspace.update.layout
- browser.update.workspace_session
- memory.propose

High-risk:

- agent.execute.tool
- shell.update.profile
- model.route.update
- browser.bridge.agent
- extension.enable

Critical-risk:

- policy.bundle.update
- agent.lease.grant
- secret.lease.issue
- device.command.remote
- sync.collection.wipe
- workspace.replace.local

## Required policy behavior

1. SourceChannel requests are denied by default.
2. A request must be validated before policy evaluation.
3. Policy evaluation must happen before execution.
4. A valid envelope does not imply permission.
5. A valid policy decision must reference a policy bundle hash and reason code.
6. High-risk and critical-risk requests must emit audit events whether allowed or denied.
7. Critical-risk requests must be signed by an authority recognized for the relevant profile, workspace, org, or device.

## Replay and expiry

- Every request requires a nonce.
- Nonces must be single-use within their profile/workspace/device scope.
- Expired requests are denied.
- Replayed requests are denied and audited.
- Stale policyBundleHash values require policy refresh or denial.

## Required audit events

- sourcechannel.request.received
- sourcechannel.request.validated
- sourcechannel.request.rejected
- sourcechannel.policy.allow
- sourcechannel.policy.deny
- sourcechannel.policy.require_review
- sourcechannel.execution.started
- sourcechannel.execution.completed
- sourcechannel.execution.failed
- sourcechannel.replay.denied
- sourcechannel.expired.denied

## Dangerous anti-patterns

- Trusting localhost as authority
- Letting browser JavaScript call agent runtimes directly
- Letting terminal UI mutate shell startup files without policy review
- Letting MCP servers inherit all local tools
- Letting workspace UI issue persistent memory writes directly
- Letting extension state sync without policy class and audit
- Letting enterprise admin surfaces inspect personal local-first data by default

## Acceptance criteria

1. Every privileged surface uses SourceChannel for high-risk and critical-risk operations.
2. Every SourceChannel request has origin, profile, workspace, device, capability, nonce, expiry, policy hash, reason, audit pointer, and signature.
3. Every high-risk and critical-risk operation has a PolicyDecision.
4. Every denied request emits an audit event with reason code.
5. No product surface is trusted solely because it runs locally.
6. No web origin communicates directly with agent, shell, secret, model, or policy services without SourceChannel.
