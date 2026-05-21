# Mutation and Evidence Accountability: Stack Integration Map

Status: Proposed
Date: 2026-05-05

## Purpose

This implementation map turns the forensic lessons behind SourceOS Mutation and Evidence Accountability into concrete improvement targets for BearBrowser, TurtleTerm, SourceOS Shell, sourceos-syncd, sourceos-devtools, sourceos-boot, Exodus, FogStack, and the ontology/evidence planes.

The critical lesson is that SourceOS must learn from opaque macOS logs by refusing process-only attribution. The stack must explain delegated mutation: human intent, UI action, app or agent actor, service delegation, database/file/temp/object mutation, evidence routing, policy decision, and evidence quality.

## Cross-stack doctrine

1. Every mutation requires a receipt.
2. Every delegated mutation requires an `on_behalf_of` chain.
3. Every resource-pressure incident requires actor, object, operation, policy, resource cost, causal parent, and evidence-quality fields.
4. Every degraded or blind sensor prevents security clearance.
5. Every browser write-pressure incident must distinguish core profile, origin storage, service-worker/cache, session restore, sync, extension storage, diagnostics, and profile repair.
6. Every terminal/session action that spawns, writes, downloads, extracts, or invokes agents must carry session and intent context.
7. Every sync, archive extraction, preview, index, media/codec, and diagnostic path must distinguish durable user data from temp/cache/derived state.
8. Every evidence route must say where events went, what was redacted, what was sampled, what was dropped, and what requires privilege.

## BearBrowser improvements

BearBrowser must become the reference implementation for browser write accountability.

Required work:

- Emit `BrowserWriteAccountabilityReceipt` for core profile writes, per-origin storage, service-worker/cache writes, downloads/cache writes, session restore, sync state, diagnostics, extension storage, hidden/system add-ons, and profile repair/migration.
- Add `extension_inventory_state` with values `none_visible`, `installed`, `hidden_possible`, `unavailable`, and `not_collected`.
- Prevent unsupported attribution: if no visible extensions exist, extension storage must not be the primary cause without additional evidence.
- Emit per-origin and per-storage-class counters where available.
- Capture SQLite/WAL/checkpoint counts for browser profile databases.
- Surface a user-readable `Explain browser writes` panel.
- Add fixtures mirroring Firefox-style opaque reports: SQLite profile churn, raw write bursts, service-worker cache churn, session-restore snapshots, and no-extension anti-patterns.

Acceptance criteria:

- A write-pressure example can identify whether the write source is profile core, origin storage, service worker, sync, extension, cache, or unknown.
- A no-visible-extension case cannot be auto-labeled as extension-caused.
- Missing database path/origin/extension fields reduce evidence quality.

## TurtleTerm improvements

TurtleTerm must become the reference implementation for terminal/session mutation accountability.

Required work:

- Emit `TerminalSessionReceipt` for interactive shells, command execution, downloads, archive extraction, file writes, chmod/chown/xattr changes, and agent invocations.
- Attach terminal session ID, working directory, command digest/redacted command class, process tree, user intent class, and output artifact class.
- Emit `ArchiveExtractionReceipt` when tools such as tar, unzip, bsdtar, ditto-equivalent, npm/pnpm extraction, package managers, or build tools expand archives.
- Emit `DiagnosticSelfNoiseReceipt` when terminal-driven diagnostics collect traces, symbolicate, export logs, or write evidence bundles.
- Mark commands that cross path boundaries: Downloads, Desktop, Documents, project workspace, app container, sync root, cache, temp, external volume, network mount, package/bundle.

Acceptance criteria:

- A terminal-driven extraction can explain source archive, output path class, file count, byte count, permission/xattr changes, cleanup policy, and downstream indexing/sync triggers.
- A diagnostic command can account for its own evidence writes.
- Agent-triggered terminal work carries human intent and agent identity.

## SourceOS Shell improvements

SourceOS Shell must provide the operator-facing explanation plane.

Required work:

- Add `sourceosctl explain writes`.
- Add `sourceosctl explain sync`.
- Add `sourceosctl explain browser`.
- Add `sourceosctl explain terminal`.
- Add `sourceosctl explain logs`.
- Add `sourceosctl explain compromise`.
- Add an Evidence Topology panel showing event sources, routing, sinks, privilege requirements, redaction, sampling, drops, and retention.
- Add a Mutation Graph view with actor, delegated actor, service, object, policy, resource, and evidence-quality nodes.

Acceptance criteria:

- An operator can distinguish no positive compromise evidence from evidence sufficient to clear compromise.
- A resource incident shows causal parents, delegated actors, evidence gaps, and next evidence required.

## sourceos-syncd improvements

sourceos-syncd must become the reference implementation for delegated sync accountability.

Required work:

