#!/usr/bin/env python3
"""Validate the consent-governance family: ConsentSurfaceRegistry + CapabilityConsentPolicy.

These two contracts record how consent GATES observation and action. They describe no
capture mechanism — no collector, no transport, no payload — so the only thing that can
make them mean anything is a gate that refuses to certify a weakened default. This is
that gate.

Five invariants, each proven to bite on every run by a synthetic negative control:

  (a) self-sovereign      — collectorPrincipal MUST equal subjectPrincipal. The observed
                            and the observing are one principal, or this is not the
                            contract it claims to be.
  (b) default-deny        — the registry schema must DECLARE consent.state default
                            'denied'; a 'granted'/'revoked' surface must carry the
                            evidence of that transition (grantedAt/revokedAt + grantRef),
                            so a state cannot be edited into existence; and every per-use
                            capability must ship defaultState 'disabled'.
  (c) canonical defaults  — every capability in the canonical matrix must be present
                            (absence from the policy IS ungoverned, the state this family
                            exists to eliminate) with its pinned defaultStandard; and
                            effectiveMode may diverge from defaultStandard only when
                            userOverride marks it as the subject's own decision. The same
                            attributability rule applies to a GRANTED surface — a denied or
                            revoked surface is 'off' by consequence of consent, not by
                            override, and is exempt.
  (d) one-shot            — a per-use capability must be oneShot:true and may never sit in
                            a standing mode, not even behind userOverride. Per-use without
                            one-shot is the exact hole through which a single 'allow'
                            becomes a standing permission.
  (e) explanation         — every surface and capability carries a non-trivial plain
                            sentence: consent to something unexplained is not consent.
                            Length alone is not enough, so placeholder and
                            single-word-repeated text is rejected too.

Self-exclusion discipline (see tools/validate_schema_references.py): the negative control
is built from SYNTHETIC in-memory documents only. It never reads, writes, or mutates
anything in examples/ or schemas/, so the proof can never pollute the thing being proven.
If any control fails to trip, the validator exits non-zero and certifies nothing.

  validate_consent_plane_examples.py              # full run (default)
  validate_consent_plane_examples.py --self-test  # negative control only
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    ("ConsentSurfaceRegistry.json", "consent_surface_registry.json"),
    ("CapabilityConsentPolicy.json", "capability_consent_policy.json"),
]

# The canonical shipped consent standard per capability. Pinned HERE, in the gate, rather
# than only in the example: an example is a file anyone can edit, a gate is a thing that
# has to be argued with. Active capabilities are per-use; microphone is the single
# deliberate exception (a per-utterance prompt makes continuous listening unusable, so the
# honest mitigation is a session bound, not a prompt).
CANONICAL_CAPABILITY_DEFAULTS = {
    "camera": "per-use",
    "screen_capture": "per-use",
    "control_my_computer": "per-use",
    "skycomputer": "per-use",
    "file_write": "per-use",
    "network_egress": "per-use",
    "send_on_behalf": "per-use",
    "microphone": "standing-session",
}

STANDING_MODES = {"standing-session", "standing-persistent"}

MIN_EXPLANATION_CHARS = 12
MIN_EXPLANATION_WORDS = 3
PLACEHOLDER_EXPLANATIONS = {
    "todo", "tbd", "n/a", "na", "none", "null", "-", "--", "xxx", "placeholder",
    "fixme", "?", "see docs", "as above",
}


# ── pure checks (no I/O; these are exactly what the negative control pins) ────────────
def check_a_self_sovereign(registry: dict) -> list[str]:
    """(a) The observer and the observed must be the same principal."""
    subject = registry.get("subjectPrincipal")
    collector = registry.get("collectorPrincipal")
    if collector != subject:
        return [
            f"(a) not self-sovereign: collectorPrincipal={collector!r} != "
            f"subjectPrincipal={subject!r} — a third party holding the observation is "
            f"not expressible in this contract"
        ]
    return []


def consent_state_default(registry_schema: dict) -> str | None:
    """Read the DECLARED default of surfaces[].consent.state out of the schema."""
    try:
        node = registry_schema["properties"]["surfaces"]["items"]["properties"]
        return node["consent"]["properties"]["state"].get("default")
    except (KeyError, TypeError):
        return None


def check_b_default_deny(registry: dict, policy: dict, registry_schema: dict) -> list[str]:
    """(b) Denial is the resting state, and a departure from it must be evidenced."""
    out: list[str] = []

    declared = consent_state_default(registry_schema)
    if declared != "denied":
        out.append(
            f"(b) ConsentSurfaceRegistry declares consent.state default {declared!r}, "
            f"not 'denied' — an unanswered surface would be a permitted one"
        )

    for surface in registry.get("surfaces", []):
        sid = surface.get("surfaceId")
        consent = surface.get("consent") or {}
        state = consent.get("state", "denied")
        if state == "granted":
            for field in ("grantedAt", "grantRef"):
                if not consent.get(field):
                    out.append(
                        f"(b) surface {sid!r} is 'granted' with no {field} — a grant with "
                        f"no evidence is an assumed one, which default-deny forbids"
                    )
        elif state == "revoked":
            for field in ("revokedAt", "grantRef"):
                if not consent.get(field):
                    out.append(
                        f"(b) surface {sid!r} is 'revoked' with no {field} — a withdrawal "
                        f"must point at the grant it withdrew"
                    )

    for cap in policy.get("capabilities", []):
        cid = cap.get("capabilityId")
        if cap.get("defaultStandard") == "per-use" and cap.get("defaultState") != "disabled":
            out.append(
                f"(b) per-use capability {cid!r} ships defaultState="
                f"{cap.get('defaultState')!r}, not 'disabled' — an unanswered active "
                f"capability would be live"
            )
    return out


def check_c_canonical_defaults(policy: dict, registry: dict) -> list[str]:
    """(c) The shipped matrix is pinned, and any divergence must be attributable."""
    out: list[str] = []
    present = {c.get("capabilityId") for c in policy.get("capabilities", [])}

    for cap_id, expected in CANONICAL_CAPABILITY_DEFAULTS.items():
        if cap_id not in present:
            out.append(
                f"(c) canonical capability {cap_id!r} is absent from the policy — absence "
                f"is not a safe default, it is ungoverned"
            )

    for cap in policy.get("capabilities", []):
        cid = cap.get("capabilityId")
        expected = CANONICAL_CAPABILITY_DEFAULTS.get(cid)
        standard = cap.get("defaultStandard")
        if expected is not None and standard != expected:
            out.append(
                f"(c) capability {cid!r} declares defaultStandard={standard!r} but the "
                f"canonical shipped default is {expected!r}"
            )
        if cap.get("effectiveMode") != standard and not cap.get("userOverride"):
            out.append(
                f"(c) capability {cid!r} runs effectiveMode={cap.get('effectiveMode')!r} "
                f"against defaultStandard={standard!r} with userOverride=false — an "
                f"unattributed divergence is a silently changed default"
            )

    # Same attributability rule for a GRANTED surface. A denied/revoked surface is 'off'
    # by consequence of consent, not by override, so it is exempt.
    for surface in registry.get("surfaces", []):
        consent = surface.get("consent") or {}
        if consent.get("state", "denied") != "granted":
            continue
        standard = surface.get("defaultStandard")
        if surface.get("effectiveMode") != standard and not surface.get("userOverride"):
            out.append(
                f"(c) granted surface {surface.get('surfaceId')!r} runs effectiveMode="
                f"{surface.get('effectiveMode')!r} against defaultStandard={standard!r} "
                f"with userOverride=false — an unattributed divergence"
            )
    return out


def check_d_one_shot(policy: dict) -> list[str]:
    """(d) A per-use grant is single-use and not persistable — no exceptions."""
    out: list[str] = []
    for cap in policy.get("capabilities", []):
        cid = cap.get("capabilityId")
        standard = cap.get("defaultStandard")
        effective = cap.get("effectiveMode")
        if "per-use" not in (standard, effective):
            continue
        if cap.get("oneShot") is not True:
            out.append(
                f"(d) per-use capability {cid!r} is not oneShot — a per-use grant that can "
                f"be persisted is how one 'allow' becomes a standing permission"
            )
        if effective in STANDING_MODES:
            out.append(
                f"(d) per-use capability {cid!r} sits in standing mode {effective!r} — "
                f"one-shot forbids the persistable grant a standing mode requires, and "
                f"userOverride cannot licence it (the subject may tighten, never loosen)"
            )
    return out


def explanation_defect(label: str, text: object) -> str | None:
    """Is this a real sentence a person could act on, or a placeholder?"""
    if not isinstance(text, str):
        return f"(e) {label} has no explanation — an unexplained surface cannot be consented to"
    stripped = text.strip()
    if len(stripped) < MIN_EXPLANATION_CHARS:
        return f"(e) {label} explanation is {len(stripped)} chars, under the {MIN_EXPLANATION_CHARS} minimum"
    if stripped.lower().rstrip(".") in PLACEHOLDER_EXPLANATIONS:
        return f"(e) {label} explanation is placeholder text: {stripped!r}"
    if len({w.lower() for w in stripped.split() if w}) < MIN_EXPLANATION_WORDS:
        return (
            f"(e) {label} explanation has under {MIN_EXPLANATION_WORDS} distinct words: "
            f"{stripped!r} — length alone is not an explanation"
        )
    return None


def check_e_explanations(registry: dict, policy: dict) -> list[str]:
    """(e) Every governed thing carries the plain sentence shown before enabling."""
    out: list[str] = []
    for surface in registry.get("surfaces", []):
        defect = explanation_defect(f"surface {surface.get('surfaceId')!r}", surface.get("explanation"))
        if defect:
            out.append(defect)
    for cap in policy.get("capabilities", []):
        defect = explanation_defect(f"capability {cap.get('capabilityId')!r}", cap.get("explanation"))
        if defect:
            out.append(defect)
    return out


def run_all_checks(registry: dict, policy: dict, registry_schema: dict) -> dict[str, list[str]]:
    return {
        "a_self_sovereign": check_a_self_sovereign(registry),
        "b_default_deny": check_b_default_deny(registry, policy, registry_schema),
        "c_canonical_defaults": check_c_canonical_defaults(policy, registry),
        "d_one_shot": check_d_one_shot(policy),
        "e_explanation": check_e_explanations(registry, policy),
    }


# ── negative control: synthetic only, never touches examples/ or schemas/ ─────────────
def _nc_registry() -> dict:
    return {
        "id": "urn:srcos:consent-registry:_nc",
        "type": "ConsentSurfaceRegistry",
        "specVersion": "0.0.0",
        "deploymentScope": "self-sovereign",
        "subjectPrincipal": "urn:srcos:principal:_nc",
        "collectorPrincipal": "urn:srcos:principal:_nc",
        "surfaces": [
            {
                "surfaceId": "telemetry:model:nc_surface",
                "category": "negative-control",
                "sensitivity": "benign",
                "pii": False,
                "defaultStandard": "standing-persistent",
                "effectiveMode": "standing-persistent",
                "userOverride": False,
                "explanation": "Synthetic negative-control row, never shipped anywhere.",
                "projectionMode": "LOSSLESS",
                "purpose": "negative-control",
                "consent": {
                    "state": "granted",
                    "grantedAt": "2026-01-01T00:00:00Z",
                    "grantRef": "urn:srcos:consent-grant:_nc",
                },
            }
        ],
    }


def _nc_policy() -> dict:
    return {
        "id": "urn:srcos:consent-policy:_nc",
        "type": "CapabilityConsentPolicy",
        "specVersion": "0.0.0",
        "deploymentScope": "self-sovereign",
        "subjectPrincipal": "urn:srcos:principal:_nc",
        "capabilities": [
            {
                "capabilityId": cap_id,
                "riskClass": "sensor-capture",
                "defaultStandard": standard,
                "effectiveMode": standard,
                "userOverride": False,
                "defaultState": "disabled",
                "explanation": "Synthetic negative-control capability, never shipped.",
                "oneShot": standard == "per-use",
            }
            for cap_id, standard in CANONICAL_CAPABILITY_DEFAULTS.items()
        ],
    }


_NC_SCHEMA_DENIED = {
    "properties": {"surfaces": {"items": {"properties": {
        "consent": {"properties": {"state": {"default": "denied"}}}}}}}
}
_NC_SCHEMA_GRANTED = {
    "properties": {"surfaces": {"items": {"properties": {
        "consent": {"properties": {"state": {"default": "granted"}}}}}}}
}


def _mutate(doc: dict, path: list, value: object) -> dict:
    """Deep-copy ``doc`` and set ``path`` to ``value`` (list indices allowed)."""
    out = copy.deepcopy(doc)
    node = out
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    return out


def _drop(doc: dict, path: list) -> dict:
    out = copy.deepcopy(doc)
    node = out
    for key in path[:-1]:
        node = node[key]
    del node[path[-1]]
    return out


def _cap_index(policy: dict, cap_id: str) -> int:
    return next(i for i, c in enumerate(policy["capabilities"]) if c["capabilityId"] == cap_id)


def negative_control() -> bool:
    """Every invariant, shown failing on a synthetic defect and passing when clean."""
    reg, pol = _nc_registry(), _nc_policy()
    cam = _cap_index(pol, "camera")
    mic = _cap_index(pol, "microphone")

    controls: list[tuple[str, bool]] = [
        # baseline: the clean synthetic pair must produce NO findings, or every
        # "it bites" result below would be meaningless noise.
        ("clean synthetic pair passes every check",
         not any(run_all_checks(reg, pol, _NC_SCHEMA_DENIED).values())),

        # (a) self-sovereign
        ("(a) bites: collector is a third party",
         bool(check_a_self_sovereign(_mutate(reg, ["collectorPrincipal"], "urn:srcos:principal:vendor")))),

        # (b) default-deny — all three prongs
        ("(b) bites: schema declares default 'granted'",
         bool(check_b_default_deny(reg, pol, _NC_SCHEMA_GRANTED))),
        ("(b) bites: granted surface with no grantRef",
         bool(check_b_default_deny(_drop(reg, ["surfaces", 0, "consent", "grantRef"]), pol, _NC_SCHEMA_DENIED))),
        ("(b) bites: revoked surface with no revokedAt",
         bool(check_b_default_deny(_mutate(reg, ["surfaces", 0, "consent"],
                                           {"state": "revoked", "grantRef": "urn:srcos:consent-grant:_nc"}),
                                   pol, _NC_SCHEMA_DENIED))),
        ("(b) bites: per-use capability ships enabled",
         bool(check_b_default_deny(reg, _mutate(pol, ["capabilities", cam, "defaultState"], "enabled"),
                                   _NC_SCHEMA_DENIED))),

        # (c) canonical defaults
        ("(c) bites: camera weakened to standing-persistent",
         bool(check_c_canonical_defaults(_mutate(pol, ["capabilities", cam, "defaultStandard"], "standing-persistent"), reg))),
        ("(c) bites: a canonical capability deleted from the policy",
         bool(check_c_canonical_defaults(_mutate(pol, ["capabilities"],
                                                 [c for c in pol["capabilities"] if c["capabilityId"] != "camera"]), reg))),
        ("(c) bites: effectiveMode diverges with userOverride=false",
         bool(check_c_canonical_defaults(_mutate(pol, ["capabilities", mic, "effectiveMode"], "off"), reg))),
        ("(c) bites: granted surface diverges with userOverride=false",
         bool(check_c_canonical_defaults(pol, _mutate(reg, ["surfaces", 0, "effectiveMode"], "standing-session")))),
        ("(c) exempts: denied surface sits 'off' without an override",
         not check_c_canonical_defaults(pol, _mutate(_mutate(reg, ["surfaces", 0, "effectiveMode"], "off"),
                                                     ["surfaces", 0, "consent"], {"state": "denied"}))),

        # (d) one-shot
        ("(d) bites: per-use capability is not oneShot",
         bool(check_d_one_shot(_mutate(pol, ["capabilities", cam, "oneShot"], False)))),
        ("(d) bites: per-use capability in a standing mode even with userOverride",
         bool(check_d_one_shot(_mutate(_mutate(pol, ["capabilities", cam, "effectiveMode"], "standing-persistent"),
                                       ["capabilities", cam, "userOverride"], True)))),

        # (e) explanation
        ("(e) bites: explanation too short",
         bool(check_e_explanations(_mutate(reg, ["surfaces", 0, "explanation"], "TODO"), pol))),
        ("(e) bites: long but trivial explanation",
         bool(check_e_explanations(reg, _mutate(pol, ["capabilities", cam, "explanation"], "todo todo todo todo")))),
        ("(e) bites: explanation missing entirely",
         bool(check_e_explanations(_drop(reg, ["surfaces", 0, "explanation"]), pol))),
    ]

    for name, ok in controls:
        print(f"    {'OK  ' if ok else 'FAIL'} negative control: {name}")
    return all(ok for _, ok in controls)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Consent-governance gate for the consent plane.")
    ap.add_argument("--self-test", action="store_true", help="run only the negative control")
    args = ap.parse_args(argv)

    # A gate that cannot fail certifies nothing.
    if not negative_control():
        print("FAIL: negative control did not trip — the gate has no teeth; refusing to certify")
        return 2
    if args.self_test:
        print("OK: negative control passed")
        return 0

    checks: dict[str, bool] = {}
    for schema_name, example_name in PAIRS:
        schema = _load(ROOT / "schemas" / schema_name)
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(_load(ROOT / "examples" / example_name))
        checks[f"schema:{example_name}"] = True

    registry_schema = _load(ROOT / "schemas" / "ConsentSurfaceRegistry.json")
    registry = _load(ROOT / "examples" / "consent_surface_registry.json")
    policy = _load(ROOT / "examples" / "capability_consent_policy.json")

    findings = run_all_checks(registry, policy, registry_schema)
    for name, violations in findings.items():
        checks[name] = not violations
    flat = [v for violations in findings.values() for v in violations]
    if flat:
        print(f"FAIL: {len(flat)} consent-governance violation(s):", file=sys.stderr)
        for violation in flat:
            print(f"  {violation}", file=sys.stderr)
        return 1

    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
