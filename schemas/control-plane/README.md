# Control-plane schema tranche — local-first release family

This directory contains the first machine-readable contract family for the local-first SourceOS lifecycle slice.

## Canonical schema identity

This tranche was originally imported with `$id` values under the `socioprophet.org` namespace (legacy).

Canonical SourceOS contract IDs use the `schemas.srcos.ai/v2/...` namespace.

To avoid breaking legacy `$id` consumers, this directory supports a **two-layer identity model**:

- **Legacy schemas**: `*.schema.json` files preserve the original `$id` values.
- **Canonical wrappers**: `*.json` files provide canonical `$id` values in the `schemas.srcos.ai` namespace and `allOf`-wrap the legacy schema.

New work should reference the canonical wrapper filenames.

## Included schemas

Legacy (original import, legacy `$id`):

- `experience-profile.schema.json`
- `isolation-profile.schema.json`
- `release-set.schema.json`
- `boot-release-set.schema.json`
- `enrollment-token.schema.json`
- `fingerprint.schema.json`
- `mesh-skill.schema.json`
- `skill-execution-events.schema.json`
- `incident-events.schema.json` (legacy incident lifecycle schema identity; canonical wrapper is `IncidentEvent.json`)

Canonical wrappers (preferred for new references):

- `ExperienceProfile.json`
- `IsolationProfile.json`
- `ReleaseSet.json`
- `BootReleaseSet.json`
- `EnrollmentToken.json`
- `Fingerprint.json`
- `MeshSkill.json`
- `SkillExecutionEvent.json`
- `IncidentEvent.json`

## Intent

These schemas define the minimum typed seam for:

1. selecting operator/user experience posture
2. selecting isolation posture
3. assigning a release to a device, cohort, or site
4. authorizing boot/recovery/install flows where required
5. redeeming one-time enrollment tokens
6. emitting post-apply fingerprints for compliance and rollback decisions
7. emitting incident lifecycle events (freeze/fork/kill)

## Downstream consumers

- `SocioProphet/agentplane`
- `SocioProphet/sociosphere` (by reference where needed)
- `SocioProphet/TriTRPC` (transport-safe refs after stabilization)
- SourceOS realization and installer lanes
