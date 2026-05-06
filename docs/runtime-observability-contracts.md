# Runtime observability and capability governance contracts

## Purpose

This contract family adds typed runtime evidence records for SourceOS desktop, browser, terminal, session, and runtime-install flows. The goal is to make effective capability state, assisted browser sessions, workspace classification, session-event recovery, and runtime installation provenance explicit and reviewable.

The family is additive. It does not replace `SessionReceipt`, `AgentMachineReceipt`, `PolicyDecision`, `TelemetryEvent`, or release records. It adds focused evidence surfaces that downstream implementations can emit and validators can check.

## Contract family

| Schema | Type | URN prefix | Primary owner |
|---|---|---|---|
| `schemas/CapabilityLedger.json` | `CapabilityLedger` | `urn:srcos:capability-ledger:` | `SourceOS-Linux/sourceos-shell` |
| `schemas/BrowserAutomationReceipt.json` | `BrowserAutomationReceipt` | `urn:srcos:receipt:browser-automation:` | `SourceOS-Linux/BearBrowser` |
| `schemas/GitWorkspaceState.json` | `GitWorkspaceState` | `urn:srcos:git-workspace-state:` | `SourceOS-Linux/agent-term` |
| `schemas/OrphanEventReceipt.json` | `OrphanEventReceipt` | `urn:srcos:receipt:orphan-event:` | `SocioProphet/sociosphere` |
| `schemas/RuntimeInstallReceipt.json` | `RuntimeInstallReceipt` | `urn:srcos:receipt:runtime-install:` | Agent Machine / runtime installer lane |

## Canonical examples

| Example | Schema | Scenario |
|---|---|---|
| `examples/capabilityledger.json` | `CapabilityLedger` | Browser assistance capability resolves to `enabled` after cross-plane reconciliation. |
| `examples/browserautomationreceipt.json` | `BrowserAutomationReceipt` | User-visible, revocable browser assistance session with policy decision and evidence references. |
| `examples/gitworkspacestate.json` | `GitWorkspaceState` | Passive Git discovery classifies a non-repo directory as an expected negative state. |
| `examples/orphaneventreceipt.json` | `OrphanEventReceipt` | Lifecycle event initially missing session attachment is recovered and linked to a session DAG node before TTL expiry. |
| `examples/runtimeinstallreceipt.json` | `RuntimeInstallReceipt` | Runtime install resolves a manifest, verifies an artifact, emits compact receipt references, and records install success. |

## Trace story

```text
AgentSession
  -> CapabilityLedger
       records effective capability truth after cross-plane reconciliation
  -> BrowserAutomationReceipt
       records owned, visible, scoped, policy-governed browser assistance
  -> GitWorkspaceState
       classifies workspace state before passive or requested Git operations
  -> OrphanEventReceipt
       records recovery or quarantine for lifecycle events without immediate session attachment
  -> RuntimeInstallReceipt
       records runtime manifest resolution, artifact verification, install state, and compact log mode
```

## Design requirements

1. A feature becomes effective only after the capability ledger records a reconciled state.
2. Browser assistance sessions must be visible, owned, scoped, policy-governed, evidence-backed, and revocable.
3. Git discovery must classify workspace state before issuing user-facing remediation.
4. Lifecycle events without immediate session attachment must enter recovery or quarantine.
5. Runtime install logs should emit compact receipt references by default; full manifests belong in evidence bundles.
6. Examples must include non-empty `evidenceRefs`, `policyDecisionRef`, parseable timestamps, and stable URN prefixes.

## Validation

The `validate-runtime-observability-examples` make target runs `tools/validate_runtime_observability_examples.py`. It validates schema conformance plus evidence-discipline invariants:

- unique example IDs
- required URN prefixes
- non-empty `evidenceRefs`
- required `policyDecisionRef`
- parseable timestamps
- no raw path storage in `GitWorkspaceState`
- browser session timestamp ordering
- orphan-event recovery/quarantine consistency
- compact runtime-install log mode in the canonical example

```bash
make validate-runtime-observability-examples
```

## Downstream rollout order

1. Merge the schema/example/validation tranche in `SourceOS-Linux/sourceos-spec`.
2. Implement `BrowserAutomationReceipt` emission and visible session controls in `SourceOS-Linux/BearBrowser`.
3. Implement `GitWorkspaceState` classifier and severity discipline in `SourceOS-Linux/agent-term`.
4. Implement `CapabilityLedger` reconciliation and surface display in `SourceOS-Linux/sourceos-shell`.
5. Implement `OrphanEventReceipt` queue/recovery/quarantine in `SocioProphet/sociosphere`.
6. Implement `RuntimeInstallReceipt` emission in the Agent Machine / runtime installer lane.

## Related issues

- Parent spec: `SourceOS-Linux/sourceos-spec#99`
- Browser implementation: `SourceOS-Linux/BearBrowser#25`
- Terminal implementation: `SourceOS-Linux/agent-term#39`
- Shell implementation: `SourceOS-Linux/sourceos-shell#12`
- Sociosphere implementation: `SocioProphet/sociosphere#283`
