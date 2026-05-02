# Agent Machine Local Data Plane and TopoLVM Mount Contracts

This contract addition defines the shared mount semantics for SourceOS Agent Machine local workspaces and their cluster-local TopoLVM analogue.

## Why this exists

Agent Machine needs a safe way to expose useful local disk space to the internal Podman-backed workspace without collapsing host, user, and agent boundaries.

The first local convention is intentionally simple:

| Purpose | Host path | Agent path | Default posture |
|---|---|---|---|
| Code / repositories | `~/dev` | `/workspace/dev` | read/write, explicit grant |
| Generated documents / reports | `~/Documents/SourceOS/agent-output` | `/workspace/output` | read/write, explicit grant |
| Browser downloads | `~/Downloads/SourceOS/agent-downloads` | `/workspace/downloads` | browser read/write, agent read-only |

These are explicit mount roots. They are not a license to mount the whole host home directory.

## New schema types

| Schema | Purpose |
|---|---|
| `AgentMachineLocalDataPlane.json` | Declares logical host-to-agent workspace mounts and their storage backend. |
| `AgentMachineMountPolicy.json` | Declares allow/deny rules, download policy, promotion policy, and mount evidence requirements. |
| `TopoLVMPlacementProfile.json` | Maps the same logical mount contract to TopoLVM-backed node-local persistent volumes in cluster mode. |

## Local mode

In local macOS/Windows/Linux Agent Machine mode, the mount path is:

```text
host OS -> Podman machine / WSL / native Podman -> agent container
```

Mac mode does not use TopoLVM directly. The host filesystem is APFS and the Agent Machine boundary is the Podman machine/container mount contract.

## Cluster mode

In Linux cluster mode, the same logical mount contract can be realized by TopoLVM-backed local persistent volumes:

```text
cluster node local disk -> TopoLVM PVC/PV -> agent workspace pod/container
```

TopoLVM provides topology-aware local persistent volumes. It should not be described as a cross-node shared filesystem. If SourceOS later needs cross-node shared semantics, those should be modeled as a replication or mesh-storage layer above or adjacent to TopoLVM.

## Security invariants

- Deny by default.
- Do not mount `$HOME` wholesale.
- Do not mount `~/.ssh`, `~/.gnupg`, browser profiles, keychains, cloud credentials, token stores, password stores, or app databases by default.
- Browser downloads use a scoped downloads directory, not the whole host `~/Downloads` folder.
- Downloaded artifacts are hashed and recorded in evidence.
- Moving downloads into code or document-output space is an explicit promotion action with its own evidence record.
- Notes, Reminders, Photos, Voice Memos, and TextEdit-style surfaces are future App Doors, not default raw filesystem mounts.

## Example files

| Example | Description |
|---|---|
| `examples/agent_machine_local_data_plane_macos.json` | macOS/Podman defaults for `~/dev`, document output, and scoped browser downloads. |
| `examples/agent_machine_mount_policy_default.json` | deny-by-default mount policy with sensitive path denylist and downloads promotion policy. |
| `examples/topolvm_placement_profile_agent_machine.json` | cluster-local TopoLVM placement profile for code, output, and downloads volumes. |

## Implementation owners

| Repo | Role |
|---|---|
| `SourceOS-Linux/sourceos-spec` | Canonical schemas and examples. |
| `SourceOS-Linux/sourceos-devtools` | Local CLI implementation via `sourceosctl agent-machine mounts ...`. |
| `SociOS-Linux/workstation-contracts` | IPC/conformance receipts for mount broker behavior. |
| `SocioProphet/agentplane` | Execution evidence consumption and placement metadata. |
| `SocioProphet/sociosphere` | Workspace topology, dependency direction, and validation lanes. |
| `SocioProphet/topolvm` | Cluster-local storage backend reference and documentation mapping. |

## Current status

This addition is contract-first. The next implementation step is to teach `sourceosctl` to render, inspect, validate, and apply these mount profiles in dry-run mode before any host mutation is introduced.
