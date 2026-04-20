# ADR: Contract vs Bootstrap Boundaries

## Status
Draft

## Context
SourceOS / SociOS needs a clean separation between:
- normative contracts and compatibility rules
- Apple Silicon bootstrap and boot-chain implementation
- generic runner / adapter / workspace execution tooling

Without that split, contract, bootstrap, and runtime logic drift into each other.

## Decision
`SourceOS-Linux/sourceos-spec` remains the canonical home for:
- runner ↔ adapter IPC schemas
- protocol versioning and compatibility rules
- capability registry
- canonical error namespace
- ADRs governing compatibility discipline

Apple Silicon bootstrap logic belongs in `SociOS-Linux/asahi-installer`.
Apple Silicon boot-chain logic belongs in `SociOS-Linux/asahi-u-boot`.
Generic runner / adapter / workspace / CI implementation belongs in a separate SociOS-Linux implementation repository.

## Consequences
This repository should define the contract that implementations must satisfy, but it should not carry runtime implementation code.
