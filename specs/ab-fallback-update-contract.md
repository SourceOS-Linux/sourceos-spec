# A/B Fallback Update Contract v0.1

Status: v0.1 (tranche strictness bar). Program: TRUST FABRIC W9.2.

## Why this family

The estate ships updates to fog nodes, to installed applications, and to itself,
and until this contract there was **no path back from a bad one anywhere in it**.
The closest thing that exists is generation-based: `sourceos-syncd` applies a
`nixos-rebuild switch`, a `sourceos-health-check.timer` fires at `OnBootSec=120s`,
and on failure it shells out to a rollback that infers its target as "the highest
non-current generation". That is a heuristic standing in for a recorded pointer,
and it has three holes that no amount of care closes:

1. **No attempt bound.** If the candidate never reaches userspace, the health
   timer never fires, so nothing reverts it. The failure mode that most needs
   automatic fallback is the one the mechanism cannot observe.
2. **No candidate marking.** Nothing records which payload is on trial, so
   "roll back" means "guess backwards" rather than "return to the slot that
   passed".
3. **No confirm step.** A health pass is fire-and-forget. Nothing promotes a
   candidate or pins a last-known-good, so the difference between "this worked"
   and "this has not failed yet" is never written down.

The lesson taken is EVE-OS's: GRUB GPT priority-boot plus dual watchdogs — never
ship an update you cannot brick with. This family lands that shape as a contract
so the OS-image path and the application-update path use one vocabulary instead
of two, and so the rollback path is a recorded transition rather than an inference.

## Schemas

| Schema | Role |
| --- | --- |
| `UpdateSlot` | One of exactly two slots on a target. Carries the GPT attribute triple (`bootPriority`, `triesRemaining`, `successful`) the slot selector reads, the digest of the payload installed, and the role/running split. |
| `UpdateTransaction` | One attempt to move a target from the active payload to a new one. Records the write target, the pinned probe, every boot attempt and where it fell back to, and which slot the target ended on. |
| `UpdateHealthProbe` | The digest-pinned definition of what a candidate must prove before promotion: a non-empty check set with at least one blocking check, and a mandatory hardware+software watchdog pair. |

## The invariant

> **The currently-good slot is never overwritten by the update being applied.**

It is enforced in three independent places, on purpose, because it is the only
property whose violation is unrecoverable:

- **By schema, within one document.** `UpdateTransaction` carries a top-level
  `not`/`anyOf` clause enumerating the two illegal `(fromSlot, toSlot)` pairs.
  The slot set is closed to exactly two, so the illegal set is finite and the
  constraint is expressible in JSON Schema rather than deferred to a runtime
  check a caller can forget. `UpdateSlot` adds the same rule from the other side:
  `state: "writing"` requires `role: "candidate"`.
- **By schema, on the settle path.** Four if/then clauses pin `settledOnSlot` to
  `toSlot` on promotion and to `fromSlot` on rollback or refusal. A failed update
  leaves the target where it started, and that is decided by the contract rather
  than by the operator writing the record.
- **Across documents, by the validator.** `tools/validate_ab_update_examples.py`
  asserts that a settled transaction's `preservedPayloadDigest` still equals the
  active slot's `payloadDigest`. This is the executable form of the invariant, as
  opposed to an assurance that it holds. A mutation test in the same tranche
  confirms it fires.

## State machine

`UpdateTransaction.outcome` is the terminal projection of this machine. The
reference implementation is `AbUpdateMachine` in `sourceos-boot`
(`src/sourceos_boot/ab_update_machine.py`).

| From | Event | To | Slot effects |
| --- | --- | --- | --- |
| `idle` | `begin(payload)` | `writing` | candidate → `writing`; **active untouched** |
| `writing` | `write_complete(digest match)` | `candidate_ready` | candidate → `written` |
| `writing` | `write_complete(digest mismatch)` | `rolled_back` (`digest-mismatch`) | candidate → `unbootable`; active retained |
| `writing` | `write_failed` | `rolled_back` (`write-failed`) | candidate → `unbootable`; active retained |
| `candidate_ready` | `arm()` | `armed` | candidate `bootPriority` > active, `triesRemaining = maxAttempts`, `successful = false` |
| `armed` | `boot_attempt()` | `trying` | bootloader decrements `triesRemaining` **before** handing over control |
| `trying` | `probe_pass()` | `promoted` | candidate → `good`, `successful = true`, roles swap; **previous payload retained bootable at lower priority** |
| `trying` | `probe_fail()` \| `watchdog_expired()` (tries remain) | `armed` | fall back to active; candidate stays armed |
| `trying` | `probe_fail()` \| `watchdog_expired()` (tries exhausted) | `refused` | candidate → `unbootable`, `bootPriority = 0`; target stays on active |
| `armed` \| `trying` \| `candidate_ready` | `operator_abort()` | `rolled_back` (`operator-abort`) | candidate → `unbootable`; active retained |

`refused` is terminal on purpose. It is the state that ends the boot loop, and a
system without it retries a fatal payload forever. `promoted` is terminal for the
same reason in the opposite direction: a machine that keeps trying after a pass
has not understood that promotion is the end.

Attempt accounting follows the GPT attribute rather than a software counter:
`triesRemaining` is decremented by the bootloader **before** control transfers, so
a payload that hangs before userspace still consumes an attempt. A counter
decremented after a successful boot never terminates for a payload that cannot
reach userspace — which is exactly the boot loop this contract exists to forbid.

