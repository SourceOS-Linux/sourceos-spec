Use the GitHub issue body as the source of truth.

Before editing:
1. Read the issue.
2. Inspect the repository.
3. Identify existing validation commands.
4. Keep the PR bounded.

When implementing:
- Prefer existing schema and documentation patterns.
- Add examples and validation with schema changes.
- Keep this repository normative: schemas, contracts, examples, and docs only.
- Do not implement runtime behavior here.
- Do not duplicate implementation code from NLBoot or sourceos-boot.

When opening the PR:
- Link the issue.
- Include validation evidence.
- List known gaps.
- State non-goals preserved.
- Do not mark ready if validation did not run.
