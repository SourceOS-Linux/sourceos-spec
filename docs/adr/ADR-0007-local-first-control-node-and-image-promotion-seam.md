# ADR-0007 — Local-first control node and image promotion seam

Status: Proposed

## Context

We now have a concrete working control-node prototype on macOS that proves the operator-side envelope for SourceOS and SociOS Linux work:

- nix-darwin-managed host configuration on the operator machine
- Podman machine + OCI image build/push/run path
- Artifact Registry push path for `node-commander`
- user-scoped launchd agent wiring for a local control/runtime helper

That work is valuable, but it is not yet canonically placed in the typed-contract stack. Without an explicit contract boundary, Linux image generation, image validation, node control, and issue/task promotion risk being implemented as local glue rather than shared SourceOS contract surfaces.

The current repo topology already separates concerns:

- `sourceos-spec` is the typed-contract / canonical spec lane
- `SociOS-Linux/source-os` is the workstation/profile/bootstrap lane
- `SocioProphet/agentplane` is the execution control-plane and evidence lane
- `SocioProphet/prophet-platform` is the runtime / deployable service lane

This ADR reserves the local-first control-node and image-promotion seam in that topology.

## Decision

### 1. Local-first is a contract rule, not a weak preference

Control-node and image-validation placement follows a hard ordering:

1. local operator machine / local eligible executor
2. trusted private Linux builder or owned cluster
3. attested fog executor
4. burst cloud only when explicitly enabled by policy

This ordering is part of the SourceOS/SociOS contract posture and should not be reduced to a mere cost-weighting preference.

### 2. The control node is a distinct contract surface

We reserve a contract family for the operator-side control node. The control node is responsible for:

- building or dispatching candidate image builds
- launching validation scenarios
- staging the Node Commander runtime
- emitting evidence that determines whether a candidate build may update a Git repository and mark a task complete

This family is not fully machine-readable yet, but its first contract objects are expected to include:

- `ControlNodeProfile`
- `NodeCommanderRuntime`
- `ImagePromotionGate`
- `BuildValidationEvidenceBundle`

### 3. Node Commander is a runtime role, not the canonical contract home

`Node Commander` is the small operator-side runtime/agent responsible for local node command, OCI execution, and first-step orchestration. It may be packaged as a local binary or OCI image, but its canonical meaning belongs upstream in the spec lane, not only in host-specific bootstrap code.

The initial runtime assumptions are:

- user-scoped execution on the operator node
- Podman / OCI first
- explicit config, state, and evidence directories
- no Docker-specific dependency in the canonical path
- evidence-bearing execution suitable for downstream promotion gating

### 4. Image promotion is evidence-gated

A SourceOS or SociOS Linux candidate build may not update the relevant Git repository and may not mark an issue/task done until promotion gates pass.

At minimum, the promotion seam must be able to express:

- build identity and provenance
- target profile / image identity
- scenario results
- validation receipts
- policy decision inputs and outputs
- promotion decision
- reversal / rollback reference when applicable

This ADR reserves that seam in the typed-contract lane even though the exact machine-readable schemas will follow in later PRs.

### 5. Repo ownership split

This ADR fixes the current ownership split:

- `SourceOS-Linux/sourceos-spec`
  - canonical typed contracts and ADRs for control-node and image-promotion concepts
- `SociOS-Linux/source-os`
  - workstation/bootstrap application of the operator-node profile
- `SocioProphet/agentplane`
  - downstream execution, placement, validation, replay, and evidence consumption
- `SocioProphet/prophet-platform`
  - deployable runtime implementations once Node Commander and adjacent services stabilize

## Consequences

### Positive

- prevents local operator-node work from remaining orphaned implementation glue
- gives Linux image generation and validation a canonical contract lane
- gives `agentplane` a clear downstream seam for promotion/evidence consumption
- gives `source-os` a clear downstream seam for workstation/control-node bootstrap

### Constraints

- this ADR does not itself add schemas
- this ADR does not declare Docker helper behavior canonical
- this ADR does not move runtime implementation ownership into `sourceos-spec`

## Follow-on work

1. Define the first machine-readable starter schemas for:
   - `ControlNodeProfile`
   - `NodeCommanderRuntime`
   - `ImagePromotionGate`
   - `BuildValidationEvidenceBundle`
2. Bind the downstream execution/evidence consumption seam in `SocioProphet/agentplane`.
3. Bind the workstation/bootstrap application seam in `SociOS-Linux/source-os`.
4. Bind runtime implementation work in `SocioProphet/prophet-platform` once the real Node Commander implementation replaces the current bootstrap placeholder.
