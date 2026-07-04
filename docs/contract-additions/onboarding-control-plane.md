# Onboarding Control-Plane Contract Additions

This note documents the additive SourceOS/SociOS onboarding and agent-workbench control-plane contract family introduced by ADR-0012.

## Contract family

| File | Type | URN prefix |
|------|------|------------|
| `schemas/WorkspaceScope.json` | WorkspaceScope | `urn:srcos:workspace-scope:` |
| `schemas/TrustMode.json` | TrustMode | `urn:srcos:trust-mode:` |
| `schemas/CapabilityPack.json` | CapabilityPack | `urn:srcos:capability-pack:` |
| `schemas/ConnectorActionScope.json` | ConnectorActionScope | `urn:srcos:connector-action-scope:` |
| `schemas/AutomationTemplate.json` | AutomationTemplate | `urn:srcos:automation-template:` |
| `schemas/OnboardingReceipt.json` | OnboardingReceipt | `urn:srcos:receipt:onboarding:` |

These contracts support role/workspace/trust-mode onboarding ceremonies, plugin and capability-pack catalogs, connector action-scope inspection, scheduled automation templates, first-run workspace setup receipts, and SourceOS Shell composer/evidence-rail state.

## Example payloads

| File | Purpose |
|------|---------|
| `examples/workspacescope.json` | Read-only repository workspace boundary for SourceOS spec review |
| `examples/trustmode.read_only_analyst.json` | Low-risk trust envelope with no writes, sends, command execution, or persistent indexing |
| `examples/capabilitypack.repo_release_prep.json` | Draft-only repository release-prep pack composed from skills and GitHub read scope |
| `examples/connectoractionscope.github_read_only.json` | GitHub read-only action scope for repo, PR, and issue reads |
| `examples/automationtemplate.yesterday_git_activity.json` | Daily previous-day Git activity report template |
| `examples/onboardingreceipt.first_run_read_only.json` | First-run onboarding receipt binding role, workspace, trust, capability, connector, automation, trial task, artifacts, and revocation |

## Validation

The family has a dedicated validator:

```bash
make validate-onboarding-examples
```

The target is also wired into the top-level validation lane:

```bash
make validate
```

## Reuse boundaries

This family does not replace existing contracts:

- `AgentSession` remains the session object.
- `ExecutionSurface` remains the runtime, sandbox, network, workdir, worktree, and approval envelope.
- `SkillManifest` remains the narrow skill declaration.
- `Connector` remains the configured local or external connection.
- `Policy`, `PolicyDecision`, `CapabilityToken`, and `Obligation` remain the governance machinery.
- `SessionReceipt` remains the general final session receipt.

The onboarding contracts add the composition and ceremony layer around those primitives.

## Follow-on work

The next implementation slices should add:

- Ontogenesis RDF/OWL/SHACL semantics and validation gates.
- Sociosphere workspace fixtures, registry entries, and onboarding-state-machine validator.
- Agentplane run-envelope and receipt integration.
- SourceOS Shell onboarding UI stubs and composer/evidence-rail binding.
- Prophet Platform evidence-console/API binding for onboarding receipts.

Potential follow-on contracts include `RoleProfile`, `PermissionVocabulary`, `AutomationBinding`, `AutomationRunRecord`, `RevocationRecord`, and `WorktreeScope`.