## Probe digest (normative)

`UpdateHealthProbe.definitionDigest` is:

```
sha256( canonical_json({ checks, evaluatedIn, minConsecutivePasses,
                         onProbeUnavailable, timeoutSeconds, watchdogs }) )
```

where `canonical_json` is `json.dumps(..., sort_keys=True, separators=(",", ":"))`.
The projection covers the check and watchdog objects **entire, descriptions
included**: an exclusion list is somewhere to hide a weakening, and the cost of
re-pinning after a comment edit is far below the cost of a gate that can be edited
without the pin noticing. `UpdateTransaction.healthProbeDigest` records this value
at open. If the probe is edited while a transaction is in flight, the digests
diverge and the family validator rejects the pair — which is what stops a failing
candidate being promoted by relaxing the gate it failed.

## Deliberate deltas from the source patterns

1. **Dual watchdogs are mandatory, not recommended.** `watchdogs` requires at
   least one `hardware` and one `software` entry, enforced by two `contains`
   clauses. Neither kind alone closes the gap: a software watchdog cannot fire
   through a wedged kernel, because the process that would notice is the process
   that is stuck; a hardware watchdog only ever learns whether something petted
   it, so it cannot distinguish a live-but-broken payload from a healthy one.
   Requiring both is what makes "hung" and "running but failing" terminate in the
   same automatic fallback. The software timeout must be shorter (validator), so
   the software watchdog gets the first, attributable word.
2. **The bootloader may not declare its own success.** `evaluatedIn` is closed to
   `post-boot-userspace` and `successful` is set only by userspace. A bootloader
   can observe that control transferred and nothing more; a design that lets the
   boot path mark its own boot good has no gate at all.
3. **An inconclusive probe is a failure.** `onProbeUnavailable` is closed to
   `fail`. Reading "could not determine" as "proceed" is the declared-unenforced
   gap applied to the one control standing between a target and a brick.
4. **Two slots, closed.** `slot` is `A`/`B` and not an open label set. The
   fallback guarantee is that one slot is retained known-good while the other is
   written, and that argument does not generalise to N without a new arbitration
   rule. A third slot is a contract change, not a new enum value.
5. **Role and running are separate fields.** During a trial boot the candidate is
   executing while the active slot is still the fallback. Collapsing the two makes
   the fallback slot indescribable at exactly the moment it matters.
6. **Promotion retains the slot it replaces.** After promotion the previous active
   becomes the candidate but keeps `successful: true` and a non-zero priority
   until it is overwritten by the next update. The check set includes a
   `rollback-capability` kind for the same reason: promotion is the moment the
   previous payload stops being the guaranteed way back, so the ability to go back
   is verified *before* it is spent, not after.
7. **Every rollback is attributed.** `rollbackReason` is a closed set and is
   required whenever the outcome is `rolled-back` or `refused`. An unattributed
   rollback teaches nothing and is indistinguishable from one that was never
   diagnosed.

## Repo placement

| Layer | Repo | Delivers |
| --- | --- | --- |
| L0 | `sourceos-spec` | these normative schemas + fixtures (this document) |
| L1 | `sourceos-boot` | `AbUpdateMachine` reference implementation + `sourceos-boot ab-update` CLI surface |
| L2 | `sourceos-syncd` | emits `UpdateTransaction` from its apply path; `check-health` becomes the probe runner |
| L3 | `source-os` | GPT A/B partition layout + GRUB priority-boot slot selector; the `sourceos.syncd.slots.*` NixOS option surface |
| L4 | `Noetica` | application-update consumer once an updater exists (see below) |

**L3 is where hardware enters and where this contract stops being testable in
software.** `source-os/scripts/install-image.sh` currently creates two partitions
(512M ESP + a single rootfs). An A/B layout needs a second rootfs slot and a GRUB
config that reads the priority attributes. That work is real and is not in this
tranche; nothing in it is verifiable without booting a machine, and a test that
claims to verify a bootloader without one would be worth less than no test.

**L4 has no updater to consume this.** Noetica ships no `tauri-plugin-updater`,
no `updater` block in `tauri.conf.json`, and distributes via Homebrew cask. Its
own `docs/WORKPLAN-111-gaps.md` records this as ship-blocker #77: *"No Tauri
auto-updater at all — no in-app updates, no rollback, brew-only."* The contract is
written to cover it (`targetRef` is any `urn:srcos:` URN, and the example set
includes an application target) but there is nothing on that side to wire yet.

## Conformance

`fixtures/ab-update/conformance.json` holds fourteen negative vectors. Each MUST
FAIL validation for its stated reason, and `tools/validate_ab_update_examples.py`
fails the build if any of them validates. They are negative by construction and
live in `fixtures/`, never in `examples/`.

Run: `make validate-ab-update-examples`.

## Open items

- **OI-1** GRUB slot-selector implementation and the A/B partition layout (L3).
  Requires a hardware or VM boot loop to verify; explicitly out of the v0.1
  tranche.
- **OI-2** `bootPriority` is typed 0–15 after the GPT attribute width. If a target
  ever needs a non-GPT selector (an application updater, say), the field keeps its
  ordering semantics but loses its hardware meaning. Left as-is rather than
  abstracted early.
- **OI-3** `UpdateTransaction.receiptRef` is optional at v0.1. Once targets emit
  into the reasoning-evidence fabric it should become required for any
  transaction that mutates a slot.
