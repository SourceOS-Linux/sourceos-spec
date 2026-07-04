> ⚠️ **UNAPPROVED DRAFT — strategy brief, not endorsed.** Working analysis produced in a
> 2026-07-02 session. Assumes an unconfirmed Gulf channel; success metrics are proposed, not
> agreed. Do not cite or act on without review. See `README.md` in this folder.

# Gulf-Finance lighthouse brief

**Design partner:** a SAMA (Saudi) or UAE-central-bank–regulated bank
**The bet being tested:** that *correctness attestation* — proving a computation is **right**, not just that it ran privately — is a felt buyer need **today**, not ahead of the market.
**Binds to:** `economic-prophet` / `open_ep_framework` (do not reinvent). **Runs in-region.** **Emits evidence on the reasoning spine.**

---

## 1. Why this cell (recap)

Finance-Gulf tied Finance-India at the top of the design-partner matrix (4.35) on the thesis-making axes — localization force, correctness pain, verified-compute differentiation — and won the tiebreak on **entry speed + capital**: sovereign Gulf buyers are funded, fast, and have an explicit AI-sovereignty appetite right now. Finance (not health) because its correctness pain is **numeric** — the home turf of the dimensional/sympy gate — and because `open_ep_framework` is our strongest existing asset fit.

## 2. The workload (bound to real modules)

A bank's **regulatory profitability + capital computation** — the numbers it must defend to the regulator — run end to end on the existing engine:

| Regulatory obligation | `open_ep_framework` module | What is computed |
|---|---|---|
| IFRS 9 Expected Credit Loss | `expected_loss.py` | ECL = PD × LGD × EAD, staged |
| Basel III capital charge | `capital.py` | RWA-driven capital requirement |
| Funds Transfer Pricing | `ftp.py` | risk-adjusted funding cost |
| Economic profit / RAROC | `product_objects.py`, `attribution.py` | EP after capital charge; return on risk-adjusted capital |
| Zero-EP / breakeven pricing | `breakeven.py` | the price that makes EP = 0 |
| Recovery surface | `recovery.py` | LGD recovery modeling |
| Audit trail | `audit.py`, `validation.py` | the existing evidence surface we extend |

These are exactly the figures a Gulf bank must **prove** to SAMA / the UAE central bank, **in-country**, on a recurring reporting cycle. The pain is not hypothetical — it is a standing regulatory obligation with penalties.

## 3. What the correctness gate proves that TEE cannot

This is the whole wedge. A confidential-computing (TEE) competitor can prove the ECL job *ran privately on unmodified code inside a sealed enclave*. It proves **nothing about whether the ECL number is right**. Our dimensional/sympy correctness gate proves the computation is **valid**:

- **Dimensional consistency** — PD is dimensionless [0,1]; LGD is dimensionless [0,1]; EAD and ECL are currency; the product's units must reconcile to currency. A unit error (e.g. a bps/decimal confusion in LGD) is caught and blocked, not silently reported to the regulator.
- **Identity/invariant checks** — capital ratios in range, EP = revenue − cost − capital-charge reconciles, breakeven solve satisfies EP = 0 on replay.
- **Replayable proof** — the gate emits a receipt that lets the regulator (or internal audit) *re-derive* the number, not just trust that it ran.

> **The sentence no hyperscaler can say:** "This ECL/capital figure was computed **where your data is governed**, and here is a **replayable proof that the number is correct** — not merely a proof that it ran privately."

## 4. Sovereignty posture

- Executes at **`locus = trusted_private`** (in-region, in-bank) — reuses the `SyncCycleReceipt.locus` vocabulary already in sourceos-spec.
- No cross-border transfer of customer/exposure data → satisfies the sector-specific localization that actually binds in the Gulf (SAMA/UAE central bank), independent of the softer transfer-permitting privacy regime.
- The local model does the reasoning; the correctness gate + canon do the proving. Confidential computing (TEE) is used as the **confidentiality channel**, not the differentiator.

## 5. Evidence emitted

Extend the engine's existing `audit.py` output onto the reasoning-evidence spine:
- a `ReasoningRun` per computation cycle (status → `completed`/`blocked`),
- a **correctness receipt** (the gate result) referenced from each reported figure,
- bound to the existing `policy_simulation_uvmc_audit.json`-style audit artifact.
This makes the regulatory pack **replayable**, not just signed.

## 6. Falsifiable success metric (this IS the risk test)

The lighthouse succeeds iff **the bank's risk/finance team treats the correctness receipt as decision-relevant** — i.e. one of:
1. they run a real reporting-cycle ECL or capital figure through the gate and it **catches a defect** they would otherwise have filed, OR
2. they state the replayable proof **reduces their regulatory-review / audit burden** (a signed statement, not a vibe).

If neither happens, the honest read is that correctness is ahead of the market (the Musketeer risk) — and we learn that from *one* partner in weeks, not from more desk research.

## 7. Thin PoC scope (what to actually build)

Deliberately small — this tests demand, not capability:
1. Wire the **dimensional/sympy gate** around `expected_loss.py` + `capital.py` (two engines, not all seven).
2. Emit the **correctness receipt** + `ReasoningRun` from `audit.py`.
3. Run one **synthetic-but-realistic** SAMA/IFRS-9 portfolio in-region; demonstrate a caught unit/identity defect on a seeded-error variant.
4. One-page **regulator-facing replay demo**: "here is the number, here is the proof, re-derive it."

Everything else in `open_ep_framework` (FTP, recovery, attribution, UVMC) is out of PoC scope — pull in only after the wedge is validated.

## 8. Honest risks / caveats
- ⚠ **Assumed no existing Gulf channel.** If there is a relationship, PoC-to-signature compresses sharply. Confirm first.
- The gate's value depends on the bank's figures having **derivable structure** to check (ECL/capital do; some downstream adjustments are judgmental overlays the gate can't validate — scope to the mechanical core).
- Sovereign procurement can still be slow even when appetite is high; a **design-partner PoC** (not a sale) is the right first vehicle to stay fast.
- Regulator acceptance of a "replayable proof" as audit-reducing is itself unproven — success metric #2 is the softer of the two; prioritize #1 (catch a real defect).
