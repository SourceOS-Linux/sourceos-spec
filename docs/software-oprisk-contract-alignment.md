# Software Operational Risk Typed Contract Alignment

## Purpose

This note records how `SourceOS-Linux/sourceos-spec` aligns to the software operational risk governance pack proposed in `SocioProphet/socioprophet-standards-storage` PR #72.

## Why this repo is in scope

The current upstream README positions `sourceos-spec` as the canonical machine-readable specification layer for SourceOS / SociOS metadata governance and the agent plane, including JSON Schemas, OpenAPI, AsyncAPI, and semantic overlays.

That makes this repo the correct downstream owner for the **typed contract lane** of software operational risk.

## Expected responsibilities

### 1. Incident schema family

This repo SHOULD host or cross-reference machine-readable contracts for software operational-risk objects such as:

- outage incident,
- degradation incident,
- upstream watch item,
- drift KRI,
- control evidence summary,
- reserve / scenario report envelope.

### 2. Transport and API implications

Where operational-risk data flows across services, the contract layer SHOULD define or patch:

- REST / query surfaces,
- event channels,
- and schema identities for incident and watchlist exchange.

### 3. Semantic alignment

The semantic layer SHOULD eventually express relationships among:

- critical service,
- dependency node,
- edge,
- common-mode cluster,
- control,
- incident,
- evidence grade,
- and reserve output.

## Immediate backlog

1. Define a first incident schema for harvested outage records.  
2. Define a watchlist / upstream-drift schema.  
3. Decide whether reserve outputs belong in this repo or in a companion schema package.  
4. Cross-reference the standards pack after PR #72 lands.
