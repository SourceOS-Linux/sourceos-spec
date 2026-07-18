# ADR-0012: Onboarding Control-Plane Contracts

**Date:** 2026-05-05
**Status:** `Accepted`
**Deciders:** SourceOS-Linux/sourceos-spec maintainers

---

## Context

SourceOS/SociOS needs a local-first, auditable agent workbench where roles, workspaces, trust modes, capability packs, connector action scopes, automation templates, artifacts, and receipts are visible, scoped, revocable, and machine-readable.

Claude-style onboarding demonstrates a useful role-first ceremony: choose role, add plugins/connectors/skills, confirm working context, and finish with a calm progress rail. Codex-style workbench surfaces demonstrate the project/workspace grammar: local mode, branch context, permission defaults, plugin/skill catalogs, connector cards, and scheduled automation templates.

SourceOS should not copy casual toggle semantics. The SourceOS/SociOS contract layer must make capability activation explicit, signed or policy-backed where required, scoped to a workspace, revocable, and receipted.

## Decision

Introduce an additive onboarding and agent-workbench control-plane family:

| Schema | URN prefix | Purpose |
|--------|------------|---------|
| `WorkspaceScope` | `urn:srcos:workspace-scope:` | Selected workspace, repository, folder, organization, fog workspace, or sandbox boundary |
| `TrustMode` | `urn:srcos:trust-mode:` | User-visible permission envelope expressed as explicit verbs |
| `CapabilityPack` | `urn:srcos:capability-pack:` | Curated bundle of SkillManifest refs, connector scopes, policy refs, expected artifacts, and revocation behavior |
| `ConnectorActionScope` | `urn:srcos:connector-action-scope:` | Exact connector verbs and side-effect class allowed for a configured Connector |
| `AutomationTemplate` | `urn:srcos:automation-template:` | Reusable scheduled, manual, evented, or conditional work-product template |
| `OnboardingReceipt` | `urn:srcos:receipt:onboarding:` | Receipt proving what was selected, enabled, disabled, scoped, trialed, and made revocable |

These schemas bridge the existing Workstation, Governance, Execution/Provenance, and Agent Plane families. They are additive and SemVer-minor compatible.

## Reuse of existing contracts

This family intentionally does not replace existing primitives:

- `AgentSession` remains the concrete session object.
- `ExecutionSurface` remains the runtime, sandbox, network, workdir, worktree, and approval envelope.
- `SkillManifest` remains the narrow skill declaration.
- `Connector` remains the configured connection to a local or external system.
- `Policy`, `PolicyDecision`, `CapabilityToken`, and `Obligation` remain the governance decision and grant machinery.
- `SessionReceipt` remains the general final receipt for completed sessions.

The new schemas add composition and ceremony layers around those primitives so onboarding can produce a draft `AgentSession`, bind it to a `WorkspaceScope` and `TrustMode`, activate compatible `CapabilityPack` and `ConnectorActionScope` refs, optionally enable `AutomationTemplate` refs, and emit an `OnboardingReceipt`.

## Canonical ceremony state machine

The intended first-run state machine is:

1. `S0_BOOTSTRAP`
2. `S1_ROLE_PROFILE`
3. `S2_WORKSPACE_SCOPE`
4. `S3_TRUST_MODE`
5. `S4_CAPABILITY_PACKS`
6. `S5_CONNECTOR_ACTION_SCOPES`
7. `S6_AUTOMATION_TEMPLATES`
8. `S7_AGENT_SESSION_DRAFT`
9. `S8_TRIAL_TASK`
10. `S9_RECEIPT_REVIEW`
11. `S10_READY`
12. `S11_REVOKE_OR_RESET`

## Consequences

### Positive

- SourceOS Shell can render first-run onboarding and composer/evidence-rail state from contracts.
- Sociosphere can validate workspace-scope compatibility before materializing workspace or automation bindings.
- Agentplane can execute only after `AgentSession` and `ExecutionSurface` bindings exist and can include onboarding refs in run and replay artifacts.
- Ontogenesis can add RDF/OWL/SHACL semantics for trust modes, capabilities, connector scopes, automation templates, and receipts.
- Prophet Platform can index and display onboarding receipts as evidence objects.
- Connector enablement is no longer vague; action scopes distinguish read, draft, write, comment, send, publish, merge, destructive, and control classes.

### Constraints

- SourceOS Shell UI implementation is out of scope for this repository.
- Runtime enforcement belongs in SourceOS Shell, Sociosphere, Agentplane, and downstream execution surfaces.
- Capability-pack marketplace review, signatures, and license policy are modeled here but enforced downstream.
- Advanced follow-on contracts such as `RoleProfile`, `PermissionVocabulary`, `AutomationBinding`, `AutomationRunRecord`, `RevocationRecord`, and `WorktreeScope` remain follow-up work.

## Non-goals

- Do not implement UI in `sourceos-spec`.
- Do not replace `AgentSession`.
- Do not replace `ExecutionSurface`.
- Do not replace `SkillManifest`.
- Do not replace `SessionReceipt`.
- Do not make connector toggles equivalent to write authority.
- Do not make scheduled chats equivalent to governed recurring work products.

## Validation

This slice adds `tools/validate_onboarding_examples.py` and wires it into `make validate` through `validate-onboarding-examples`.

## References

- `schemas/WorkspaceScope.json`
- `schemas/TrustMode.json`
- `schemas/CapabilityPack.json`
- `schemas/ConnectorActionScope.json`
- `schemas/AutomationTemplate.json`
- `schemas/OnboardingReceipt.json`
- `tools/validate_onboarding_examples.py`
