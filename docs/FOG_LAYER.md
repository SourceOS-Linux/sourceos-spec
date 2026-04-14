# Fog Layer (FogVault + FogCompute)

This document defines the **Fog Layer** contract surface for the SourceOS/SociOS ecosystem.

The fog layer is designed for **heterogeneous, churny, citizen-fog environments** where machines appear and disappear and cannot be treated as durable infrastructure.

## Architecture summary

### FogVault (storage + topic substrate)

- **Local substrate:** nodes expose fast, capacity-managed *local* storage (e.g., LVM-backed PVs via a local CSI driver such as TopoLVM).
- **Distributed meaning + replication:** durability and convergence are provided *above* local storage via **append-only Merkle-log topics** (Hypercore). "Folders" and indexes are derived views.
- **Topic contract:** a topic is an append-only channel with explicit replication policy, membership, and key epochs.

### FogCompute (compute substrate)

- Nodes advertise resource offers (CPU/GPU/RAM/IO windows).
- Requestors submit work orders (image digests + inputs/outputs + verification policy).
- Workers emit usage receipts (metered via OS primitives) and optional settlement events.
- Settlement (tokenization / escrow) is a **pluggable layer**; receipts are the core evidence artifact.

## Contract status

The Fog Layer is represented by the schema set in `schemas/`:

- `Topic.json`, `TopicEnvelope.json`, `ReplicationPolicy.json`, `ContentRef.json`
- `Offer.json`, `WorkOrder.json`, `UsageReceipt.json`, `SettlementEvent.json`

These are **v0 scaffolds** intended to be evolved via ADRs and semver discipline.
