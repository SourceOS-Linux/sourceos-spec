# ADR 0001: Architecture-aware Boot and Storage Profiles

**Date:** 2026-04-15  
**Status:** `Accepted`

---

## Context

Boot semantics are not generic storage semantics. They are a firmware- and architecture-bound contract between the machine, the partition map, the bootloader, and the filesystems used on the early-boot path.

SourceOS and SociOS aim to provide auditable, reproducible, zero-trust installation and recovery behavior. That requires the boot-critical storage surface to be modeled explicitly rather than inferred from ad hoc installer heuristics.

A useful concrete example is legacy / PowerPC guidance from Red Hat Enterprise Linux 6, which treats the storage layout as boot-critical infrastructure rather than as generic capacity planning. In that guidance, Power systems require a PReP boot partition as the first partition on disk, recommend tight sizing for that partition, constrain early-boot filesystem choices, and call out operational sizing guidance for `/boot`, `/`, `/var`, and swap.

The broader lesson generalizes beyond that specific platform:

- some platforms require architecture-specific boot artifacts (for example ESP, BIOS boot partitions, or PReP)
- early-boot filesystem compatibility is stricter than general-purpose data filesystem selection
- `/var` is an operational state surface and must be sized and governed differently from boot-critical partitions
- swap sizing is workload- and policy-dependent, not a single universal formula

If these rules live only inside installer code, they are hard to audit, hard to validate, and easy to drift across implementations.

## Decision

SourceOS/SociOS SHALL model disk layout through **architecture-aware boot/storage profiles** rather than through a single generic partitioning recipe.

A boot/storage profile binds a specific architecture and boot method to an explicit set of constraints and recommendations, including:

1. required boot partitions and their ordering rules
2. allowed filesystem families for boot-critical mount roles
3. minimum or recommended size heuristics for boot-critical and mutable-state partitions
4. bootloader and early-boot artifact placement requirements
5. validation rules, warnings, and failure conditions surfaced before destructive install actions

At minimum, the profile model MUST distinguish between:

- **boot-critical surfaces**: e.g. ESP, BIOS boot partition, PReP boot partition, `/boot`
- **system/root surfaces**: e.g. `/`
- **mutable operational state**: e.g. `/var`
- **user and project state**: e.g. `/home`, user volumes, project volumes

The SourceOS/SociOS stack SHOULD treat swap as a policy-governed resource derived from workload class, suspend/hibernate policy, and system role, rather than as a fixed linear function of RAM.

The initial profile set SHOULD cover at least:

- x86_64 + UEFI
- x86_64 + BIOS on GPT where relevant
- Apple-oriented UEFI-derived paths where relevant to our supported hardware
- Power / PReP-style legacy boot paths where support is intentionally provided

Installers and image-build systems consuming this specification SHOULD implement a dry-run validator that can explain *why* a candidate layout is invalid or risky before any write occurs.

## Alternatives considered

| Alternative | Reason not chosen |
|-------------|------------------|
| Keep partitioning logic only in installer implementation code | Hides normative rules inside implementation details, makes review and cross-implementation consistency harder |
| Use one generic partitioning recipe for all architectures | Incorrect for multi-architecture systems and incapable of expressing firmware-specific boot requirements |
| Treat storage only as an image-build concern rather than a specification concern | Prevents policy validation at the contract layer and weakens auditability |
| Encode only minimum sizes without filesystem or ordering constraints | Misses the actual boot semantics that cause installations to fail |

## Consequences

### Positive

- boot requirements become explicit, reviewable, and portable across installers and image-build paths
- architecture-specific boot artifacts are modeled as first-class constraints rather than tribal knowledge
- dry-run validation and policy explanation become possible before destructive installation steps
- separation of boot-critical storage from mutable operational state improves auditability and recovery design
- SourceOS can align installer behavior, image building, and documentation on one normative storage model

### Negative

- additional specification work is required to define profile structures and validation semantics
- installer implementations must expose more detailed validation and error messaging
- profile maintenance becomes an ongoing responsibility as supported hardware and boot methods evolve

## References

- Red Hat Enterprise Linux 6 Installation Guide — PPC partitioning recommendations: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/6/html/installation_guide/s2-diskpartrecommend-ppc#id4394007
- Repository authoring guidance for ADRs: `CONTRIBUTING.md`
