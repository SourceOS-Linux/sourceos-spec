# SourceOS Agentic Graph Estate Integration Map

Status: draft
Scope: GitHub estate integration for SourceOS local-first agentic graph foundation.

## Control repo

### SourceOS-Linux/sourceos-spec

Role: canonical architecture and contract source.

Owns:

- Local-first agentic graph architecture
- Sync engine registry
- SourceGraph record model
- SourceChannel contract
- Agentic sync threat model
- Repo manifest contract
- Acceptance criteria

## Shared tooling

### SourceOS-Linux/sourceos-devtools

Role: validator and operator tooling.

Owns:

- JSON Schema validation CLI
- sourceos contract validate
- sourceos repo scan
- sourceos graph doctor
- sourceos sync doctor
- sourceos policy explain
- estate inventory scanner

## SourceOS runtime and product surface

### SourceOS-Linux/sourceos-shell

Role: shell execution and shell sync.

Owns:

- sourceos.sync.shell implementation
- shell profile sync
- command template policy
- environment redaction
- audit events for shell profile changes

### SourceOS-Linux/TurtleTerm

Role: terminal product surface.

Owns:

- terminal UI integration
- pane/session state
- workspace-bound terminal context
- Neovim integration surface
- SourceChannel client integration

### SourceOS-Linux/agent-term

Role: terminal-native agent ChatOps.

Owns:

- Matrix-oriented agent interaction
- slash topic routing
- workspace-context-bound agent sessions
- audit events for chat-driven agent commands

### SourceOS-Linux/agent-machine

Role: local agent runtime.

Owns:

- local agent execution
- capability lease enforcement
- model/provider runtime selection
- local-only mode
- enterprise firewall profile support

### SourceOS-Linux/openclaw

Role: coding-agent compatibility and execution primitives.

Owns:

- coding-agent runtime compatibility
- local code-agent execution primitives
- policy-aware tool use integration

### SourceOS-Linux/BearBrowser

Role: browser/workspace bridge.

Owns:

- sourceos.sync.browser
- workspace-bound browser sessions
- tab/bookmark/session policy
- origin-bound SourceChannel bridge
- extension metadata policy

### SourceOS-Linux/sourceos-boot

Role: bootstrapping and early system integration.

Owns:

- device initialization hooks
- early profile bootstrap contracts
- boot-time policy loading contract

### SourceOS-Linux/sourceos-model-carry

Role: model transport and local/remote model profile integration.

Owns:

- sourceos.sync.models participation
- local model availability metadata
- model/provider routing fixtures

## Socioprophet control plane

### SocioProphet/agent-registry

Role: governed agent registry.

Owns:

- sourceos.sync.agent-registry
- signed agent manifests
- agent identity records
- agent trust tiers
- capability leases
- tool grants
- model compatibility metadata

### SocioProphet/policy-fabric

Role: policy authority.

Owns:

- sourceos.sync.policy-fabric
- policy precedence
- signed policy bundles
- explainable policy decisions
- allow/deny/review/quarantine decisions
- firewall and network profile policy

### SocioProphet/guardrail-fabric

Role: enforcement and safety guardrail layer.

Owns:

- guardrail constraints
- safety floors
- unsafe operation gating
- runtime enforcement support for policy-fabric

### SocioProphet/memory-mesh

Role: governed memory graph.

Owns:

- sourceos.sync.memory-mesh
- memory object lifecycle
- memory provenance
- proposal/review/promotion workflow
- memory quarantine
- memory retention and revocation

### SocioProphet/prophet-workspace

Role: primary workspace cockpit.

Owns:

- workspace graph UI
- sync health panel
- policy explanation panel
- memory review UI
- agent capability panel
- conflict workbench
- audit timeline

### SocioProphet/sourceos-workspace

Role: SourceOS workspace facade or bridge.

Owns:

- workspace bridge contracts
- SourceOS-specific workspace abstractions
- integration with prophet-workspace where required

### SocioProphet/sociosphere

Role: workspace/controller topology.

Owns:

- user/org/workspace/repo/agent topology
- controller relationships
- workspace graph composition

### SocioProphet/meshrush

Role: peer/relay transport.

Owns:

- SourceRelay transport
- peer discovery
- encrypted object transport
- offline queueing
- enterprise relay profiles
- local LAN and homelab sync modes

### SocioProphet/sherlock

Role: observability and investigation.

Owns:

- audit ingestion
- graph diff explanation
- suspicious mutation inspection
- policy and sync explanation surfaces

### SocioProphet/sherlock-search

Role: search over graph, audit, policy, and memory state.

Owns:

- audit/event index
- graph object index
- policy decision search
- memory provenance search

### SocioProphet/google_workspace_mcp

Role: Google Workspace bridge.

Owns:

- workspace connector integration
- SourceChannel-compatible MCP behavior
- policy-aware external document access

## Legacy OS and desktop integration sources

These repos are initial inventory and harvesting targets, not immediate rewrite targets.

- SociOS-Linux/os
- SociOS-Linux/accounts
- SociOS-Linux/settings-daemon
- SociOS-Linux/default-settings
- SociOS-Linux/files
- SociOS-Linux/desktop
- SociOS-Linux/switchboard
- SociOS-Linux/gnome-online-accounts

## Required `.sourceos/manifest.json`

Each primary implementation repo must add a manifest:

```json
{
  "$schema": "https://sourceos-linux.github.io/sourceos-spec/schemas/SourceOSRepoManifest.json",
  "repo": "owner/name",
  "domain": "workspace|agent|policy|memory|shell|browser|os|transport|observability|tooling|spec",
  "ownedSchemas": [],
  "syncEngines": [],
  "sourceChannels": [],
  "policyClasses": [],
  "auditEvents": [],
  "dangerousSurfaces": []
}
```

## M1 required repo manifests

- SourceOS-Linux/sourceos-spec
- SourceOS-Linux/sourceos-devtools
- SourceOS-Linux/sourceos-shell
- SourceOS-Linux/TurtleTerm
- SourceOS-Linux/agent-term
- SourceOS-Linux/agent-machine
- SourceOS-Linux/BearBrowser
- SocioProphet/agent-registry
- SocioProphet/policy-fabric
- SocioProphet/memory-mesh
- SocioProphet/prophet-workspace
- SocioProphet/sociosphere
- SocioProphet/meshrush
- SocioProphet/sherlock

## M1 acceptance criteria

1. All M1 repos declare `.sourceos/manifest.json`.
2. sourceos-devtools can scan manifests and report compliant, partial, missing, or invalid.
3. Each manifest declares sync engines, policy classes, audit events, dangerous surfaces, and owned schemas where applicable.
4. Runtime repos do not merge high-risk sync objects without policy class and audit event definitions.
5. Policy, agent, memory, shell, browser, and transport repos reference this repo as their contract authority.
