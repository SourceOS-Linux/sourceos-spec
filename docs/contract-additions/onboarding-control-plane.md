# Onboarding Control-Plane Contract Additions

This note records the additive SourceOS/SociOS onboarding control-plane contract family.

## Contract family

| File | Type | URN prefix |
|------|------|------------|
| `schemas/WorkspaceScope.json` | WorkspaceScope | `urn:srcos:workspace-scope:` |
| `schemas/TrustMode.json` | TrustMode | `urn:srcos:trust-mode:` |
| `schemas/CapabilityPack.json` | CapabilityPack | `urn:srcos:capability-pack:` |
| `schemas/ConnectorActionScope.json` | ConnectorActionScope | `urn:srcos:connector-action-scope:` |
| `schemas/AutomationTemplate.json` | AutomationTemplate | `urn:srcos:automation-template:` |
| `schemas/OnboardingReceipt.json` | OnboardingReceipt | `urn:srcos:receipt:onboarding:` |

## Example payloads

| File | Purpose |
|------|---------|
| `examples/workspacescope.json` | Read-only repository workspace boundary for SourceOS spec review |
| `examples/trustmode.read_only_analyst.json` | Low-risk read-only trust envelope |
| `examples/capabilitypack.repo_release_prep.json` | Draft-only repository release-prep pack |
| `examples/connectoractionscope.github_read_only.json` | GitHub read-only action scope |
| `examples/automationtemplate.yesterday_git_activity.json` | Daily previous-day Git activity report template |
| `examples/onboardingreceipt.first_run_read_only.json` | First-run onboarding receipt tying the selected objects together |

## Validation

Run:

```bash
python tools/validate_onboarding_examples.py
```

The focused CI workflow is `Onboarding Control Plane`.

## Reuse boundaries

This family adds a composition layer around existing SourceOS primitives. It does not replace the session, surface, skill, connector, policy, decision, capability-token, obligation, or receipt families already present in the spec.

## Follow-on work

Next implementation work belongs in downstream runtime and product repositories after the schema family stabilizes here.
