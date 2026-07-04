# SourceOS Mutation and Evidence Accountability v0.1

## Purpose

This contract defines the minimum evidence model for mutation, resource pressure, policy denials, evidence routing, media/codec work, temporary artifacts, service lifecycle, and compromise assessment in SourceOS.

The design motivation is a repeated failure pattern observed in opaque macOS logs: low-level mechanisms recorded fragments of truth, but no layer provided a complete causal explanation. SourceOS must make mutation and evidence accountable by default.

## Normative principles

1. **Receipts over loose logs.** Events that mutate state, consume resource budgets, change evidence routing, or degrade security coverage must emit structured receipts.
2. **No degraded sensor may clear an incident.** Absence of evidence from a degraded sensor is not negative evidence.
3. **Report by actor, object, operation, policy, cost, and cause.** Process name alone is not attribution.
4. **Report by coalition and service class.** Browsers, office stacks, indexers, sync agents, and model services are multi-process families.
5. **Every denial needs a classification.** A denial can be expected, expected-but-degraded, misconfigured, suspicious, impossible, or unknown.
6. **Retry and activation storms must circuit-break.** Repeated failures must be summarized with counts, first/last timestamps, backoff state, and remediation.
7. **Logs are governed artifacts.** Routed, sampled, dropped, redacted, compressed, or diverted log streams must themselves have routing receipts.
8. **Temporary artifacts are typed.** Codec scratch files, previews, thumbnails, sync staging, caches, and owned media must not collapse into one path class.
9. **Cross-reboot continuity is mandatory.** Boot sessions, shutdowns, restarts, login sessions, and logging topology changes require stable correlation IDs.
10. **Evidence quality is explicit.** Each incident must expose what is known, unknown, degraded, redacted, or insufficient.

## Required event families

- `sourceos.observability.event.v0.1`
- `sourceos.write_accountability.v0.1`
- `sourceos.routing_receipt.v0.1`
- `sourceos.media_work.v0.1`
- `sourceos.temporary_artifact.v0.1`
- `sourceos.coalition_resource.v0.1`
- `sourceos.policy_decision.v0.1`
- `sourceos.compromise_assessment.v0.1`

## Minimum event envelope

Every receipt must include:

- `schema`
- `event_id`
- `timestamp`
- `boot_id`
- `session_id`
- `actor`
- `operation`
- `policy`
- `evidence_quality`
- `causal_parents`

## Required evidence-quality states

- `complete`
- `partial`
- `degraded_sensor`
- `opaque_symbolication`
- `redacted`
- `insufficient_for_clearance`

## Required compromise-assessment states

- `compromise_proven`
- `compromise_suspected`
- `no_positive_compromise_evidence`
- `cannot_exclude_compromise`
- `sensor_degraded`
- `evidence_inadequate`

## Required artifact classes

- `owned_media`
- `durable_document`
- `derived_preview`
- `codec_temp`
- `attachment_cache`
- `thumbnail_cache`
- `sync_staging`
- `failed_transcode_residue`
- `message_database_reference`
- `browser_profile_db`
- `browser_cache`
- `semantic_index`
- `opaque_vendor_state`

## Required operator queries

A SourceOS operator view must be able to answer:

- Explain writes.
- Explain logs and evidence routing.
- Explain memory and coalition pressure.
- Explain sync/reindex/full-sync risks.
- Explain policy denials.
- Explain degraded security coverage.
- Explain media/temp artifacts.
- Explain why compromise can or cannot be excluded.

## Initial repo placement

This contract belongs in `SourceOS-Linux/sourceos-spec` under `docs/contract-additions/mutation-evidence-accountability.md`. Implementation should be fanned out only after the contract and schema fixtures are validated.
