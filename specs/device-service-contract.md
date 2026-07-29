# DeviceService Contract v0.1 — the southbound device plane (W8.7)

Status: v0.1.0 (normative for the schemas listed below)
Validation: `make validate-device-service-examples` (tools/validate_device_service_examples.py).
Reference implementation: `device-service` in `SocioProphet/prophet-platform` (`apps/device-service`).

## 1. Scope — the gap this closes

The estate had **no southbound device abstraction anywhere**. The health twin
ingests batch corpora; the smart home has nothing; a Δt<50ms twin sync is
aspirational for the simple reason that no sensor stream exists to be late.

EdgeX Foundry's lesson is the fix, and it is a lesson about *shape*, not about
adopting EdgeX: **ONE southbound interface, N protocol drivers.** A driver's job
is to speak a protocol. It is emphatically not to invent a vocabulary — the
moment each driver defines its own event shape, every consumer downstream grows
a per-driver special case and the "device plane" is a directory of adapters
rather than a plane.

This contract lands that one interface as two types:

| Schema | What it is |
|--------|-----------|
| `DeviceProfile` | What a device **is**: identity, protocol, protocol binding, and the exact set of readings it produces with units, value types, operating ranges, and protocol-native source addresses. |
| `DeviceReading` | One **observation**: a metric's value, in a declared unit, at a declared instant, with a declared quality — and the provenance that makes those words mean something. |

## 2. The normative invariant: a reading is attributable or it is nothing

> An unattributable reading is the silent-wrong we keep paying for.

A bare number with a timestamp is not data. It is a number with a timestamp.
`DeviceReading` therefore **requires** the whole attribution set — there is no
optional path to an anonymous value:

| Field | What it answers | Why required |
|-------|-----------------|--------------|
| `deviceRef` | *which physical thing* | Two identical sensors in two rooms are not interchangeable. |
| `deviceProfileRef` | *under what declaration* | The profile is what makes the number mean a temperature. |
| `profileDigest` | *which revision of that declaration* | §3. |
| `metric` | *which of the device's readings* | A device produces several. |
| `sourceAddress` | *off which physical channel* | Proves the value came from the declared characteristic/register/topic, not an adjacent one. |
| `unit` | *in what units* | §4. |
| `quality` | *how much to believe it* | §5. |
| `observedAt` | *when the sensor saw it* | §6. |

`tools/validate_device_service_examples.py` resolves every one of these across
the example set: the profile must exist, the digest must match, the metric must
be declared, the unit and source address must agree with the declaration, the
value must be of the declared type and inside the declared range, and
`provenanceLinks` must independently name both the device and the profile — so
the attribution survives being read by something that is not this validator.

## 3. Digest-pinning: a range cannot be widened after the fact

`DeviceProfile.definitionDigest` is `sha256` over the canonical JSON (sorted
keys, no whitespace, UTF-8) of the declared-capability projection
`{deviceClass, protocol, metrics}` of the document **as written** — schema
defaults are not materialised, so an omitted field and an explicitly-defaulted
one are different declarations and hash differently.

Every `DeviceReading` carries the digest of the profile revision it was actually
admitted against. This closes a specific attack that a plain `profileRef` leaves
wide open: a reading fails the declared range, so somebody widens the range.
With digest-pinning, widening the profile produces a new digest and **orphans**
the readings it was meant to legalise instead of silently admitting them — the
mismatch is detectable forever after.

This deliberately mirrors `UpdateHealthProbe.definitionDigest` from the A/B
fallback update family (W9.2), where the same construct stops a failing
candidate from being promoted by weakening the gate it failed. The validator
**recomputes** the digest rather than reading it back: a digest that is merely
stored is an assertion about pinning; a digest that is recomputed is pinning.

## 4. One envelope, not two — and one unit, stated twice

`DeviceReading` is a structural profile of the `ConversationEvent` envelope,
exactly as the MPCC trading families are: `actorRef`, `workspaceRef`,
`branchRef`, `visibilityScope`, `wallTime`, `logicalTime`, `causalParents`,
`traceContext`, `provenanceLinks`, `policyLabels`, `riskLabels` are carried with
**byte-identical sub-schemas**, and the validator fails the build on any drift.
`DeviceProfile` carries the registry subset of the same vocabulary (no event
time, no causality — a profile is declared, not observed).

`specVersion` is deliberately **excluded** from the parity set: it is the
per-family contract version by construction, and the strictness bar pins it to
the `0.1.0` const instead. Rationale for structural profiles over `allOf`
composition is unchanged from `specs/mpcc-event-contract.md` §2 — this repo
requires `additionalProperties: false` everywhere, which `allOf` envelope reuse
cannot express in draft 2020-12 without `unevaluatedProperties`.

**`unit` is stated on both the profile and every reading, on purpose.** The
redundancy is the point: consumers read readings, not profiles, and a value
whose unit must be looked up elsewhere is a unit-confusion incident waiting for
a deployment. The validator enforces the equality, so the redundancy cannot
become a disagreement.

## 5. Quality is closed, and absence is typed

`quality` is a closed five-value enum:

| Value | Meaning |
|-------|---------|
| `ok` | Measured, within specification. |
| `degraded` | Measured, but the driver has cause to doubt it. |
| `stale` | A cached prior value re-reported because the device did not answer in time. |
| `substituted` | A value supplied by something other than the device (a default, an interpolation). |
| `unavailable` | No value. The device produced nothing. |

Normative: **`stale` and `substituted` are not `ok`, and `substituted` is not
measured.** Conflating them is how a smart-home twin comes to believe a default
is a measurement, and then how a health twin does.

