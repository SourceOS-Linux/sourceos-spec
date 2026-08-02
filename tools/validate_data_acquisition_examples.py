#!/usr/bin/env python3
"""Validate the Data-Acquisition governance family (scoped CatalogEntry + DataAcquisitionRequest).

The feature: every doc/dataset/collection is auto-catalogued at user/project/chat
scope; promotion to PLATFORM scope is not automatic. It is authorized only by a
DataAcquisitionRequest whose approval is the MEET of two independent gates — a
governance review AND an IP/legal rights review. Either gate not-approved ⇒ the
request is not approved, and the object stays at its origin scope. Fail closed.

Five checks:
  1. schema conformance — schemas valid draft-2020-12; every example validates;
  2. meet soundness — the check this family exists for. A DAR's `state` is
     RECOMPUTED from its two gate decisions: 'approved' iff BOTH are 'approved';
     'denied' if either is 'denied'; otherwise in-flight. A `state` that
     disagrees with the recomputed meet fails — in BOTH directions, so neither a
     rubber-stamp 'approved' nor a laundered single-gate approval can pass;
  3. promotion binding — a CatalogEntry at scope 'platform' MUST carry
     promotion.state 'promoted' and a darRef that resolves to an *approved* DAR
     whose subjectRef is that entry; and a non-platform entry may not claim
     'promoted'. No object reaches platform without an approved request;
  4. no orphan promotions — every promotion.darRef resolves to a DAR in the set;
  5. negative vectors — every case fails validation on its named `failValidator`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

DAR_SCHEMA = "DataAcquisitionRequest.json"
ENTRY_SCHEMA = "CatalogEntry.json"
SCHEMA_NAMES = [DAR_SCHEMA, ENTRY_SCHEMA]

DAR_EXAMPLES = ["data_acquisition_request.approved.json", "data_acquisition_request.pending.json"]
ENTRY_EXAMPLES = ["catalog_entry.user_scope.json", "catalog_entry.platform_scope.json", "catalog_entry.legacy.json"]
PAIRS = [(DAR_SCHEMA, e) for e in DAR_EXAMPLES] + [(ENTRY_SCHEMA, e) for e in ENTRY_EXAMPLES]

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def fail(msg: str) -> None:
    FAILURES.append(msg)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def meet_state(dar: dict) -> str:
    """Recompute the overall state from the two independent gates. Fail closed:
    approved iff BOTH approved; denied if either denied; else in-flight."""
    g = dar["governanceReview"]["decision"]
    ip = dar["ipLegalReview"]["decision"]
    if g == "approved" and ip == "approved":
        return "approved"
    if g == "denied" or ip == "denied":
        return "denied"
    return "in-flight"  # submitted / under-review


# --------------------------------------------------------------- 1. conformance
def check_conformance(schemas: dict[str, dict]) -> None:
    for name, schema in schemas.items():
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
            CHECKS[f"schema-valid:{name}"] = True
        except jsonschema.SchemaError as exc:
            fail(f"schema invalid: {name}: {exc.message}")
    for schema_name, example_name in PAIRS:
        errors = sorted(jsonschema.Draft202012Validator(schemas[schema_name]).iter_errors(load(ROOT / "examples" / example_name)), key=str)
        if errors:
            for err in errors:
                fail(f"example {example_name} vs {schema_name}: {err.message}")
        else:
            CHECKS[f"example:{example_name}"] = True


# --------------------------------------------------------------- 2. meet soundness
def check_meet(dars: dict[str, dict]) -> None:
    for name, dar in dars.items():
        recomputed = meet_state(dar)
        state = dar["state"]
        # 'approved' must agree exactly with the meet, in both directions.
        if state == "approved" and recomputed != "approved":
            fail(f"{name}: state 'approved' but the gate meet is {recomputed!r} — a single-gate or "
                 f"rubber-stamp approval is not the meet")
        elif recomputed == "approved" and state != "approved":
            fail(f"{name}: both gates approved but state is {state!r} — an approved meet must be recorded as approved")
        elif state == "denied" and recomputed != "denied":
            fail(f"{name}: state 'denied' but no gate is denied (meet is {recomputed!r}) — a denial must name a denying gate")
        elif recomputed == "denied" and state != "denied":
            fail(f"{name}: a gate is denied but state is {state!r} — a denied gate cannot leave the request open/approved")
        else:
            CHECKS[f"meet:{name}"] = True


# ------------------------------------------------------------- 3/4. promotion binding
def check_promotion(entries: dict[str, dict], dars: dict[str, dict]) -> None:
    by_id = {d["id"]: d for d in dars.values()}
    for name, entry in entries.items():
        scope = entry.get("scope")
        promo = entry.get("promotion") or {}
        state = promo.get("state")
        dar_ref = promo.get("darRef")

        # orphan check: any darRef must resolve
        if dar_ref is not None and dar_ref not in by_id:
            fail(f"{name}: promotion.darRef {dar_ref} resolves to no DataAcquisitionRequest in the set")
        else:
            CHECKS[f"promotion:{name}:no-orphan-dar"] = True

        if scope == "platform":
            if state != "promoted":
                fail(f"{name}: scope 'platform' but promotion.state is {state!r} — must be 'promoted'")
                continue
            dar = by_id.get(dar_ref) if dar_ref else None
            if dar is None:
                fail(f"{name}: scope 'platform' but no darRef resolving to a DAR — no object reaches platform without an approved request")
            elif dar["state"] != "approved":
                fail(f"{name}: promoted to platform by DAR {dar['id']} whose state is {dar['state']!r}, not 'approved'")
            elif dar["subjectRef"] != entry["id"]:
                fail(f"{name}: the DAR that promoted it names subjectRef {dar['subjectRef']}, not this entry")
            else:
                CHECKS[f"promotion:{name}:bound-to-approved-dar"] = True
                # WO-COMMONS-2: the DOI is minted once at promotion and recorded on
                # BOTH the entry and the approving DAR — they must agree.
                entry_doi = promo.get("doi")
                dar_doi = dar.get("mintedDoi")
                if entry_doi and dar_doi and entry_doi != dar_doi:
                    fail(f"{name}: promotion.doi {entry_doi!r} != minting DAR.mintedDoi {dar_doi!r} — "
                         f"a DOI is minted once; the entry and its DAR must record the same one")
                elif entry_doi:
                    CHECKS[f"promotion:{name}:doi-matches-dar"] = True
        else:
            if state == "promoted":
                fail(f"{name}: scope {scope!r} but promotion.state is 'promoted' — only platform entries are promoted")
            else:
                CHECKS[f"promotion:{name}:origin-not-promoted"] = True


# ------------------------------------------------------------- 5. negative vectors
def check_negative_vectors(schemas: dict[str, dict]) -> None:
    fixture = load(ROOT / "fixtures" / "data-acquisition" / "conformance.json")
    for i, case in enumerate(fixture["cases"]):
        schema = schemas[case["schema"]]
        expected = case.get("failValidator")
        try:
            jsonschema.validate(case["document"], schema)
        except jsonschema.ValidationError as exc:
            if expected is not None and exc.validator != expected:
                fail(f"negative vector {i} ({case['schema']}) failed on {exc.validator!r}, not the expected {expected!r}: {case['reason']}")
            else:
                CHECKS[f"negative:{i}:{case['schema']}:{exc.validator}"] = True
            continue
        fail(f"negative vector {i} ({case['schema']}) unexpectedly PASSED: {case['reason']}")


def main() -> int:
    schemas = {name: load(ROOT / "schemas" / name) for name in SCHEMA_NAMES}
    dars = {n: load(ROOT / "examples" / n) for n in DAR_EXAMPLES}
    entries = {n: load(ROOT / "examples" / n) for n in ENTRY_EXAMPLES}

    check_conformance(schemas)
    check_meet(dars)
    check_promotion(entries, dars)
    check_negative_vectors(schemas)

    for msg in FAILURES:
        print(f"FAIL: {msg}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
