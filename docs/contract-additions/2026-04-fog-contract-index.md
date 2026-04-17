# Fog contract additions index

- **Status:** bootstrap index
- **Date:** 2026-04-16

This document provides a discoverability layer for the initial FogVault / FogCompute contract additions landed in the typed-contract repository.

## New schema types

### FogVault (storage + topics)

- `Topic.json`
- `TopicEnvelope.json`
- `ReplicationPolicy.json`
- `ContentRef.json`

### FogCompute (offers + execution evidence)

- `Offer.json`
- `WorkOrder.json`
- `UsageReceipt.json`
- `SettlementEvent.json`

## Matching examples

- `examples/topic.json`
- `examples/topic_envelope.json`
- `examples/replication_policy.json`
- `examples/content_ref.json`
- `examples/offer.json`
- `examples/workorder.json`
- `examples/usage_receipt.json`
- `examples/settlement_event.json`

## Why these additions exist

These objects provide the first canonical contract surface for:

- append-only Merkle-log topic channels
- explicit replication and retention policy
- content-addressed fog storage references
- metered compute offers and work orders
- signed execution receipts and optional settlement mapping

## Relationship to existing schema families

These additions extend the existing SourceOS/SociOS contract system rather than replacing it.

- FogVault extends the execution / provenance story with durable topic and content-addressed storage semantics.
- FogCompute extends the execution and agent/runtime story with provider offers, workload requests, and receipts.
- Settlement remains a pluggable evidence layer rather than a mandatory control-plane dependency.

## Intended next updates

1. add dedicated OpenAPI / AsyncAPI fog patch fragments
2. fold these objects into the schema catalog and repo README family tables
3. add semantic overlay entries for fog vocabulary
4. add stricter schema cross-linking once runtime semantics are finalized