`unavailable` is schema-bound (`if`/`then`/`else`) to `value: null` **and** a
non-null `nullAbsenceRef` pointing at a `NullAbsenceRecord`. The device plane
does not get its own absence taxonomy: it reuses the existing 12-kind MPCC one,
so a `timeout` is never conflated with a `transport_failure` or an
`intentional_silence`. Symmetrically, a non-`unavailable` reading may not carry
a null value — an untyped hole wearing a measured quality is exactly the defect
the taxonomy exists to prevent.

## 6. Three timestamps, because they measure three different things

`observedAt` (the instant at the sensor) → `receivedAt` (arrival at the
DeviceService) → `wallTime` (the producer's event time on the envelope).
`observedAt` → `receivedAt` **is** the southbound latency a twin's sync budget is
actually spent on. Collapsing them into one field hides the only number that
would tell you whether a Δt target is met, which is why the family carries all
three and the validator enforces `receivedAt >= observedAt`.

## 7. Simulated devices are first-class and must stay visible

`protocol: "virtual"` denotes a simulated device with no physical counterpart.
It is a **named member of the taxonomy**, not an omission, and the validator
enforces the labelling in both directions: a virtual profile must carry the
`synthetic:simulated-device` policy label, a physical one may not, and every
reading must agree with its profile.

This is the `KnowledgeNugget` `model-generated` rule applied to sensors:
generated data that is indistinguishable downstream is worse than no data,
because it is *believed*. A simulated reading that reaches a twin unmarked is a
fabricated measurement.

## 8. Reading only, at v0.1

`metrics[].access` is closed to `"read"`. Commanding a device is a
world-changing effect and must travel the MPCC `EffectRequest` →
`EffectDecision` → `EffectRecord` lifecycle. Admitting actuation through a
widened enum here would hand every protocol driver unreviewed physical
authority over a citizen's home — the southbound *read* plane is deliberately
the only thing this contract grants.

## 9. Overlap decisions (spec-first conformance)

| Existing contract | Decision |
|-------------------|----------|
| `DeviceIdentity` | **Not duplicated, and not the same thing.** `DeviceIdentity` governs admission, attestation and trust for a SourceOS operator workstation; it says nothing about metrology. `DeviceProfile.identityRef` points at the registered host that owns the southbound link, binding the two families instead of competing. A negative vector pins this: a reading may not attribute itself to a `urn:srcos:device-identity:` URN. |
| `TelemetryEvent` | Distinct concern: a diagnostic/log event emitted during an `AgentSession` (`sessionRef` is required). It is software telemetry, not a physical observation, and has no unit, range, quality or device. Untouched. |
| `ConversationEvent` | The envelope authority. `DeviceReading` profiles it (§4). |
| `NullAbsenceRecord` | Reused verbatim for `unavailable` readings (§5). No device-local absence vocabulary exists. |
| `EffectRequest` / `EffectDecision` | The path any future device *command* must travel (§8). Not duplicated here. |
| `KnowledgeNugget` | Shares the `kkoTypeRef` ontology-URI vocabulary, so a reading is graph-typed on the same terms as a content grain. A reading is not a nugget: it is an observation, not a warrant-typed assertion about a document. |
| Fog plane (`Topic`/`Offer`/`WorkOrder`/`Receipt`/`Settlement`) | No overlap despite the shared word. That family is the FogCompute *marketplace*; this is sensor fog. |
| `EventEnvelope` | Unchanged wire wrapper; `DeviceReading` is a payload-plane domain object that rides inside it. |

## 10. Versioning

The family versions as one contract, pinned by the `specVersion` const `0.1.0`.
Additive optional fields or widened enums bump the minor; anything that can
invalidate an existing document bumps the major, with CHANGELOG + ADR per
CONTRIBUTING.md.

## 11. Known gaps (deliberate, v0.1)

- **No `Device` instance registry.** `DeviceProfile` describes a device *model*;
  `DeviceReading.deviceRef` names an *instance* by a `urn:srcos:device:` URN
  that has no schema of its own yet. In v0.1 the DeviceService owns the
  instance→profile binding in its commissioned-device table, and the reading
  makes that binding auditable by carrying both refs plus the digest. A typed
  `Device` registry (admin/operating state, last-seen, commissioning receipt,
  instance→profile binding checkable *outside* the producing service) is the
  first follow-on. This is the same house convention as `ConversationEvent`'s
  free-form `actorRef`/`workspaceRef`/`branchRef` — a stable reference now, a
  typed contract when the names have settled.
- **No command/actuation path** (§8), by design.
- **No device discovery or provisioning contract** — how a device comes to have
  a profile is out of scope; the profile is an input at v0.1.
- **No OpenAPI/AsyncAPI operations or semantic-context mappings yet**, matching
  how the MPCC, KnowledgeNugget and A/B-update families landed; wiring follows
  once names have settled.
- **Ontology typing is coarser than the metric.** `kkoTypeRef` cites the KKO
  upper ontology (`http://kbpedia.org/ontologies/kko#`), which is the ontology
  this estate actually vendors — 169 terms, verified. The ~58k KBpedia
  reference-concept layer that would carry a concept as specific as
  *temperature* is **not** vendored, so a numeric metric types as `Quantity`
  and a boolean state as `States`, with the metric name and unit carrying the
  specificity. Citing `.../kko/rc/Temperature` would look more precise and be
  an unresolvable reference — the same class of silent-wrong this contract
  exists to prevent. Nothing currently resolves these IRIs against a loaded
  KKO either; the platform-wide TBox binding is a separate tracked gap
  (`nugget-extractor` states the same).
- **No aggregate/derived-reading type.** Downsampling, windowing and unit
  conversion produce new observations whose provenance rules are not yet stated;
  emitting them as `DeviceReading`s would launder a computation into a
  measurement.
