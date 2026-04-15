# Control-plane schema tranche — local-first release family

This directory contains the first machine-readable contract family for the local-first SourceOS lifecycle slice.

## Included schemas

- `experience-profile.schema.json`
- `isolation-profile.schema.json`
- `release-set.schema.json`
- `boot-release-set.schema.json`
- `enrollment-token.schema.json`
- `fingerprint.schema.json`
- `incident-events.schema.json` (existing)

## Intent

These schemas define the minimum typed seam for:

1. selecting operator/user experience posture
2. selecting isolation posture
3. assigning a release to a device, cohort, or site
4. authorizing boot/recovery/install flows where required
5. redeeming one-time enrollment tokens
6. emitting post-apply fingerprints for compliance and rollback decisions

## Downstream consumers

- `SocioProphet/agentplane`
- `SocioProphet/sociosphere` (by reference where needed)
- `SocioProphet/TriTRPC` (transport-safe refs after stabilization)
- SourceOS realization and installer lanes
