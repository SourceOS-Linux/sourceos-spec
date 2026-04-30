# ADR: Developer Tools Repo Boundary

**Date:** 2026-04-30  
**Status:** Accepted

---

## Context

SourceOS needs a dedicated home for Linux-native developer tooling: Nix/devshell orchestration, NLBoot/operator tooling, lab profile selection, release tooling, local AI governance utilities, and SourceOS workstation bootstrap scripts.

Without a clear boundary, developer tooling risks drifting into `sourceos-spec` (the typed-contract registry) or into OS substrate repos, causing confusion about ownership, validation scope, and consumable contracts.

## Decision

`SourceOS-Linux/sourceos-devtools` is established as the canonical home for all SourceOS developer tooling. Its topology role is `roleDeveloperToolchain`.

`sourceos-spec` registers the repo in the canonical topology (repo descriptor example and `connectsTo` link) but does **not** carry any devtools implementation, shell scripts, Nix expressions, or operator tooling.

Specifically, `sourceos-devtools` owns:

- Nix flakes and devshell configurations
- NLBoot operator and lab-profile selection scripts
- Release tooling (cut, sign, publish)
- Local AI governance CLI utilities
- SourceOS workstation bootstrap helpers
- `repo.maturity.yaml` for its own maturity tracking

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Embed devtools in `sourceos-spec` | Violates the typed-contract-registry boundary; spec must stay normative-only |
| Embed devtools in `agentos-spine` | Spine owns Linux integration, not developer ergonomics or release tooling |
| Embed devtools in `SourceOS` (substrate) | Substrate is immutable OS layer; devtools are operator-time, not build-time |

## Consequences

- `sourceos-spec` remains a pure typed-contract and vocabulary registry with no executable devtools content.
- `sourceos-devtools` consumes contracts and vocabulary from `sourceos-spec` but does not redefine them.
- Agents and tooling can resolve the devtools repo via `urn:sourceos:repo:SourceOS-Linux:sourceos-devtools` using the canonical topology descriptor.

## References

- [GitHub issue #70: Admin task: create and bootstrap sourceos-devtools repo](https://github.com/SourceOS-Linux/sourceos-spec/issues/70)
- `examples/repo-descriptor.sourceos-devtools.jsonld` — canonical topology entry
- `semantic/repo-ontology.jsonld` — `roleDeveloperToolchain` definition
