# Image Trust — measured, not asserted

The Assay pattern, applied to images. `AssayStandard` measures a *verifier's* reliability so a
claim can only project `ok` behind a measured judge. **`ImageTrustReport` measures an *image's*
checks so `ImagePromotionGate` can only `approve` behind measured, gate-eligible evidence.** An
image — OS or agent — cannot declare itself trustworthy.

## Schemas

| Schema | URN prefix | Purpose |
|---|---|---|
| `ImageTrustReport.json` | `urn:srcos:image-trust:` | Per-dimension measured trust checks + a render-time `projectedTrust` verdict. Unifies OS and agent images via `subjectKind`. |
| `AgentImage.json` | `urn:srcos:agent-image:` | Agent runtime-artifact identity + provenance, parallel to `OSImage` (distinct from `AgentPassport`, which classifies a running process). |
| `ImagePromotionGate.json` | `urn:srcos:image-gate:` | Now requires a `trustReportRef` when `decision: approved` — an approval must be backed. |

## How it reuses, not reinvents

- Each check carries a **`Measurement`** (`$ref: Measurement.json`). Measurement's own invariants
  therefore apply for free: a `declared`/`assumed` measurement is gate-ineligible by shape, and a
  `measured` one must name its `instrument`. A trust check cannot smuggle in an asserted number.
- `measured_boot` is fed by the existing `BootProofRecord` / `AttestationEvidence`; `attestation_verify`
  and `signature_verify` record the *outcome* of verifying `OSImage.provenance` / `AgentImage.provenance`
  refs, which by themselves are only pointers.

## The projection (executable, CI-enforced)

`projectedTrust` is recomputed from the checks by `tools/validate_image_trust_examples.py`, which fails
if the recorded value doesn't follow:

- **`bad`** — a gate-eligible measurement recorded a failure (`passed: false`).
- **`ok`** — every check is gate-eligible **and** passed.
- **`sad`** — otherwise: a `declared`/`derived`/`assumed` or partly-`unobserved` check, none failed.
  Honest pending-work (`unmetReason` names the dimension), not soft failure.

And the gate rule: an `ImagePromotionGate` with `decision: approved` must reference an `ImageTrustReport`
that projects `ok` — the cross-document half the schema's `if/then` can't express. This closes, for
images, the same self-assertable-approval gap the Assay hardening (F2) closed for verifiers.

## Examples

| Example | Projects |
|---|---|
| `examples/image_trust_report.os.json` | `ok` — OS image, all checks measured + gate-eligible |
| `examples/image_trust_report.agent.json` | `sad` — agent image with a *declared* SBOM (not measured) |
| `examples/agent_image.json` | an `AgentImage` |
| `examples/image_promotion_gate.json` | `approved`, backed by the OS report |
