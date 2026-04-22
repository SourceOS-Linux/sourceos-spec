# ADR 0002 — sourceos-shell API and event backlog

## Status
Accepted

## Context

The shell/document/provenance workflow now has an initial schema cut, but downstream implementations also need a clear backlog for the API and event surfaces that should be added to OpenAPI and AsyncAPI.

## Decision

Queue the following surfaces for future OpenAPI/AsyncAPI additions:

- artifact sign/validate status
- annotation export
- run-report publication
- publish decisions
- mirror receipts
- Noether diagnostic publication
- search route decisions

## Consequences

The schema layer can land incrementally while API/event surfaces are added in follow-on patches without re-defining the objects elsewhere.
