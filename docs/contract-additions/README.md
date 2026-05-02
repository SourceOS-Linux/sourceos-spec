# SourceOS Contract Additions

This directory contains discoverability notes for additive SourceOS/SociOS contract families that extend the canonical schema set without changing the core repository boundary.

| Addition | Purpose | Key schemas |
|---|---|---|
| [Agent Machine Local Data Plane and TopoLVM Mount Contracts](agent-machine-local-data-plane.md) | Defines safe local workspace mounts for Agent Machine and maps the same logical contract to TopoLVM-backed node-local persistent volumes in cluster mode. | `AgentMachineLocalDataPlane`, `AgentMachineMountPolicy`, `TopoLVMPlacementProfile` |

## Rules for additions

- Keep canonical schema files in `schemas/`.
- Keep conforming examples in `examples/`.
- Keep implementation code in the owning implementation repository.
- Do not commit secrets, tokens, private keys, real browser profiles, device-local paths, or user-specific values.
- If an addition creates a new topology lane, link it from Sociosphere and implementation issues rather than duplicating control logic here.
