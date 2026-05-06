# Runtime Causality Contracts v0

This additive contract slice introduces first-pass runtime-causality records derived from ordered diagnostic evidence. The goal is to collapse opaque operating-system log storms into typed, bounded, user-explainable evidence objects.

## Added schemas

| File | Type | URN prefix | Purpose |
|---|---|---|---|
| `schemas/RetryLoopFingerprint.json` | `RetryLoopFingerprint` | `urn:srcos:retry-loop:` | Summarize repeated runtime failures with count, cadence, retry class, terminal state, policy validity, and remediation. |
| `schemas/SecurityVerdictState.json` | `SecurityVerdictState` | `urn:srcos:security-verdict:` | Represent security decision availability, including degraded states such as no verdict provider, invalid provider, unavailable policy, or insufficient evidence. |
| `schemas/NetworkTruthState.json` | `NetworkTruthState` | `urn:srcos:network-truth:` | Preserve layered connectivity truth instead of reducing network state to online/offline. |
| `schemas/BrowserLaunchTransaction.json` | `BrowserLaunchTransaction` | `urn:srcos:browser-launch-transaction:` | Model browser launch as a preflight transaction before WebContent/GPU/Networking child processes are allowed to spawn. |

## Added examples

| File | Scenario |
|---|---|
| `examples/retry_loop_fingerprint.json` | Full Disk Access/TCC denial loop collapsed into one bounded fingerprint. |
| `examples/security_verdict_state.json` | Network-flow observation where the verdict provider is unavailable. |
| `examples/network_truth_state.json` | Wi-Fi radio active but no association, failed route, and degraded DNS/DHCP observers. |
| `examples/browser_launch_transaction.json` | Browser launch prevented before child-process spawn because broker and extension-registry preflight failed. |

## Design intent

The records are designed to support SourceOS doctor flows, browser diagnostics, terminal diagnostics, mesh/network intelligence, and forensic evidence receipts. They intentionally avoid platform-specific names in schema fields while allowing platform-specific event evidence through `evidenceRefs`.

## Observed failure classes covered

- Permission-denied polling loops.
- Security monitors that see flows but cannot attach verdicts.
- Network path ambiguity where radio, route, DNS, DHCP, captive portal, and internet reachability disagree.
- Browser child-process launch failures caused by missing desktop brokers, invalid registries, or denied service lookups.
- Diagnostic storms that need first-seen, last-seen, count, cadence, and user-readable remediation.

## Follow-up contract families

The next additive slice should add:

- `RuntimeIdentityGraph`
- `DesktopServiceBrokerState`
- `MaintenanceEpoch`
- `RuntimeRegistryIntegrityRecord`
- `BootSessionPhaseState`
- `DiagnosticStormRecord`

Those are intentionally deferred so this first PR remains focused and reviewable.
