# Radio-Spatial, Learned Location, and Home Context Boundaries

Status: additive security-contract placement note.

## Summary

SourceOS treats radio-spatial context as high-sensitivity derived personal data.

This boundary covers Wi-Fi RSSI/LQM, BSSID/AP observations, Bluetooth proximity, AWDL/Nearby discovery, Wi-Fi ranging capability, motion/PDR hints, micro-location, visit/routine inference, known-place state, HomeKit service-area state, Matter/Thread topology, and IntelligencePlatform-style derived context views.

The motivating forensic evidence showed a same-evening local chain across Wi-Fi signal telemetry, Wi-Fi positioning, nearby/ranging discovery, CoreRoutine/routined learned-location state, HomeKit/assistant access, model asset handling, and IntelligencePlatform knowledge maintenance. The evidence supports a radio-spatial learned-location substrate. It does not, by itself, prove a direct Wi-Fi -> ANE -> room-map causal path.

## Security rule

Radio-spatial context is personal context.

A trustworthy OS must expose receipts for:

1. signal collection,
2. location/routine/home derivation,
3. model or heuristic use,
4. protected or shared storage,
5. cloud or mirroring behavior,
6. export,
7. retention,
8. deletion, and
9. user revocation.

The user must not need to inspect private SQLite databases, protected plist stores, or opaque system logs to know whether radio-spatial derived context exists.

## Claim discipline

SourceOS receipts distinguish four different claims:

- **subsystem present**: code paths, stores, schemas, or preferences exist;
- **current visible activity**: counters, timestamps, logs, or receipts show activity in a known window;
- **causal bridge proven**: the output of one stage is tied to the input of another stage;
- **derived artifact found**: a room, home, routine, graph, or other derived object is identified.

A zero current counter does not erase a subsystem. It only limits the claim about current activity.

## Required receipt family

This placement note introduces the following additive schemas:

- `RadioSpatialSignalReceipt`
- `RadioSpatialInferenceReceipt`
- `LearnedLocationReceipt`
- `RadioPOIReceipt`
- `RoutineSchedulerReceipt`
- `RadioSpatialModelAssetReceipt`
- `RadioSpatialCorrelationReceipt`
- `ProtectedContextStoreReceipt`

Together these receipts capture signal collection, inferred location/routine/home context, model asset use, scheduled routine jobs, correlation windows, and protected stores.

## Required user-visible controls

The SourceOS shell should expose a Context Receipts surface showing:

- radio-spatial signals collected,
- inferred locations, visits, known places, and routines,
- Home/Matter/Thread state used for inference,
- model assets used,
- local versus cloud/private compute boundaries,
- shared containers and preference domains touched,
- protected stores created,
- cloud/mirroring state,
- deletion and revocation status.

## Integration points

This boundary must compose with:

- visual/OCR derived-context receipts,
- shared-state and group-container receipts,
- connector/tool-permission receipts,
- model-asset receipts,
- private-cloud and partner-compute receipts,
- agent session and tool-call receipts.

## Acceptance tests

- A Wi-Fi-derived location fix emits `RadioSpatialSignalReceipt` and `RadioSpatialInferenceReceipt`.
- Known-place identifiers are exported only as hashes or presence flags unless the user explicitly exports raw values.
- BluePOI-like subsystem keys with zero counters produce `currentSnapshotActivity: inactive_or_zero_counter`.
- Model asset use for motion/location/routine inference emits `RadioSpatialModelAssetReceipt`.
- A protected context store emits `ProtectedContextStoreReceipt` even when raw contents are unavailable.
- Deleting a source signal or source object deletes or tombstones derived radio-spatial context.

## Non-goals

This note does not define a vendor-specific Apple compatibility layer. It defines the open SourceOS receipt model we require from any implementation that collects or derives radio-spatial context.
