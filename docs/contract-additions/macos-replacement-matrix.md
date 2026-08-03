# macOS → SourceOS/SociOS replacement & enhancement matrix

**The census.** The [integrated-agent-native-stack contract](./integrated-agent-native-stack.md)
(sourceos-spec#262) says *how* every surface must be built (feature-modification,
accessibility-by-default, the six seams + purple-team tests, the Noetica
concierge, ontology bindings). This document is the *what*: every stock-macOS app
and subsystem, its SourceOS replacement, the SociOS enhancement that makes it a
**superset** rather than a clone, the enhancement IDs it draws on
([E1–E12](https://github.com/SociOS-Linux/enhancements/blob/main/os/enhancement-matrix.md)),
its third-party dependencies vs a stock macOS deployment, and an honest status.

The rule (from the contract): a replacement is not "done" until it is **agent-native**
(the agent uses the same typed, consented, receipted surface a human does),
**accessible by default**, and **passes its seam's purple-team test**.

## Status legend
`spec` design written · `partial` some code · `built` shipped & agent-native · `gap` not yet specified · `hw` blocked by Apple-silicon hardware (see register)

## Core apps & shell

| macOS | SourceOS replacement | Owning repo | Superiority (why it's a superset) | E-IDs | 3rd-party deps vs stock macOS | Status |
|---|---|---|---|---|---|---|
| Finder | Nautilus (owned SociOS shell integration) + goose-drive | source-os, goose-notes | files are consent-plane surfaces; agent operates them via the a11y seam; every mutation receipted | E1 E4 E7 | GNOME/Nautilus, gvfs | partial |
| Safari / WebKit | **BearBrowser** + LDT-UI (local-render, no remote JS/CSS) | BearBrowser | untrusted web confined to agent-space; local digital-twin UI renders verified components under user policy | E1 E7 | Gecko | partial |
| Mail | prophet-workspace (JMAP) + goose triage | prophet-workspace, goose-notes | local-agent triage/summarize/draft; consent receipts on read/send; office surfaces show their warrant | E2 E3 E4 | JMAP, CalDAV, dovecot/postal | partial |
| Notes | **goose-notes** | goose-notes | agent captures/edits via same typed acts; Guard Goose scan+receipt; voice concierge priority-interrupt | E1 E4 E2 | Rust workspace, whisper.cpp | **built** |
| Terminal | TurtleTerm (Tilix-quake) + sourceos-shell | TurtleTerm, sourceos-shell | command-bus consent-gate on exec (agent denied egress/operate); netwatch System-Graph; agent co-pilot drawer | E1 E4 E7 | wezterm, tmux | **built** |
| Spotlight | **lampstand** launcher | sourceos-shell, lampstand | purpose-gated, slashtag-aware, transparent ranking, receipted; routes through sherlock(IR)/holmes/NewHope | E1 E10 | Albert-class core (owned) | **gap** |
| Messages | owned mesh messaging (Matrix substrate) | sourceos-shell | first-class absorption, no 3rd-party balkanization; runs on the personal mesh | E3 | Matrix/Dendrite (owned deploy) | gap |
| Calendar | CalDAV via prophet-workspace | prophet-workspace | agent schedules with consent + receipts | E2 E3 | CalDAV, radicale | partial |
| Photos | owned media library | *unassigned* | on-device model plane for tagging (governed); no cloud egress by default | E6 E1 | — | **gap** |
| Music | owned player + library | *unassigned* | local-first, no vendor account | — | — | **gap** |
| System Settings | SociOS settings + **[consent/receipts pane](./e11-consent-receipts-ux.md)** | source-os | the consent plane + warrant/receipts are *visible & editable* — the E11 UX macOS never surfaces | E11 E1 | GNOME Settings | spec |
| Preview / Quick Look | owned viewer | *unassigned* | render locally-verified, no remote fetch | E7 | evince/poppler | gap |
| Activity Monitor | **turtle-netwatch** + turtle-diagnose + System Graph | TurtleTerm, hellgraph | processes/sockets become a queryable System Graph; anomalies → consent-gated Governor actions | E1 E4 | ss/lsof, hellgraph | **built** |
| Automator / Shortcuts | agent **App-Intents** (per-app intent ontology) | ontogenesis, agent-machine | intents are purpose-bound + consent-gated, not capability-only | E1 E10 | — | partial |

## System & intelligence subsystems

| macOS | SourceOS replacement | Owning repo | Superiority | E-IDs | 3rd-party deps | Status |
|---|---|---|---|---|---|---|
| Siri + Apple Intelligence | **Noetica voice concierge** | Noetica, goose-voice | native superset: local-agent default, reasoning-backed multi-step, App-Intents bridge, **every action receipted** — the thing Siri cannot do | E2 E6 | whisper.cpp, Ollama, on-node SMLL | partial |
| TCC (privacy prompts) | **consent-plane** (role×surface×space×tool×purpose) | agent-standards, policy-fabric, goose-guard | GDPR-grade purpose-limitation, far finer than TCC; enforced fail-closed at runtime (3 surfaces live) | E1 | — | **built** |
| Sandbox / App Sandbox | **isolation spaces** (kernel/system/user/agent/data-ns) + taints/tolerations | source-os, ontogenesis | k8s-style taints; browser confined to agent-space; data-namespace needs per-tenant + region consent | E7 E1 | seccomp, namespaces, eBPF | partial |
| Gatekeeper / App Store / notarization | **sovereign supply chain** (Guix + zot + signing) | source-os, gitea-sovereign | reproducible builds, SBOM, in-toto/SLSA; no vendor notarization | E5 E8 | Guix, zot, cosign | partial |
| Core ML / Neural Engine | **governed model plane** (labs + eval + ledger + router) | tritfabric, model-router | models promoted through fail-closed gates (SHACL+eval); provenance ledger | E6 | ONNX, Ollama | partial · **hw** |
| Keychain / Secure Enclave | **sovereign identity + digital twin** (TPM/vTPM) | agent-registry, prophet-health | portable, agent-scoped credentials; twin binds identity | E9 | TPM2, vTPM | partial · **hw** |
| Time Machine / Migration Assistant | **sovereign snapshot + backup** | source-os | Guix generations + snapshot/backup to sovereign store (prophet-backups) | E12 E8 | Guix, restic/borg, MinIO | **gap** |
| Software Update | **sovereign OTA** | source-os | signed, reproducible, rollbackable images | E12 E5 | Guix, image-builder | partial |
| Continuity / Handoff / AirDrop | **[personal mesh transport](./e3-mesh-transport.md)** | sourceos-shell (memory-mesh/hellgraph-federated ride as tenants) | cross-device over your WireGuard mesh, not iCloud; every transfer consent-gated + receipted | E3 | WireGuard, Avahi, libp2p | spec |
| Xcode / dev tools | **prophet-cli** (zero-config → continuum + tritfabric) | prophet-cli | one dev entrypoint; sourceos-continuum onboard→dev→test→rollout | E8 | Go CLI | partial |

## Hardware-gap register — where Apple silicon wins, honestly

Spec cannot close these; they are silicon, not software. State them so nothing is over-promised.

| Capability | macOS advantage | SourceOS reality on Asahi (Apple silicon) | Mitigation |
|---|---|---|---|
| **Neural Engine (ANE)** | Core ML offloads to the 16-core ANE | ANE is **not accessible** under Asahi — no driver | Run on CPU/GPU via the governed model plane (E6); accept lower on-device throughput; offload heavy inference to LMS/fog |
| **Secure Enclave (SEP)** | Keychain/biometrics rooted in SEP | SEP **inaccessible** on Asahi | Root identity in **TPM/vTPM** (E9) — portable but not the SEP hardware boundary |
| **HW media codecs** | ProRes/H.265 HW encode/decode | HW codecs **immature** on Asahi | Software codecs; accept CPU cost; document per-format |
| **Display pipeline** | ProMotion/HDR/wide-gamut fully tuned | partial under Asahi/Linux | track upstream Asahi progress |

> These four are the only places the *spec* concedes to macOS. Everywhere else the
> SourceOS surface is a **superset** by being agent-native, consent-governed, and
> receipted — capabilities macOS does not offer at all.

## How to use this matrix
1. Every `gap`/`partial` row is a work item; the highest-leverage gaps are **lampstand** (Spotlight), **owned messaging**, **Photos/Music/Time-Machine**, and completing the **model plane** + **identity** despite the hardware ceiling.
2. A row moves to `built` only when it satisfies the [contract](./integrated-agent-native-stack.md): agent-native + accessible-by-default + its seam's purple-team test passes.
3. `hw` rows can reach `built` in software while remaining honestly capped by the register above.

## Long tail (audit-flagged as unspecified — now enumerated, mostly `gap`)

| macOS | SourceOS replacement | Owning repo | Superiority | E-IDs | Status |
|---|---|---|---|---|---|
| Contacts | CardDAV via prophet-workspace | prophet-workspace | agent reads with consent+receipt; no cloud | E3 E1 | gap |
| Reminders | tasks in goose-notes (Taskwarrior adapter) | goose-notes | agent-created tasks are typed intents + receipted | E1 | partial |
| Maps | owned map surface (offline-first) | *unassigned* | no location egress by default; consent-gated | E1 | gap |
| Weather | investor-insights weather mesh (TWC/IBM cartridge) | investor-insights | governed data cartridge, not a vendor widget | E6 | partial |
| Clock / World Clock | GNOME clocks + agent alarms | source-os | agent alarms are intents | — | gap |
| Home (HomeKit) | citizen-IoT fogstack | fogstack | sovereign IoT, no vendor cloud | E3 | partial |
| Passwords | sovereign identity vault (E9) | agent-registry | agent-scoped, portable; TPM-rooted where available | E9 | gap · hw |
| Screen Time | consent/receipts activity view (E11) | source-os | the operator sees agent+human activity as receipts, not surveillance | E11 E4 | gap |
| Disk Utility | GNOME Disks + snapshot tooling | source-os | snapshots tie to E12 backup plane | E12 | gap |
| Console / logs | telemetry plane + System Graph | hellgraph, telemetry | logs are queryable graph + receipts | E4 | partial |
| FaceTime / Screen Sharing | mesh A/V (owned, Matrix/WebRTC) | sourceos-shell | first-class, on the personal mesh | E3 | gap |
| AirPlay | mesh cast (owned) | sourceos-shell | sovereign cast over the [personal mesh](./e3-mesh-transport.md) (kind=cast) | E3 | spec |
| Dictation | Noetica on-device STT (whisper.cpp) | goose-voice | on-device, no cloud STT (a Guard Goose requirement) | E2 | partial |

> With this, the census enumerates **~37 stock-macOS surfaces** — the full replacement scope. `gap` rows are the feature-gaps-zero backlog; `hw` rows are honestly capped by the register above.
