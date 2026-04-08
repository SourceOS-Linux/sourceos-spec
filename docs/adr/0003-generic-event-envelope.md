# ADR-0003: Generic EventEnvelope for all channels

**Status:** Accepted  
**Date:** 2025-12-24  
**Deciders:** SourceOS core team

---

## Context

The event spine publishes events from many entity types (Dataset, Policy, Run, AgentSession, etc.). The AsyncAPI specification must define a payload schema for each channel. Two design options were considered:

**Option A — Channel-specific payload schemas:**  
Each channel references a dedicated schema (e.g., `DatasetEvent.json`, `PolicyEvent.json`). Payloads are strongly typed per channel.

**Option B — Generic envelope with typed payload:**  
All channels share a single `EventEnvelope.json` schema. The `eventType` string field discriminates the sub-type; the `payload` field is an open `object`.

## Decision

Use a **generic `EventEnvelope`** (Option B) for all channels.

## Rationale

1. **Operational simplicity** — a single schema for all event consumers reduces the number of schema versions that must be co-evolved across teams.
2. **Cross-cutting concerns** — the envelope provides a uniform place for `eventId`, `occurredAt`, `actor`, `objectId`, and `integrity` fields that every event needs, regardless of type.
3. **Incremental type refinement** — teams can introduce typed payload schemas for specific `eventType` values as usage matures, using `oneOf`/discriminator on the payload field, without changing the channel contract.
4. **Kafka compaction** — using `objectId` as the Kafka message key enables log compaction by default, regardless of `eventType`.

## Trade-offs

- **Loss of static payload typing at the channel level** — consumers must switch on `eventType` at runtime. This is mitigated by documenting the valid `eventType` values per channel in `asyncapi.yaml` channel descriptions.
- **No compile-time payload validation** — tooling cannot auto-generate typed consumer stubs per `eventType`. This is acceptable at v2; typed variants can be added as a non-breaking change in a future minor version.

## Future evolution

A future ADR may introduce `oneOf` discriminated payload schemas for high-volume event types (e.g., `RunRecordedPayload`, `PolicyEvaluatedPayload`) as a minor, non-breaking addition to the `EventEnvelope` schema.

## Consequences

- `EventEnvelope.json` uses `"payload": { "type": "object" }` — no further constraint.
- Each `asyncapi.yaml` channel description documents the expected `eventType` values for that channel.
- Consumers must not assume `payload` structure without first checking `eventType`.
- The `integrity.eventHash` field enables consumers to detect replay attacks and message corruption independently of the payload type.
