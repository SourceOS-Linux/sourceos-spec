# ADR-0012: SourceOS Mutation and Evidence Accountability

Status: Proposed
Date: 2026-05-05

## Context

A multi-artifact forensic review of macOS resource, syslog, console, Wi-Fi, and memorystatus reports exposed a recurring operating-system design failure: modern systems may enforce policy and collect telemetry while still failing to explain causality to the human operator.

The reviewed evidence showed repeated browser disk-write pressure, browser process-family memory pressure, sandbox/TCC denials, watchdog coverage gaps, launchd/XPC service churn, Spotlight/indexing worker churn, opaque log-routing, media/codec diagnostic chatter, and weak continuity across shutdown, boot, login, and logging-service restart boundaries.

The security conclusion is intentionally conservative: the available logs do not prove compromise, but they are not sufficient to clear compromise either. Several sensors were degraded or semantically incomplete. SourceOS must treat opaque or degraded telemetry as an evidence-quality failure, not as negative evidence.

## Decision

SourceOS will adopt a receipt-native accountability model for mutation, evidence routing, service lifecycle, resource pressure, media work, temporary artifacts, policy denials, and compromise assessment.

The canonical specification home is this repository, `SourceOS-Linux/sourceos-spec`, using the existing layout:

- `docs/adr/` for architectural decisions.
- `docs/contract-additions/` for normative contracts.
- `schemas/` for JSON schemas.
- `examples/` for valid examples.
- `fixtures/` for invalid or degraded anti-pattern examples.
- `tools/` for schema validation and CI checks.

Implementation should fan out only after this contract is stable:

- `SourceOS-Linux/sourceos-boot`: boot evidence topology attestation and cross-reboot session IDs.
- `SourceOS-Linux/sourceos-devtools`: validators, CLI tooling, CI gates, and synthetic anti-pattern fixtures.
- `SourceOS-Linux/sourceos-shell`: operator timeline, evidence panel, and `sourceosctl explain` flows.
- `SourceOS-Linux/BearBrowser`: browser coalition/profile/storage/write receipts.
- `SourceOS-Linux/TurtleTerm`: terminal/session/UI-observation receipts.
- `SourceOS-Linux/sourceos-syncd`: sync-cycle receipts, full-sync risk receipts, and temporary artifact budgets.

## Required event families

- `sourceos.observability.event.v0.1`
- `sourceos.write_accountability.v0.1`
- `sourceos.routing_receipt.v0.1`
- `sourceos.media_work.v0.1`
- `sourceos.temporary_artifact.v0.1`
- `sourceos.coalition_resource.v0.1`
- `sourceos.policy_decision.v0.1`
- `sourceos.compromise_assessment.v0.1`

## Consequences

Every relevant subsystem must preserve enough evidence to answer:

1. What happened?
2. Who or what caused it?
3. Which durable or temporary object changed?
4. Which policy allowed, denied, degraded, sampled, redacted, routed, or dropped the event?
5. What resource budget was consumed?
6. What evidence was missing or degraded?
7. What downstream work or risk was created?
8. What should the user or operator do next?

## Non-goals

This ADR does not attempt to prove compromise in the reviewed macOS artifacts. It uses them as design evidence. It also does not require raw sensitive paths or network identifiers in default logs. SourceOS should use privacy-preserving object IDs by default and support explicit forensic expansion only when authorized.

## Acceptance criteria

- A base observability event schema exists and validates examples.
- Mutation/write accountability, evidence routing, media work, temporary artifact lifecycle, coalition resource, policy decision, and compromise assessment schemas exist.
- Valid examples and invalid anti-pattern fixtures are provided.
- A local validator checks valid examples pass and anti-pattern fixtures fail.
- Documentation explicitly states that lack of positive evidence is not clearance when sensors are degraded or evidence quality is insufficient.
