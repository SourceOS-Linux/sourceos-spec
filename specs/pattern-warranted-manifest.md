# SP-PATT-WARR-001 — Pattern-Warranted Agent Manifest Pipeline

**Status:** DRAFT v0.1.0 · normative artifacts landed in `sourceos-spec`
**Owner:** SocioProphet / Platform Architecture
**Depends on:** SCOPE-D (`epistemicLevel`), Mellumwork (ternary falsification), HellGraph (typed-atom kernel), PolicyFabric (PEP), AgentPlane (execution binding), agent-registry (declaration surface)
**Patent adjacency:** P-02/agentplane, P-04/consent-bound revocation

This document is the spec-repo home of SP-PATT-WARR-001. It binds the design to concrete
JSON Schemas under `schemas/` and to conformance fixtures under `fixtures/pattern-warrant/`.
Implementations across the estate conform to these artifacts; they do not re-derive them.

## `$id` normalization (spec-first)

The design draft used `https://schema.socioprophet.ai/...` URIs. The canonical
`sourceos-spec` convention is `https://schemas.srcos.ai/v2/<Name>.json` with a `type`
const discriminator, a `specVersion` string, and `additionalProperties: false`. All
artifacts below follow the repo convention, not the draft URIs.

| Draft entity | Schema |
|---|---|
| `CandidateManifest/v1` (§4) / `ManifestAtom` (§5) | `schemas/CandidateManifest.json` |
| `EvidenceAtom` (§2.1) | `schemas/EvidenceAtom.json` |
| `PatternAtom` (§5) | `schemas/PatternAtom.json` |
| `ConsentAtom` (§5) | `schemas/ConsentAtom.json` |
| `AttestationAtom` (§5) | `schemas/AttestationAtom.json` |
| `WarrantEdge` (§5) | `schemas/WarrantEdge.json` |
| warrant lattice (§1.3, §2.2, §3) | `schemas/WarrantLattice.json` + `examples/warrant-lattice.default.json` |
| abstention event (§3.3 corollary) | `schemas/AbstentionEvent.json` |

## Invariants (conformance-tested at every layer)

- **SP-PW-I1 — evidence-informed, never evidence-authorized.** No value of any
  evidence-derived score grants execution authority. Evidence determines only (i) whether a
  manifest may be *proposed* and (ii) which attestation quorum is *required*. Authority is
  granted exclusively by signed attestations meeting `Q(C)`.
- **SP-PW-I2 — no collapse.** `ZERO` is never rendered as `NEG` at any surface (enforcement,
  logging, approver UI). A decayed warrant is reduced authority under live uncertainty, not a
  failure. Collapsing `ZERO → deny` reintroduces the binary-threshold pathology this pipeline
  exists to remove.

## Grant predicate (§1.4)

```
Grant(m, t) ⟺ Declared(m)
            ∧ Attested(m, Q(C(m)))
            ∧ W_p(pattern(m), t) ≥ minW(C(m))
            ∧ ¬Revoked(evidence(m), t)
```

`Declared` and `Attested` are one-shot, monotone. The last two conjuncts are evaluated
continuously; their falsification lowers the operating **ceiling** (per capability), it does
not revoke the declaration.

## Response mapping (§3.3)

| Ternary | Condition | Response |
|---|---|---|
| `POS` | `W_p ≥ minW(C)` | operate at declared class `C` |
| `ZERO` | `W_p < minW(C)`, no NEG | ceiling reduction to `C' = max{ c : minW(c) ≤ W_p }`; over-ceiling ops return an `AbstentionEvent`, not an error; flag for re-attestation |
| `NEG` | falsifying test attested | suspend; return to declaration gate; prior attestations retained |

## Repo placement (build order)

| Layer | Repo | Delivers |
|---|---|---|
| L0 | `sourceos-spec` | these normative schemas + fixtures (this document) |
| L1 | `hellgraph` | atom types + `WarrantEdge` (decoupled module; no kernel edits) |
| L2 | `scope-d` | decomposable-aggregate scorer, concentration cap, decay, hysteresis, ternary map |
| L3 | `mellumwork` (new) | ternary falsification harness — POS/ZERO/NEG source |
| L4 | `agent-registry` | declaration + attestation quorum gate; approver surface (§8) |
| L5 | `policyfabric` (new) | PEP: live `W_p` consult, per-capability ceiling, abstention path |
| L6 | `agentplane` | execution binding, honors per-capability ceiling |
| L7 | `prophet-mesh`/`noetica` | evidence capture consumer over existing provenance stream |

## Open items (resolutions carried into build)

- **OI-1** `θ_up`/`θ_down` and `quorum.minAttestors` in `examples/warrant-lattice.default.json`
  are placeholders pending a scoring-function choice. The lattice schema treats `thetaUp`/
  `thetaDown` as open objects until L2 fixes the scorer. Dwell values (`d_up=7d`, `d_down=2d`)
  and decay half-lives are normative now.
- **OI-2** `C3` retains the `PROVED` requirement. `C3` automation is rare by construction; the
  `machineDerivedExempt` cap is the only path to `PROVED` without behavioral diversity.
- **OI-3** No cross-tenant evidence aggregation without an explicit grant. Deferred to its own
  work order; the `principal`/`consentToken` fields carry enough to gate it later.
- **OI-4** ZERO/abstention rates feed the SP-EVAL-CRF-001 abstention-calibration headline
  metric. `AbstentionEvent` is the emission surface for that feed.

## Threat model (§7) — schema-enforced points

- Synthetic usage manufactures warrant → `WarrantLattice.concentrationCaps` (§2.2).
- Warrant laundering (promote under C0, re-declare at C3) → `consequenceClass` immutable
  post-declaration; a class change is a new manifest with a new quorum.
- Evidence-set substitution post-attestation → `evidenceSetDigest` bound into the signed
  `AttestationAtom` payload.
- Consent revocation used to infer participation → SP-PW-R3: revocation-induced demotion is
  indistinguishable from decay-induced demotion at the enforcement surface.

## Conformance

See `fixtures/pattern-warrant/conformance.json` for the §9 test vectors T1–T7. Every
implementing layer runs them; T7 (ZERO never serialized as NEG) is mandatory at L4/L5/L6.
