# Immutable Node Profile Contracts

This contract addition defines the first SourceOS machine-readable surface for immutable Linux node profiles.

## Why this exists

The platform standards layer already defines the general immutable host capability placement grammar. SourceOS needs a contract-native form that downstream implementation repos can validate, render, and emit evidence for.

The key boundary is:

- SourceOS immutable nodes are base substrate profiles.
- Socios capability packs are optional automation commons and must not be required for a base SourceOS node.

## Added schemas

| Schema | Purpose | URN prefix |
|---|---|---|
| `ImmutableNodeProfile.json` | Top-level immutable node profile tying together substrate posture, release refs, host placements, state schemas, validation commands, and optional Socios pack refs. | `urn:srcos:immutable-node-profile:` |
| `HostCapabilityPlacement.json` | Placement declaration for one host capability, service workload, extension, or state root. | `urn:srcos:host-capability-placement:` |
| `NodeStateSchema.json` | Durable state root contract with rollback compatibility and mutability posture. | `urn:srcos:node-state-schema:` |

## Added examples

| Example | Schema |
|---|---|
| `examples/immutablenodeprofile.json` | `schemas/ImmutableNodeProfile.json` |
| `examples/hostcapabilityplacement.json` | `schemas/HostCapabilityPlacement.json` |
| `examples/nodestateschema.json` | `schemas/NodeStateSchema.json` |

## Validation

The focused validator is:

```bash
python3 tools/validate_immutable_node_examples.py
```

A future hygiene pass should wire this into the repository `Makefile` and `schemas/README.md` once the contract slice is accepted.

## Downstream implementation map

| Downstream repo | Expected role |
|---|---|
| `SourceOS-Linux/sourceos-boot` | Consumes boot/release references and coordinates boot/recovery/install/rollback handoff. |
| `SourceOS-Linux/agent-machine` | Renders and validates systemd, Quadlet, state roots, activation decisions, storage receipts, and runtime evidence. |
| `SourceOS-Linux/sourceos-devtools` | Exposes `sourceosctl immutable-node plan|validate|inspect` operator flows. |
| `SocioProphet/agentplane` | Consumes immutable-node activation/runtime evidence and replayable receipts. |
| `SocioProphet/prophet-platform` | Consumes profiles as deployment/FogStack substrate evidence. |
| `SocioProphet/sociosphere` | Registers topology and cross-repo governance edges. |
| `SociOS-Linux/socios` | Optional automation/personalization commons only after explicit enrollment. |

## Non-goals

This tranche does not:

- implement boot execution;
- mutate host state;
- make Socios mandatory;
- replace BootReleaseSet;
- add a production node renderer;
- add CI or Makefile wiring yet.
