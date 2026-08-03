# Sovereign Shell Assembly — how the OS is built from the parts

The build index for the SociOS/SourceOS agentic shell: every component the
[feature-gaps-zero campaign](https://github.com/SourceOS-Linux/sourceos-spec/issues/267)
produced, its owning repo, and where it plugs into the [source-os](https://github.com/SourceOS-Linux/source-os)
image build. Read with the [census](./macos-replacement-matrix.md) (the *what*) and the
[integrated-agent-native-stack contract](./integrated-agent-native-stack.md) (the *how*).

## Components (built this campaign)
| Component | Repo | Kind | Integration point |
|---|---|---|---|
| Consent plane (spaces/purposes/gate) | agent-standards · policy-fabric · goose-guard · ontogenesis | runtime + ontology | enforced at 3 surfaces; TCC replacement |
| lampstand (parse + router) | sourceos-shell `tools/lampstand_*` | service logic | Spotlight replacement; routes to IR + consent |
| MeshTransfer (E3) | sourceos-shell `tools/mesh_transfer` | schema + gate | Continuity/AirDrop; `sourceos-shell` mesh service |
| netwatch (System Graph) | TurtleTerm `turtle-netwatch` | agent | Activity Monitor replacement; ingests to hellgraph |
| Canonical surfaces (7) | sourceos-spec `docs/surfaces/` | UI + tokens | E11 pane, B₁₁ automaton, launcher, turn-witness, framework, genesis/flywheel |
| Surface feeds + producer | sourceos-spec `docs/surfaces/data` + `tools/build_surface_feed.py` | live-state seam | surfaces read feeds; `provenance` LIVE/SAMPLE |
| E12 OTA + backup | (spec) `e12-ota-backup.md` | generation lifecycle | Software Update + Time Machine replacement |

## Vendored dependencies (consumed, not forked)
Pinned by release + verified by `tools/verify_vendor.py` (recomputes the deterministic
`git archive` sha512). A pin that can't be verified is a build failure.

| Dep | Pin | Why vendored | Lock |
|---|---|---|---|
| **hellgraph** (System Graph) | `v0.4.45` (`dbe854f`) · MIT | not our lane — netwatch ingests into it; surface feeds read from it | `vendor/hellgraph.lock.json` |

> Rule: hellgraph is **consumed vendored**, never modified here. Bump the pin by
> re-running `verify_vendor.py --checkout <path>` against a new release tag.

## Build order (bottom-up)
1. **Base** — measured boot (Heads + dm-verity) seals the image (Atzilut). *(source-os)*
2. **Substrate** — vendored hellgraph (System Graph) + telemetry. *(vendored + source-os)*
3. **Governance** — consent plane loaded; taints/tolerations active (fail-closed). *(agent-standards/policy-fabric)*
4. **Shell services** — lampstand, mesh transfer, netwatch, goose. *(sourceos-shell/TurtleTerm)*
5. **Surfaces** — E11/B₁₁/launcher/turn-witness wired to feeds. *(sourceos-spec/docs/surfaces)*
6. **Update lifecycle** — E12 OTA + backup generations. *(source-os)*

Each layer is fail-closed and receipted; a layer that can't verify the one below it
does not come up. This is the buildable spine referenced by the census and E12.

## What remains to a bootable image
- Package the shell components into the source-os workstation profile (a NixOS/Guix
  module) + a contract test that the flake evaluates. *(source-os; verified by `nix build`)*
- E12 update-tree implementation + measured-boot attestation. *(source-os)*
- Local model serving (E2/E6) for the Noetica concierge. *(agent-machine)*
