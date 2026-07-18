# SVF OS Validation Profiles

Status: contract declaration for SourceOS/SociOS OS lanes  
Plane: SourceOS / SociOS typed-contract and OS validation  
Upstream authority: SocioProphet/ProCybernetica SVF policy primitive  
Workspace registry: SocioProphet/sociosphere SVF workspace registry

## Purpose

This document defines the first Sovereign Validation Fabric (SVF) posture for SourceOS and SociOS OS validation profiles.

The immediate goal is not to execute image builds, package builds, kernel checks, signing, or hardware validation through Sociosphere. The immediate goal is to declare the OS validation surfaces that should become governed SVF Plans once repo-local validators exist.

## Initial placement

`SourceOS-Linux/sourceos-spec` is the canonical typed-contract, JSON-LD, and shared vocabulary lane for SourceOS / AgentOS contracts. It is therefore the correct first home for the cross-repo OS validation profile vocabulary.

`SociOS-Linux/SourceOS` is the immutable workstation and edge substrate. It should later publish substrate-specific SVF contracts that consume the shared vocabulary from this repository.

`SourceOS-Linux/sourceos-boot`, `SourceOS-Linux/sourceos-shell`, and `SourceOS-Linux/sourceos-devtools` may later publish repo-local validation contracts for boot, shell, and developer tooling surfaces.

## Initial SVF ids

The first profile family reserves these ids:

- `svf:policy:sourceos.contract-readonly`
- `svf:plan:sourceos.contract-validation-basic`
- `svf:profile:sourceos.contracts`
- `svf:policy:socios.sourceos-substrate-readonly`
- `svf:plan:socios.sourceos-substrate-basic`
- `svf:profile:socios.sourceos-substrate`

## Candidate claim scopes

Initial SourceOS/SociOS OS validation Plans may support only bounded claims:

- `schema_conformant`
- `fixtures_validated`
- `policy_boundary_preserved`
- `artifact_integrity_verified` when digest verification actually exists
- `non_production_only`

They must not certify:

- full hardware compatibility;
- full distribution release readiness;
- secure boot or measured boot success unless attestation evidence exists;
- package provenance unless package digest and source provenance checks exist;
- kernel or module safety beyond declared checks;
- production update safety;
- downstream deployment correctness.

## Candidate validation surfaces

SourceOS/SociOS OS profiles should eventually cover:

1. typed contract schema validation;
2. JSON-LD context and vocabulary validation;
3. package manifest validation;
4. image manifest validation;
5. SBOM presence and shape validation;
6. digest manifest validation;
7. boot artifact manifest validation;
8. QEMU smoke validation, only after a safe sandbox runner exists;
9. measured-boot and attestation evidence validation, only after attestation artifacts exist;
10. release publication readiness, only after signing and provenance policy are separately defined.

## First implementation order

1. Declare this doctrine document in `sourceos-spec`.
2. Add a repo-local SVF contract bundle in `sourceos-spec` for typed-contract validation.
3. Add a contract validator that checks ids, policy posture, local read-only behavior, action refs, claim scopes, and non-claims.
4. Wire a local validation target.
5. Register `SourceOS-Linux/sourceos-spec` in Sociosphere SVF registry as advisory.
6. Later, add substrate-specific contracts in `SociOS-Linux/SourceOS`.

## Non-claims

This document does not build an OS image.

This document does not validate bootability.

This document does not issue a ValidationReceipt.

This document does not authorize signing, publishing, deployment, or production updates.

This document does not grant Sociosphere authority to execute OS build actions.
