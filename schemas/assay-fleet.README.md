# Assay Fleet Tier (cloud-mesh)

The node-tier Assay contracts (`ReasoningAssay`, `AssayStandard`) describe a verdict on a
single claim on a single node. The **fleet tier** adds the two contracts a cloud-mesh operator
needs and a single node cannot produce, and it is the boundary between the two prophet-mesh
deployment modes.

## Deployment modes

| | Single-user local | Cloud mesh (fleet) |
|---|---|---|
| locus | `local` / `trusted_private` | `attested_fog` / `burst_cloud` |
| node verdicts | `ReasoningAssay` stays on device | `ReasoningAssay` emitted per node |
| aggregation | self-view only (`AssayRollup` scope `node`) — optional | `AssayRollup` scope `cohort` / `fleet` |
| rollout | nothing to roll out | `AssayStandardRollout` across cohorts |
| dashboards | **none** | fleet + per-node views (external surface) |

"No fleet dashboards for a single user" is a **structural** property, not a permission: on-device the
fleet/cohort aggregation path is not built, so there is nothing to display and nothing to leak. Only
the cloud-mesh deployment instantiates the rollup/rollout tier.

## Schemas

| Schema | URN prefix | Purpose |
|---|---|---|
| `AssayRollup.json` | `urn:srcos:assay-rollup:` | Fleet/cohort aggregate of verdicts over a window: ok/sad/bad distribution, calibration-drift view (which `AssayStandard` versions are live across the fleet), and the unassayed-reason breakdown. |
| `AssayStandardRollout.json` | `urn:srcos:assay-standard-rollout:` | Governs promoting a new `AssayStandard` version across cohorts — canary first, widen or halt on the observed `AssayRollup`. Rides the release-bundle + lifecycle machinery. |

## Examples

| Example | Schema |
|---|---|
| `examples/assay_rollup.json` | `AssayRollup` (fleet scope, drift detected) |
| `examples/assay_standard_rollout.json` | `AssayStandardRollout` (canary widening on an observed rollup) |

## Enforced invariants

`tools/validate_assay_fleet_examples.py` checks aggregation and rollout soundness, not just schema shape:

- a rollup's `ok`/`sad`/`bad` counts sum to `totalAssays`; `unassayedReasons` cannot exceed the `sad` band;
  `standardAdoption` node counts match `scope.nodeCount`; `driftDetected` must agree with the adoption table;
- a rollout's `rolloutPct` matches its promoted/observing node share; `guard.decision` is consistent with `phase`;
  and a rollout may not have widened past canary without an observed `AssayRollup` — **no promotion-by-hope**.

## The rollup → rollout loop

A new `AssayStandard` version is not switched on fleet-wide at once — that would silently re-project every
node's verdicts against an unproven judge. The rollout advances a canary cohort, the canary emits an
`AssayRollup`, and `guard.decision` reads that rollup to `continue` / `hold` / `rollback`. Promotion is
gated on measured fleet evidence — the same "measured, not asserted" discipline the node tier applies to a
single claim, applied to a fleet-wide change.
