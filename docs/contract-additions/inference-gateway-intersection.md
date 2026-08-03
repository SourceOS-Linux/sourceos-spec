# InferenceGateway — the cloud ∩ local intersection (model serving)

**Campaign gap #8, done the right way: start at the intersection, then fan out.**
Both the cloud plane (prophet-platform model-fabric / model-router) and the local plane
(sourceos / agent-machine / noetica) serve inference. Rather than build two stacks, define
the capability **once** — the `InferenceGateway` contract — and have each side *adapt* to it.
This is the same pattern as the [ShellBackendAdapter](./agentic-shell-gitea-backend.md)
(github/gitea) and the [consent plane](./e11-consent-receipts-ux.md) (which already spans both).

## The shared seam
| Piece | Shared contract | Cloud adapter | Local adapter |
|---|---|---|---|
| Serve a model | `InferenceGateway.serve(request) → response` | prophet-platform `model-fabric/runtime-adapter-set` | agent-machine provider activation (Ollama / on-node) |
| Per-call receipt | **`GatewayCallAudit`** (memory-mesh `schemas/gateway-call-audit.schema.json`) — already exists | ✔ emit | ✔ emit |
| Admission | consent plane: inference is purpose-bound (a remote model = `egress`) | ✔ | ✔ |

**Request (shared):** `{ model, purpose, space, caller, input, params }`.
**Response (shared):** `{ output, usage, cost_usd?, receipt_hash }` + a `GatewayCallAudit`
(`callId · call_type · outcome · caller · model · usage · occurred_at · receipt_hash`).
A call with no admitting consent decision, or that can't emit an audit, is **refused fail-closed** —
identical rule on both planes.

## Intersection-first, then fan out
1. **Intersection (build first):** open-weight models that run **both** cloud and local
   (Llama, Qwen, DeepSeek, Mistral) + the governance capabilities that span both (consent
   plane, System Graph). These are the client-owned **LLM-stable** — the sovereignty answer.
2. **Fan out — cloud-only:** Claude / GPT via API (supplier + component, not client-owned).
3. **Fan out — local-only:** on-node SLMs, gemma-2-9b (Noetica concierge default, no egress).

## Every model + capability gets a surface across the estate
The [Model Catalog & Leaderboard](../surfaces/model-catalog.html) is the intersection cockpit
screen (cloud∩local placement + a **sovereignty × governance-weighted** leaderboard, not raw
capability alone). Each foundation model and OS capability then fans out to a screen in:
**prophet-platform** (catalog + serving), **prophet lattice** (notebooks), and the
**model leaderboards** — all reading the same `InferenceGateway` catalog + `GatewayCallAudit`
stream, so cloud and local rank on one board.

## Positioning (governs-people vs governs-agents)
The leaderboard's sovereignty/governance weighting encodes the strategy: *Claude Enterprise
governs people; SocioProphet governs agents.* Claude is a **supplier** (API), an **addressable
competitor** (workforce layer, not agentic execution), and a **component** (one engine in the
stable). The LLM-stable reduces supplier-as-future-competitor risk. These competitive claims are
**[DRAFT · VERIFY BEFORE USE]** — require Michael/Gus sign-off before prospect/investor use.

## Done-definition
Shared `InferenceGateway` request/response + `GatewayCallAudit` on every call; a local adapter
(agent-machine) and the cloud adapter (model-fabric) both conform; consent-gated + receipted;
the catalog/leaderboard reads one board across planes. Passes the **inference seam** purple-team
(no un-consented or un-audited call returns output).

## The governed model plane — beyond foundation models
The catalog is not only LLMs. Every **business target** (fraud, churn, credit, AML, propensity)
is a governed model with:
- **Champion / challenger** — the production champion and shadow challenger(s), each with a
  metric (AUC / PR-AUC / Gini / recall). A challenger is promoted only through the eval gate
  (SHACL + eval, fail-closed); a promotion is a `RunReceipt` — replayable, examiner-ready.
- **Historic comparison** — metric by version, champion vs challenger over time; model lineage.
- **Drift** — PSI per target; a breach flags the target and can trip the automaton.
- **DataClass classifiers** — the [trained+registered](./2026-05-agent-machine-model-carry-contracts.md)
  data-catalog classifiers governing each target's data (transaction / merchant / PII / bureau /
  protected-attribute / jurisdiction …), each with coverage + registration status.

Surface: [Model Governance Registry](../surfaces/model-governance.html) — the champion/challenger +
historic + classifier view. Regulated targets (credit, AML) require examiner sign-off before
promotion. This is model risk management (APRA CPS 230 / OCC model-risk) rendered as a witness
surface — the governs-agents thesis made examinable.
