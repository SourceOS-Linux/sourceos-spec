# Control-plane examples — local-first release family

This directory contains example payloads for the first local-first SourceOS control-plane contract family.

## Included examples

- `experience-profile.sample.json`
- `isolation-profile.sample.json`
- `release-set.sample.json`
- `boot-release-set.sample.json`
- `enrollment-token.sample.json`
- `fingerprint.sample.json`
- `incident.freeze.sample.json` (existing)

These examples are intended to support the thin local-first lifecycle slice:

1. choose experience posture
2. choose isolation posture
3. assign a release
4. optionally authorize boot/recovery
5. redeem an enrollment token
6. emit a post-apply fingerprint
