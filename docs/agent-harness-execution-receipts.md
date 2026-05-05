# Agent Harness Execution Receipt Boundary

Status: v0.1 planning baseline  
Owner plane: SourceOS specification / local runtime contracts  
Runtime producers: SourceOS Agent Machine, BearBrowser, TurtleTerm, agent-term, sourceos-shell, workstation contracts  
Consumers: AgentPlane, Policy Fabric, Memory Mesh, SCOPE-D, Delivery Excellence, SocioSphere

## Purpose

The Aden/Hive lessons are not limited to development workflows. They apply to local-first execution, host/runtime admission, browser actions, terminal commands, model carry, credential posture, offline operation, user-space boundaries, and customer-safe proof of work.

SourceOS must define the receipt boundary for governed local execution so every agent harness action can be measured and audited without turning Delivery Excellence into a runtime or Policy Fabric into an implementation repo.

## Boundary

SourceOS spec owns the neutral contract vocabulary for:

- local agent runtime activation
- Agent Machine receipts
- model carry references
- shell and terminal receipts
- browser action receipts
- local-first service manifests
- host mutation boundaries
- network profile and offline/local-only posture
- credential-use evidence
- artifact and download manifests
- replay/reconstruction pointers

SourceOS spec does not own:

- AgentPlane graph execution
- Delivery Excellence scoreboards and KPIs
- Policy Fabric gate decisions
- Memory Mesh recall/writeback runtime
- BearBrowser or TurtleTerm product implementation
- SCOPE-D security exercises

## Required receipt family

### LocalAgentRuntimeReceipt

Records local agent runtime activation and execution posture.

Required semantics:

- receipt id
- runtime profile
- agent identity ref
- policy admission ref
- activation decision ref
- model carry refs
- memory mount refs
- network profile
- filesystem scopes
- secret scopes
- host mutation policy
- started/stopped timestamps
- exit state
- AgentPlane run/session refs

### ShellReceiptEvent

Records a terminal or shell action.

Required semantics:

- command id
- command hash
- working directory
- actor/agent ref
- environment profile
- stdin/stdout/stderr pointers
- exit code
- file mutation summary
- policy decision ref
- replay eligibility

### BrowserActionReceipt

Records a browser action through BearBrowser or compatible governed browser surface.

Required semantics:

- browser session ref
- URL/domain
- action type
- credential-use flag
- upload/download refs
- screenshot or DOM/action pointer
- policy decision ref
- side-effect class
- replay/simulation eligibility

### ModelCarryRouteReceipt

Records local/cloud model routing used by a local runtime.

Required semantics:

- model profile ref
- provider ref
- residency class
- privacy class
- route decision ref
- fallback behavior
- cost class
- policy decision ref
- prompt/output hash refs when policy permits

### HostMutationBoundaryReceipt

Records whether a run attempted or performed host mutation.

Required semantics:

- mutation class
- target scope
- dry-run/live-run mode
- approval ref
- policy decision ref
- rollback ref
- mutated host flag
- denied operation refs

### DownloadArtifactReceipt

Records downloads or generated files produced by browser, terminal, or agent runtime surfaces.

Required semantics:

- artifact ref
- source URL or producer ref
- sha256
- media type
- size
- quarantine state
- scan refs
- retention class
- Memory Mesh artifact pointer ref

## Delivery Excellence projection

Delivery Excellence consumes only derived metrics/readouts unless the relevant evidence is explicitly approved for broader visibility.

Projection examples:

- local runtime activation success/failure
- shell command success/failure
- browser action success/failure
- host mutation denied/approved/performed
- credential-use event count
- offline/local-only compliance
- artifact quarantine count
- replay eligibility count
- policy-blocked action count
- customer-safe proof of work

## Policy Fabric integration

Every local execution receipt should be able to cite policy decisions for:

- runtime admission
- network profile
- filesystem scope
- secret scope
- model route
- browser side effect
- terminal side effect
- host mutation
- artifact retention
- credential use

Fail closed when controlled actions lack a required policy decision ref.

## AgentPlane integration

AgentPlane should reference SourceOS receipts in `EvidencePack`, `RunArtifact`, `ReplayArtifact`, `SessionEnvelope`, and `PromotionGate` artifacts.

Receipts are not merely logs. They are replay/proof inputs that can be sealed, hashed, redacted, and projected into Delivery Excellence metrics.

## Memory Mesh integration

Large outputs, browser screenshots, DOM captures, terminal transcripts, downloads, generated artifacts, and redacted payloads should be moved behind Memory Mesh `ArtifactPointer` refs whenever they exceed policy or size thresholds.

## SCOPE-D integration

SCOPE-D should validate these receipt classes for:

- malicious command injection
- browser automation abuse
- credential exfiltration
- artifact spoofing
- download quarantine bypass
- local service exposure
- host mutation bypass
- memory poisoning through local receipts

## Non-negotiables

- Host mutation must be explicit and policy-referenced.
- Browser and terminal side effects require receipts.
- Credential use is a first-class evidence event.
- Offline/local-only mode must be provable.
- Artifact pointers must be digest-addressed.
- Delivery Excellence receives controlled projections, not raw secrets or uncontrolled logs.
- Customer-safe readouts must not expose raw local telemetry without redaction and policy approval.

## Initial implementation path

1. Add schemas/examples for `LocalAgentRuntimeReceipt`, `BrowserActionReceipt`, `HostMutationBoundaryReceipt`, and `DownloadArtifactReceipt`.
2. Align existing `ShellReceiptEvent`, `AgentMachineReceipt`, model carry, OpsHistory, and BearHistory schemas to this boundary.
3. Require AgentPlane evidence packs to cite SourceOS receipt refs for local execution.
4. Require Delivery Excellence projections for local execution success, host mutation posture, credential-use counts, and replay eligibility.
5. Require SCOPE-D synthetic checks for browser/terminal/host-mutation abuse cases.