- Emit `SyncCycleReceipt`, `DelegatedIOReceipt`, `FullSyncRiskReceipt`, `CloudObjectTransferReceipt`, and `SchedulerReceipt`.
- Track sync roots, object IDs, batch sizes, direction, retry/backoff, pacer state, full-sync/checkpoint events, and local DB updates.
- Distinguish local sync metadata writes from durable file content writes and cloud/fog object transfers.
- Capture logical bytes, physical bytes, clone/reflink bytes, and dirty-memory accounting bytes separately.

Acceptance criteria:

- A cloud/fog sync incident can explain the origin actor, requesting actor, executing service, object namespace, DB writes, object transfers, and cleanup/staging transitions.
- A full-sync or reindex risk is emitted before the expensive work starts when possible.

## sourceos-devtools improvements

sourceos-devtools must own the validation and fixture harness.

Required work:

- Wire `tools/validate_mutation_evidence_accountability.py` into CI.
- Add schema fixtures for valid and invalid cases.
- Add anti-pattern checks for process-only attribution, false clearance with blind sensors, raw write burst without object classification, cloud sync without causal parent, folder traversal without path boundary, and diagnostic writes without observer-effect accounting.
- Provide fixture generators for synthetic WAL churn, sync bursts, archive extraction, cache maintenance, and evidence routing gaps.

Acceptance criteria:

- Valid examples pass.
- Invalid anti-patterns fail.
- CI blocks schema regressions and unsupported security conclusions.

## sourceos-boot improvements

sourceos-boot must anchor cross-reboot evidence continuity.

Required work:

- Emit `BootEvidenceTopologyAttestation` at boot.
- Generate stable `boot_id` and `session_id` values.
- Attest logging/evidence sinks, enabled sensors, disabled sensors, privilege state, redaction profiles, and retention policies.
- Record immutable OS deployment identity, kernel build, image digest, symbolication bundle state, and measured boot references when available.

Acceptance criteria:

- Every event can be attached to a boot/session context.
- Missing or degraded boot evidence prevents high-confidence security clearance.

## Exodus improvements

Exodus must treat migration as accountable mutation, not bulk copying.

Required work:

- Classify durable user media separately from derived previews, codec temps, thumbnails, attachment caches, sync staging, failed transcode residue, and opaque vendor state.
- Emit archive extraction, media/codec work, temporary artifact lifecycle, and ownership/attestation receipts.
- Quarantine or exclude vendor cache/temp artifacts unless explicitly requested.

Acceptance criteria:

- Migration manifests explain imported, excluded, quarantined, reconstructed, and ignored artifacts.
- Owned media import does not accidentally preserve codec scratch or vendor cache as durable content.

## FogStack and Prophet Platform improvements

FogStack and Prophet Platform must absorb these receipts into governance and evidence-console surfaces.

Required work:

- Extend service manifests with write budgets, log budgets, sync budgets, temp artifact budgets, and evidence routing declarations.
- Map SourceOS receipts into the platform evidence console.
- Add policy gates that reject services with unbounded logging, opaque temp artifacts, or degraded sensor-clearance claims.

Acceptance criteria:

- A service manifest declares mutation and evidence behavior before deployment.
- Evidence console can show resource pressure, delegated mutation, evidence gaps, and policy decisions across local, fog, and cloud deployments.

## Ontogenesis improvements

Ontogenesis should host the semantic model and SHACL gates.

Required work:

- Model actors, delegated actors, services, objects, artifacts, policies, evidence quality, resource budgets, and compromise assessment states.
- Add SHACL gates that reject invalid clearance when sensors are degraded.
- Add ontology classes for mutation receipt, evidence pipeline receipt, execution context receipt, and service work receipt.

Acceptance criteria:

- Receipts can be validated semantically, not only syntactically.
- Evidence-quality limits are machine-checkable.

## Immediate issue package

Create implementation issues in these repos after the spec PR opens:

1. `SourceOS-Linux/BearBrowser`: Implement browser write accountability and no-extension attribution guardrails.
2. `SourceOS-Linux/TurtleTerm`: Implement terminal/session mutation receipts and archive extraction receipts.
3. `SourceOS-Linux/sourceos-shell`: Implement `sourceosctl explain` and Evidence Topology panel.
4. `SourceOS-Linux/sourceos-syncd`: Implement delegated sync and full-sync-risk receipts.
5. `SourceOS-Linux/sourceos-devtools`: Wire schema validator and anti-pattern fixtures into CI.
6. `SourceOS-Linux/sourceos-boot`: Emit boot evidence topology attestation.
7. `SocioProphet/prophet-platform`: Integrate receipts into evidence console and FogStack manifests.
8. `ontogenesis`: Add ontology classes and SHACL gates.
9. `Exodus`: Add migration artifact taxonomy and temp/cache exclusion logic.

## Completion definition

This workstream is not complete until the specification, schemas, examples, validators, repo issues, and at least one implementation prototype exist. The first complete prototype should prove the path from observed mutation to operator explanation:

`event source -> receipt -> schema validation -> evidence graph -> sourceosctl explain -> UI/evidence console`.
