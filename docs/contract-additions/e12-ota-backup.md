# E12 — Sovereign OTA + Snapshot/Backup (Software Update + Time Machine)

**Gap #5 of the [feature-gaps-zero campaign](https://github.com/SourceOS-Linux/sourceos-spec/issues/267).**
Replaces two macOS subsystems at once — **Software Update** (OTA) and **Time Machine /
Migration Assistant** (backup/restore) — with a signed, reproducible, rollbackable
generation model. No vendor cloud; every update and every restore is consent-gated and
receipted, and a failed verify rolls back fail-closed.

## Update model — signed atomic generations
An update is a new **generation** of the reproducible image tree (Guix generations /
Nix profiles), never an in-place mutation. It follows the [B₁₁ change loop](../surfaces/b11-life-mirror.html)
exactly:

| Step | What | Fail-closed rule |
|---|---|---|
| **A · stage** | fetch a signed image; verify signature + provenance (SLSA/in-toto) | unsigned or unverifiable ⇒ refuse, never staged |
| **B · verify** | boot-test the generation; run the eval gate; the twin re-mirrors the new surface set | any check red ⇒ **auto-rollback** to the last sealed generation |
| **Q · commit** | owner consent (QR / present-owner) commits the generation as default-boot | no consent ⇒ hold on the current generation |

The base is sealed by **measured boot** (PureBoot/Heads + dm-verity) — the Atzilut
seal in the framework. A tripwire trip *during* an update drives the automaton to
SAFE-HALT and hands recovery to the present owner.

## Backup model — generations to a sovereign store
- **Snapshot:** each generation + user-space state snapshots to a sovereign store
  (prophet-backups / MinIO via restic/borg), encrypted, agent-scoped, region-tolerated
  (GDPR Ch. V — same residency rule as the consent plane).
- **Restore / migrate:** restoring is *booting a prior generation* — Migration Assistant
  parity without a vendor account. Diff any two generations before committing a restore.

## Governance
An OTA is `purpose = administer` (commit) / `ship` (publish an image); a restore is
`operate`. All are consent-gated + emit an `AutonomyAdmissionReceipt` bound to the
generation hash. The runtime enforcement is the same [consent plane](./e11-consent-receipts-ux.md);
the surface is the E11 pane (an update shows as a pending consent with its warrant).

## Superiority over macOS
- **Reproducible + rollbackable** — every update is a content-addressed generation you can
  diff and revert; Software Update is neither.
- **Receipted** — each update/restore is a sealed receipt with its warrant; macOS shows a spinner.
- **No vendor cloud** — backups live in *your* sovereign store, not iCloud.

## Done-definition
Signed atomic update-tree + measured-boot attestation + snapshot/restore of a generation,
all consent-gated + receipted; passes the **update seam** purple-team test (no path commits
an unsigned, unverified, or un-consented generation as default-boot).

## Non-goals
Not a package manager (that's Guix/Nix underneath) and not a general file-sync product —
E12 is specifically the *update + backup/restore generation lifecycle* and its governance.
