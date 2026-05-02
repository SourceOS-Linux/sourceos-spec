# Network, Mesh, BYOM, and Native Assistant Door contracts

This contract addition defines the SourceOS boundary for enterprise networking, user firewalls, service mesh integrations, bring-your-own-model endpoints, and native assistant bridges such as Apple App Intents/Siri/Shortcuts.

## Why this exists

Enterprise customers need SourceOS Agent Machine, Office Plane, Local Model Door, and external model routing to respect corporate firewall and service-mesh policy. Individual users also need their own local firewall and model-provider profiles.

These cannot be ambient privileges. Network and assistant integrations must be declared as profiles and connected to evidence, model routing, policy, and consent.

## New schema types

| Schema | Purpose |
|---|---|
| `NetworkAccessProfile.json` | Precedence-aware user/enterprise/device/workspace network policy stack. |
| `FirewallBindingProfile.json` | Host, user, enterprise, and cluster firewall binding plan/import profile. |
| `MeshBindingProfile.json` | Istio/Admiral/Linkerd/Cilium/Kubernetes mesh-policy binding profile. |
| `ExternalModelProviderProfile.json` | BYOM and enterprise model endpoint profile, including endpoint, auth reference, firewall/mesh refs, and route policy. |
| `NativeAssistantBridgeProfile.json` | Native assistant integration profile for Apple App Intents/Siri/Shortcuts, Android, Windows, browser extensions, and future host/device bridges. |

## Profile separation

SourceOS must support multiple simultaneous network profiles:

- corporate firewall profile;
- workspace profile;
- device profile;
- user firewall profile;
- agent/workload profile;
- model-provider profile.

Default precedence should be:

```text
enterprise -> workspace -> device -> user -> agent -> model-provider
```

A user profile may be stricter than enterprise policy, but must not override enterprise denies.

## Firewall and mesh posture

Mesh policy and firewall policy are complementary.

Istio egress gateways route traffic through mesh-controlled exit points and allow monitoring/routing policy on traffic leaving the mesh. However, mesh sidecars can be bypassed unless external enforcement such as network policy or firewall controls prevent non-gateway egress. Therefore SourceOS models both:

```text
MeshBindingProfile + FirewallBindingProfile
```

## BYOM posture

Bring-your-own-model endpoints are first-class provider profiles. They can represent user-private endpoints, enterprise-private endpoints, or cloud model providers.

Rules:

- endpoint auth is always a reference, never an inline token;
- prompt egress is denied by default unless policy allows it;
- training use is denied by default;
- hosted fallback requires model-router and network-policy approval;
- provider route decisions emit evidence.

## Native assistant posture

Apple integration should use App Intents/App Shortcuts style surfaces, not raw Siri plumbing. SourceOS capabilities should be exposed as declared intents such as:

- open workroom;
- create office artifact;
- summarize;
- route local model;
- inspect evidence;
- hand off to Agent Machine.

Native assistant bridges must remain policy-gated:

- local-only by default;
- no prompt egress by default;
- no raw app database access;
- no side effects without confirmation;
- cross-device handoff disabled unless explicitly granted;
- prompt evidence should be hash-only/redacted.

## Examples

| Example | Purpose |
|---|---|
| `examples/network_access_profile.enterprise_and_user.json` | Enterprise and user profile stack with precedence. |
| `examples/firewall_binding_profile.macos_lulu_user.json` | macOS user firewall planning profile for LuLu-style outbound control. |
| `examples/firewall_binding_profile.enterprise_gateway.json` | Enterprise gateway firewall import/enforcement profile. |
| `examples/mesh_binding_profile.istio_admiral_enterprise.json` | Istio/Admiral-style enterprise mesh egress profile. |
| `examples/external_model_provider_profile.byom_openai_compatible.json` | User BYOM OpenAI-compatible endpoint profile. |
| `examples/native_assistant_bridge_profile.apple_app_intents.json` | Apple App Intents/Siri/Shortcuts-style native bridge profile. |

## Implementation owners

| Repo | Role |
|---|---|
| `SourceOS-Linux/sourceos-spec` | Canonical network/firewall/mesh/BYOM/native assistant contracts. |
| `SourceOS-Linux/sourceos-devtools` | Future `sourceosctl network ...` and `sourceosctl native-assistant ...` probe/plan surface. |
| `SocioProphet/model-router` | Route external model providers and BYOM endpoints under local/enterprise policy. |
| `SocioProphet/agentplane` | Network/model-provider/native-assistant evidence. |
| `SocioProphet/sociosphere` | Topology validation and dependency direction. |
| `SociOS-Linux/socios` | Opt-in orchestration where network/model/native assistant flows touch personalization workflows. |
| `SocioProphet/guardrail-fabric` | Policy decision/evidence authority for prompt egress and side effects. |

## Non-goals

- Do not vendor Istio, Admiral, LuLu, Cilium, or enterprise firewall implementation here.
- Do not store firewall credentials, VPN secrets, API keys, or model-provider tokens.
- Do not claim a mesh policy alone prevents bypass; firewall/network policy must be modeled too.
- Do not expose raw Apple app databases, Photos libraries, Notes stores, mail stores, browser profiles, keychains, or token stores by default.
