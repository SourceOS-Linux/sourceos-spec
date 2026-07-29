#!/usr/bin/env python3
"""Validate the DeviceService contract family (W8.7 — the southbound device plane).

Seven checks, not one:
  1. schema conformance — both schemas are valid draft-2020-12 documents and
     every canonical example validates against its schema;
  2. strictness bar — both schemas hold the tranche-0001 bar: top-level
     "additionalProperties": false, specVersion pinned to the 0.1.0 const, an
     anchored urn:srcos: id pattern, and a type const equal to the title;
  3. envelope parity — DeviceReading carries the ConversationEvent envelope
     vocabulary with byte-identical sub-schemas, and DeviceProfile carries the
     registry subset of it, so the device plane can never drift into a second
     identity/causality/governance vocabulary. specVersion is deliberately
     excluded: it is per-family by construction (check 2 pins it instead);
  4. recomputed profile digest — DeviceProfile.definitionDigest is RECOMPUTED
     from the profile's own declared-capability projection, never read back. A
     digest that is merely stored is an assertion about pinning; a digest that
     is recomputed is pinning;
  5. attribution soundness — the check this family exists for. Every reading
     must resolve to a real profile, to the exact profile REVISION it claims
     (digest equality), to a metric that profile declares, and to that metric's
     declared unit, source address, value type, ontology type and operating
     range. A reading that survives all five is attributable; one that does not
     is the silent-wrong the contract is meant to make impossible;
  6. simulated-visibility — any reading produced under a "virtual" profile must
     carry a label marking it as not a measurement, and no reading produced
     under a physical profile may carry one. Simulated data that is
     indistinguishable downstream is worse than no data;
  7. negative vectors — every case in fixtures/device-service/conformance.json
     FAILS for its stated reason.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

PROFILE_SCHEMA = "DeviceProfile.json"
READING_SCHEMA = "DeviceReading.json"
ABSENCE_SCHEMA = "NullAbsenceRecord.json"
ENVELOPE_AUTHORITY = "ConversationEvent.json"

SCHEMA_NAMES = [PROFILE_SCHEMA, READING_SCHEMA]

PAIRS = [
    (PROFILE_SCHEMA, "device_profile.json"),
    (PROFILE_SCHEMA, "device_profile.virtual.json"),
    (READING_SCHEMA, "device_reading.json"),
    (READING_SCHEMA, "device_reading.unavailable.json"),
    (ABSENCE_SCHEMA, "null_absence_record.device_timeout.json"),
]

PROFILE_EXAMPLES = ["device_profile.json", "device_profile.virtual.json"]
READING_EXAMPLES = ["device_reading.json", "device_reading.unavailable.json"]
ABSENCE_EXAMPLES = ["null_absence_record.device_timeout.json"]

# The shared envelope vocabulary. ConversationEvent is the authority.
# specVersion is excluded on purpose: it is the per-family contract version and
# is pinned by the strictness bar instead.
READING_ENVELOPE_KEYS = [
    "actorRef",
    "workspaceRef",
    "branchRef",
    "visibilityScope",
    "wallTime",
    "logicalTime",
    "causalParents",
    "traceContext",
    "provenanceLinks",
    "policyLabels",
    "riskLabels",
]

# A profile is declared, not observed: it carries the registry subset (no event
# time, no causality) with the same byte-identical sub-schemas.
PROFILE_ENVELOPE_KEYS = [
    "actorRef",
    "workspaceRef",
    "visibilityScope",
    "provenanceLinks",
    "policyLabels",
    "riskLabels",
]

# Normative digest projection. Exactly the fields that decide which readings are
# admissible; prose, labels and timestamps are excluded so documentation edits do
# not orphan live readings.
DIGEST_FIELDS = ["deviceClass", "protocol", "metrics"]

# The label that keeps simulated data visibly distinguishable downstream.
SIMULATED_LABEL = "synthetic:simulated-device"

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def fail(msg: str) -> None:
    FAILURES.append(msg)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def definition_digest(profile: dict) -> str:
    """Recompute DeviceProfile.definitionDigest. Normative: sha256 over the
    canonical JSON (sorted keys, no whitespace, UTF-8) of the DIGEST_FIELDS
    projection of the document AS WRITTEN — schema defaults are not
    materialised, so an omitted field and an explicitly-defaulted one are
    different declarations and hash differently."""
    core = {field: profile[field] for field in DIGEST_FIELDS}
    canonical = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# --------------------------------------------------------------- 1. conformance
def check_conformance(schemas: dict[str, dict]) -> None:
    for name, schema in schemas.items():
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
            CHECKS[f"schema-valid:{name}"] = True
        except jsonschema.SchemaError as exc:
            fail(f"schema invalid: {name}: {exc.message}")

    for schema_name, example_name in PAIRS:
        schema = schemas[schema_name]
        example = load(ROOT / "examples" / example_name)
        errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(example), key=str)
        if errors:
            for err in errors:
                fail(f"example {example_name} vs {schema_name}: {err.message}")
        else:
            CHECKS[f"example:{example_name}"] = True


# ---------------------------------------------------------------- 2. strictness
def check_strictness(schemas: dict[str, dict]) -> None:
    for name in SCHEMA_NAMES:
        schema = schemas[name]
        if schema.get("additionalProperties") is not False:
            fail(f"{name}: top-level additionalProperties must be false")
        if schema["properties"]["specVersion"].get("const") != "0.1.0":
            fail(f"{name}: specVersion must be pinned to const 0.1.0")
        pattern = schema["properties"]["id"].get("pattern", "")
        if not (pattern.startswith("^urn:srcos:") and pattern.endswith("$")):
            fail(f"{name}: id pattern must be an anchored urn:srcos: pattern")
        if schema["properties"]["type"].get("const") != schema["title"]:
            fail(f"{name}: type const must equal title")
        CHECKS[f"strictness:{name}"] = True


# ------------------------------------------------------------ 3. envelope parity
def check_envelope_parity(schemas: dict[str, dict]) -> None:
    authority = load(ROOT / "schemas" / ENVELOPE_AUTHORITY)["properties"]
    for name, keys in ((READING_SCHEMA, READING_ENVELOPE_KEYS), (PROFILE_SCHEMA, PROFILE_ENVELOPE_KEYS)):
        props = schemas[name]["properties"]
        for key in keys:
            if key not in props:
                fail(f"{name}: missing shared envelope property {key!r}")
            elif props[key] != authority[key]:
                fail(
                    f"{name}: envelope property {key!r} drifted from ConversationEvent "
                    f"— one envelope, not a second vocabulary"
                )
            else:
                CHECKS[f"envelope-parity:{name}:{key}"] = True


# ------------------------------------------------------------- 4. digest recompute
def check_profile_digests(profiles: dict[str, dict]) -> None:
    for name, profile in profiles.items():
        recomputed = definition_digest(profile)
        if profile["definitionDigest"] != recomputed:
            fail(
                f"{name}: definitionDigest is not the digest of its own declared capability "
                f"(stored {profile['definitionDigest']}, recomputed {recomputed})"
            )
        else:
            CHECKS[f"digest-recomputed:{name}"] = True

    # Two different declarations must not share a digest, or pinning proves nothing.
    seen: dict[str, str] = {}
    for name, profile in profiles.items():
        digest = profile["definitionDigest"]
        if digest in seen:
            fail(f"{name}: shares definitionDigest with {seen[digest]} — a pin that cannot distinguish revisions")
        seen[digest] = name
    CHECKS["digest-distinct"] = True


# -------------------------------------------------------- 5. attribution soundness
def check_attribution(profiles: dict[str, dict], readings: dict[str, dict], absences: dict[str, dict]) -> None:
    by_urn = {p["id"]: p for p in profiles.values()}
    absence_by_urn = {a["id"]: a for a in absences.values()}

    for name, reading in readings.items():
        profile = by_urn.get(reading["deviceProfileRef"])
        if profile is None:
            fail(f"{name}: deviceProfileRef {reading['deviceProfileRef']} resolves to no profile in the example set")
            continue
        CHECKS[f"attribution:{name}:profile-resolves"] = True

        if reading["profileDigest"] != definition_digest(profile):
            fail(
                f"{name}: profileDigest does not match the recomputed digest of "
                f"{profile['id']} — the reading was admitted against a different revision "
                f"than the one it names"
            )
        else:
            CHECKS[f"attribution:{name}:digest-pins-revision"] = True

        declared = {m["metric"]: m for m in profile["metrics"]}
        metric = declared.get(reading["metric"])
        if metric is None:
            fail(f"{name}: metric {reading['metric']!r} is not declared by {profile['id']}")
            continue
        CHECKS[f"attribution:{name}:metric-declared"] = True

        if reading["unit"] != metric["unit"]:
            fail(
                f"{name}: unit {reading['unit']!r} contradicts the profile's declared "
                f"{metric['unit']!r} for {reading['metric']} — a unit-confusion incident in waiting"
            )
        else:
            CHECKS[f"attribution:{name}:unit-agrees"] = True

        if reading["sourceAddress"] != metric["sourceAddress"]:
            fail(
                f"{name}: sourceAddress {reading['sourceAddress']!r} is not the channel the "
                f"profile declares for {reading['metric']} ({metric['sourceAddress']!r})"
            )
        else:
            CHECKS[f"attribution:{name}:channel-agrees"] = True

        if reading.get("kkoTypeRef") and metric.get("kkoTypeRef") and reading["kkoTypeRef"] != metric["kkoTypeRef"]:
            fail(f"{name}: kkoTypeRef disagrees with the profile's declared ontology type for {reading['metric']}")
        else:
            CHECKS[f"attribution:{name}:ontology-agrees"] = True

        # value typing + range, against the declaration rather than a runtime guess
        value = reading["value"]
        quality = reading["quality"]
        if quality == "unavailable":
            if value is not None:
                fail(f"{name}: unavailable reading carries a value")
            ref = reading.get("nullAbsenceRef")
            if not ref:
                fail(f"{name}: unavailable reading carries no nullAbsenceRef")
            elif ref not in absence_by_urn:
                fail(f"{name}: nullAbsenceRef {ref} resolves to no NullAbsenceRecord in the example set")
            elif absence_by_urn[ref].get("relatedEventRef") != reading["id"]:
                fail(f"{name}: the referenced NullAbsenceRecord does not point back at this reading")
            else:
                CHECKS[f"attribution:{name}:absence-typed"] = True
        else:
            expected = metric["valueType"]
            ok_type = {
                "number": isinstance(value, (int, float)) and not isinstance(value, bool),
                "integer": isinstance(value, int) and not isinstance(value, bool),
                "boolean": isinstance(value, bool),
                "string": isinstance(value, str),
            }[expected]
            if not ok_type:
                fail(f"{name}: value {value!r} is not the declared {expected} for {reading['metric']}")
            else:
                CHECKS[f"attribution:{name}:value-type"] = True
            if expected in ("number", "integer"):
                lo, hi = metric["minimum"], metric["maximum"]
                if not (lo <= value <= hi):
                    fail(f"{name}: value {value!r} is outside the declared range [{lo}, {hi}]")
                else:
                    CHECKS[f"attribution:{name}:value-in-range"] = True

        received = reading.get("receivedAt")
        if received and received < reading["observedAt"]:
            fail(f"{name}: receivedAt precedes observedAt — the reading arrived before it was observed")
        else:
            CHECKS[f"attribution:{name}:latency-ordered"] = True

        # A reading must also *say* where it came from, not only be checkable.
        rels = {link["ref"] for link in reading.get("provenanceLinks", [])}
        if profile["id"] not in rels or reading["deviceRef"] not in rels:
            fail(
                f"{name}: provenanceLinks must name both the device and the profile, so the "
                f"attribution survives being read without this validator"
            )
        else:
            CHECKS[f"attribution:{name}:provenance-stated"] = True

    # The example set must exercise both poles, or the absence path is untested prose.
    qualities = {r["quality"] for r in readings.values()}
    if "ok" not in qualities or "unavailable" not in qualities:
        fail("example set must contain at least one measured (ok) and one typed-absence (unavailable) reading")
    else:
        CHECKS["attribution:both-poles-exercised"] = True


# ---------------------------------------------------- 6. simulated visibility
def check_simulated_visibility(profiles: dict[str, dict], readings: dict[str, dict]) -> None:
    by_urn = {p["id"]: p for p in profiles.values()}
    for name, profile in profiles.items():
        simulated = profile["protocol"] == "virtual"
        labelled = SIMULATED_LABEL in profile.get("policyLabels", [])
        if simulated and not labelled:
            fail(f"{name}: a virtual profile must carry the {SIMULATED_LABEL!r} policy label")
        elif labelled and not simulated:
            fail(f"{name}: only a virtual profile may claim the {SIMULATED_LABEL!r} label")
        else:
            CHECKS[f"simulated-visibility:{name}"] = True

    for name, reading in readings.items():
        profile = by_urn.get(reading["deviceProfileRef"])
        if profile is None:
            continue
        simulated = profile["protocol"] == "virtual"
        labels = set(reading.get("policyLabels", [])) | set(reading.get("riskLabels", []))
        if simulated and SIMULATED_LABEL not in labels:
            fail(
                f"{name}: produced under a virtual profile but carries no {SIMULATED_LABEL!r} "
                f"label — simulated data must stay visibly distinguishable downstream"
            )
        elif not simulated and SIMULATED_LABEL in labels:
            fail(f"{name}: a physically-measured reading must not be labelled simulated")
        else:
            CHECKS[f"simulated-visibility:{name}"] = True


# ------------------------------------------------------------ 7. negative vectors
def check_negative_vectors(schemas: dict[str, dict]) -> None:
    fixture = load(ROOT / "fixtures" / "device-service" / "conformance.json")
    for i, case in enumerate(fixture["cases"]):
        schema = schemas[case["schema"]]
        try:
            jsonschema.validate(case["document"], schema)
        except jsonschema.ValidationError:
            CHECKS[f"negative:{i}:{case['schema']}"] = True
            continue
        fail(f"negative vector {i} ({case['schema']}) unexpectedly PASSED: {case['reason']}")


def main() -> int:
    schemas = {name: load(ROOT / "schemas" / name) for name in SCHEMA_NAMES + [ABSENCE_SCHEMA]}
    profiles = {n: load(ROOT / "examples" / n) for n in PROFILE_EXAMPLES}
    readings = {n: load(ROOT / "examples" / n) for n in READING_EXAMPLES}
    absences = {n: load(ROOT / "examples" / n) for n in ABSENCE_EXAMPLES}

    check_conformance(schemas)
    check_strictness(schemas)
    check_envelope_parity(schemas)
    check_profile_digests(profiles)
    check_attribution(profiles, readings, absences)
    check_simulated_visibility(profiles, readings)
    check_negative_vectors(schemas)

    for msg in FAILURES:
        print(f"FAIL: {msg}", file=sys.stderr)

    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
