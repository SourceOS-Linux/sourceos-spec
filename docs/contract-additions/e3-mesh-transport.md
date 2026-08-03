# E3 — Personal Mesh Transport (Continuity / Handoff / AirDrop / AirPlay parity)

**Gap #3 of the [feature-gaps-zero campaign](https://github.com/SourceOS-Linux/sourceos-spec/issues/267).**
Apple Continuity requires an Apple ID and routes trust through iCloud. E3 is the
**sovereign personal mesh**: your devices form one fabric with **no vendor cloud**, and
every cross-device transfer is an `egress`-purpose act — **consent-gated and receipted**
(the thing Continuity cannot show you).

Spec home: `sourceos-spec`. Implementation home: **`sourceos-shell`** (owns Messages/FaceTime/AirPlay).
Memory sync (`memory-mesh`) and graph federation (`hellgraph-federated`) are **tenants** of this
transport, not the transport itself.

## Layered model
| Layer | Concern | Substrate | Sovereign point |
|---|---|---|---|
| **L0 Identity** | per-device keypair, twin-rooted | E9 identity + TPM/vTPM where present | device identity is yours, not an Apple ID |
| **L1 Discovery** | who's on my mesh, on this LAN / over WAN | mDNS/Avahi (LAN) + a signed rendezvous record (WAN) | no vendor directory; discovery is authenticated |
| **L2 Fabric** | encrypted device-to-device links | WireGuard mesh; libp2p for NAT traversal / relay | E2E by construction; relays see ciphertext only |
| **L3 Transfer primitives** | Handoff / AirDrop / AirPlay / message | typed `MeshTransfer` envelopes over L2 | every transfer is consent-gated `egress` + receipted |
| **L4 Tenants** | memory sync, graph federation, Messages, FaceTime | `memory-mesh`, `hellgraph-federated`, `sourceos-shell` A/V | ride L3; inherit its consent + receipt guarantees |

## The `MeshTransfer` envelope (normative, schema to follow)
```
{ transfer_id, kind: handoff|drop|cast|message|sync,
  from_device, to_device, purpose: "egress",
  payload_ref, payload_class,          // e.g. clipboard | file | app-state | av-stream
  consent: { granted_by, space, region }, // consent-plane decision that admitted it
  receipt: "sha256:…" }                // AutonomyAdmissionReceipt seal
```
- **kind=handoff** — app-state continuation (open-here). **=drop** — file/clipboard (AirDrop parity).
  **=cast** — A/V stream to a mesh sink (AirPlay parity). **=message** — Matrix substrate.
  **=sync** — a `memory-mesh`/`hellgraph-federated` delta.
- A transfer with no admitting consent decision is **refused fail-closed** — there is no
  "just this once" bypass; instead the receiver's E11 pane shows a pending prompt.

## Consent binding (build, don't rebuild)
Every `MeshTransfer` runs the same `policy-fabric purpose_admissibility_gate.decide()` as any
egress: `purpose=egress`, `surface=mesh`, `space` = the sending app's space, `region` toleration
required to cross a jurisdiction. A cross-device drop out of `data-namespace` needs tenant **and**
`region` tolerations (GDPR Ch. V) — identical to the [E11](./e11-consent-receipts-ux.md) residency rule.

## Superiority over Continuity (why it's a superset)
- **No vendor cloud / no account** — the fabric is WireGuard between *your* devices.
- **Every transfer receipted** — Continuity is invisible; here each Handoff/AirDrop is a sealed
  receipt in the E11 timeline with its warrant.
- **Purpose-bound** — an agent cannot silently exfiltrate via "Handoff"; it's `egress`, gated.
- **Heterogeneous** — any device that speaks the fabric joins (not just Apple hardware).

## Done-definition
- `MeshTransfer.v0.1.json` schema + a `sourceos-shell` service that forms the WireGuard fabric,
  discovers peers, and moves a **file drop** end-to-end between two devices — consent-gated + receipted.
- The receipt lands in the E11 timeline; a denied transfer shows a pending prompt, never silent success.
- Passes the **egress seam** purple-team test (no transfer path renders un-consented data as delivered).

## Non-goals
Not a VPN product, not a public overlay — a *personal* mesh (your devices + explicitly invited peers).
Public federation between *estates* is `hellgraph-federated`'s concern, riding L2 as a tenant.
