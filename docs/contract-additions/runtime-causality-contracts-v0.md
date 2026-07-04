# Runtime Causality Contracts v0

This additive contract slice introduces runtime-causality records derived from ordered diagnostic evidence. The goal is to collapse opaque operating-system log storms into typed, bounded, user-explainable evidence objects.

The slice now covers both first-pass runtime signals and second-pass causality envelopes: retry loops, security verdict availability, layered network truth, browser launch transactions, runtime identity graphs, desktop-service broker state, maintenance epochs, registry integrity, boot/session phase gates, and diagnostic-storm summaries.

## Added schemas

| File | Type | URN prefix | Purpose |
|---|---|---|---|
| `schemas/RetryLoopFingerprint.json` | `RetryLoopFingerprint` | `urn:srcos:retry-loop:` | Summarize repeated runtime failures with count, cadence, retry class, terminal state, policy validity, and remediation. |
| `schemas/SecurityVerdictState.json` | `SecurityVerdictState` | `urn:srcos:security-verdict:` | Represent security decision availability, including degraded states such as no verdict provider, invalid provider, unavailable policy, or insufficient evidence. |
| `schemas/NetworkTruthState.json` | `NetworkTruthState` | `urn:srcos:network-truth:` | Preserve layered connectivity truth instead of reducing network state to online/offline. |
| `schemas/BrowserLaunchTransaction.json` | `BrowserLaunchTransaction` | `urn:srcos:browser-launch-transaction:` | Model browser launch as a preflight transaction before WebContent/GPU/Networking child processes are allowed to spawn. |
| `schemas/RuntimeIdentityGraph.json` | `RuntimeIdentityGraph` | `urn:srcos:runtime-identity-graph:` | Connect app, helper, broker, package, executable, audit-token, profile, and session identity observations. |
| `schemas/DesktopServiceBrokerState.json` | `DesktopServiceBrokerState` | `urn:srcos:desktop-service-broker-state:` | Represent broker availability for pasteboard, launcher, core-services, file-provider, notification, extension-registry, intents, network-settings, credential, and URL-opening surfaces. |
| `schemas/MaintenanceEpoch.json` | `MaintenanceEpoch` | `urn:srcos:maintenance-epoch:` | Bound cleanup, cache-delete, indexing, backup, plugin-scan, cloud-purge, experiment-refresh, and registry-sweep maintenance work. |
| `schemas/RuntimeRegistryIntegrityRecord.json` | `RuntimeRegistryIntegrityRecord` | `urn:srcos:runtime-registry-integrity:` | Describe package receipt, extension record, broker record, manifest, launch-record, profile, and namespace-descriptor integrity. |
| `schemas/BootSessionPhaseState.json` | `BootSessionPhaseState` | `urn:srcos:boot-session-phase:` | Gate services by sealed boot, pre-login, post-login locked, unlocked user session, degraded session, or recovery session. |
| `schemas/DiagnosticStormRecord.json` | `DiagnosticStormRecord` | `urn:srcos:diagnostic-storm:` | Summarize repeated diagnostic signatures with count, cadence, severity, representative samples, suppression policy, and terminal state. |

## Added examples

| File | Scenario |
|---|---|
| `examples/retry_loop_fingerprint.json` | Full Disk Access/TCC denial loop collapsed into one bounded fingerprint. |
| `examples/security_verdict_state.json` | Network-flow observation where the verdict provider is unavailable. |
| `examples/network_truth_state.json` | Wi-Fi radio active but no association, failed route, and degraded DNS/DHCP observers. |
| `examples/browser_launch_transaction.json` | Browser launch prevented before child-process spawn because broker and extension-registry preflight failed. |
| `examples/runtime_identity_graph.json` | BearBrowser app and WebContent child process identity resolved as a degraded runtime graph. |
| `examples/desktop_service_broker_state.json` | Pasteboard, CoreServices, and extension-registry brokers degraded for browser child-process launch. |
| `examples/maintenance_epoch.json` | deleted/triald registry and experiment sweep bounded as a degraded maintenance epoch. |
| `examples/runtime_registry_integrity_record.json` | LaunchServices extension-record and treatment namespace-descriptor failures captured as registry-integrity evidence. |
| `examples/boot_session_phase_state.json` | post-login locked session blocks analytics and registry-cleanup components until unlock. |
| `examples/diagnostic_storm_record.json` | triald missing-namespace descriptor storm summarized with count, cadence, and suppression policy. |

## Design intent

The records are designed to support SourceOS doctor flows, browser diagnostics, terminal diagnostics, mesh/network intelligence, and forensic evidence receipts. They intentionally avoid platform-specific names in schema fields while allowing platform-specific event evidence through `evidenceRefs`.

## Observed failure classes covered

- Permission-denied polling loops.
- Security monitors that see flows but cannot attach verdicts.
- Network path ambiguity where radio, route, DNS, DHCP, captive portal, and internet reachability disagree.
- Browser child-process launch failures caused by missing desktop brokers, invalid registries, or denied service lookups.
- Runtime identity ambiguity across app, child process, helper, audit-token, and package boundaries.
- Background maintenance storms caused by cleanup, registry, experiment, backup, cloud purge, or plugin-scan activity.
- Registry integrity failures involving missing extension records, package receipts, broker records, and namespace descriptors.
- Boot/session phase failures where locked state prevents keyring, analytics, registry, or user-store access.
- Diagnostic storms that need first-seen, last-seen, count, cadence, sample events, suppression policy, terminal state, and remediation.

## Downstream consumers

- SourceOS doctor and workstation health reports.
- BearBrowser launch preflight and child-process attestation.
- TurtleTerm terminal helper preflight and broker checks.
- MeshRush/Meshrush network-truth and peer-path evaluation.
- Prophet Platform evidence receipts and FogStack runtime readiness checks.
- Sociosphere estate-control observability where runtime state must be summarized without losing causality.

## Implementation notes

These schemas are additive. They do not replace `TelemetryEvent`, `PolicyDecision`, `ExecutionDecision`, or `RunRecord`; instead, they summarize and relate those lower-level observations into user-readable runtime-causality records.

The minimum viable runtime flow is:

1. Capture raw telemetry.
2. Normalize repeated signatures into `RetryLoopFingerprint` and `DiagnosticStormRecord`.
3. Attach contextual truth with `NetworkTruthState`, `SecurityVerdictState`, `BootSessionPhaseState`, and `RuntimeRegistryIntegrityRecord`.
4. Gate app launches through `RuntimeIdentityGraph`, `DesktopServiceBrokerState`, and `BrowserLaunchTransaction`.
5. Bound cleanup/indexing/config refresh through `MaintenanceEpoch`.

## Follow-up work

- Add central `schemas/README.md` catalog rows for these ten types.
- Add validation automation that maps schema titles to snake_case examples.
- Add an example storm-log parser that emits these records from ordered logs.
- Wire SourceOS shell, BearBrowser, TurtleTerm, and MeshRush consumers to these contracts.
