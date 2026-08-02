# SourceOS Contract Additions

This directory contains discoverability notes for additive SourceOS/SociOS contract families that extend the canonical schema set without changing the core repository boundary.

| Addition | Purpose | Key schemas |
|---|---|---|
| [Agent Machine Local Data Plane and TopoLVM Mount Contracts](agent-machine-local-data-plane.md) | Defines safe local workspace mounts for Agent Machine and maps the same logical contract to TopoLVM-backed node-local persistent volumes in cluster mode. | `AgentMachineLocalDataPlane`, `AgentMachineMountPolicy`, `TopoLVMPlacementProfile` |
| [Network, Mesh, BYOM, and Native Assistant Door Contracts](network-assistant-model-doors.md) | Defines enterprise/user network profiles, firewall bindings, service-mesh bindings, BYOM model endpoints, and native assistant bridges such as Apple App Intents/Siri/Shortcuts-style integrations. | `NetworkAccessProfile`, `FirewallBindingProfile`, `MeshBindingProfile`, `ExternalModelProviderProfile`, `NativeAssistantBridgeProfile` |
| [Isolation Spaces and Taints](isolation-spaces-and-taints.md) | Makes the consent-plane isolation spaces (kernel/system/user/agent/data-namespace) real at the OS layer: k8s-style taints admitted by role tolerations, with surface `space_deny` as a defence-in-depth cap. The OS enforces what the consent-plane gate admits. | — |

## Rules for additions

- Keep canonical schema files in `schemas/`.
- Keep conforming examples in `examples/`.
- Keep implementation code in the owning implementation repository.
- Do not commit secrets, tokens, private keys, real browser profiles, device-local paths, or user-specific values.
- If an addition creates a new topology lane, link it from Sociosphere and implementation issues rather than duplicating control logic here.
