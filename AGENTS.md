# Agent Operating Instructions

Work issue-first.

Rules:
- One repo, one issue, one PR.
- Inspect the live repository before editing.
- Keep scope bounded to the issue body.
- Do not broaden scope without asking in the issue.
- Do not touch unrelated files.
- Do not claim production readiness unless acceptance criteria prove it.
- Include validation evidence in the PR body.
- Leave known gaps explicit.

PR body must include:
- What changed.
- Exact commands run.
- Pass/fail output summary.
- Known gaps.
- Anything blocked.

Never:
- Commit secrets, tokens, credentials, or private keys.
- Invent release URLs, checksums, SBOMs, or provenance.
- Implement runtime behavior in this repository.
- Duplicate implementation logic that belongs in NLBoot or sourceos-boot.

SourceOS spec-specific rules:
- This repo owns canonical object schemas and normative contracts.
- Keep schemas compact, versioned, and fixture-backed.
- Include positive examples and negative examples where practical.
- Make contracts consumable by NLBoot, sourceos-boot, sourceos-model-carry, Sociosphere, and web/control-plane surfaces.
- Do not claim a schema is implemented elsewhere unless verified.

Validation:
- Use repository-native validation commands if present.
- Add Makefile or schema validation if adding examples.
