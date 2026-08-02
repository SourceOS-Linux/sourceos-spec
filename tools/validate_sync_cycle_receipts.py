#!/usr/bin/env python3
"""Validate the release/sync receipt family + the epistemicLevel meet (SP-GATE-003).

Beyond schema conformance, this RECOMPUTES each receipt's epistemicLevel as the meet
of (attestation ∧ verification) and rejects a declared value that disagrees — so a
receipt can never claim 'Proved' while its inputs are unsigned or a check failed
(absence of evidence returns Speculative, not Proved).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

RELEASE_SCHEMA = ROOT / "schemas" / "ReleaseReceipt.json"
SYNC_SCHEMA = ROOT / "schemas" / "SyncCycleReceipt.json"

RELEASE_EXAMPLES = ["release_receipt.json", "release_receipt.unsigned.json", "release_receipt.failed.json"]
SYNC_EXAMPLES = ["sync-cycle-receipt.json", "sync-cycle-receipt.dry-run.json"]

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def release_meet(rr: dict) -> str:
    """Proved iff verified AND signed; Refuted if a check failed; else Speculative."""
    if rr.get("status") == "failed":
        return "Refuted"
    signed = bool((rr.get("attestation") or {}).get("signed"))
    if rr.get("status") == "verified" and signed:
        return "Proved"
    return "Speculative"  # partial, or verified-but-unsigned — absence of a signature is not Proved


def sync_meet(scr: dict) -> str:
    """Proved iff the release-attestation decision verified (ok=true); else Speculative."""
    att = scr.get("attestation") or {}
    return "Proved" if att.get("ok") is True else "Speculative"


def check(schema_path: Path, example_names: list[str], meet) -> None:
    schema = load(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    for name in example_names:
        ex = load(ROOT / "examples" / name)
        errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(ex), key=str)
        if errs:
            for e in errs:
                FAILURES.append(f"{name} vs {schema_path.name}: {e.message}")
            continue
        CHECKS[f"schema:{name}"] = True
        declared = ex.get("epistemicLevel")
        if declared is not None:
            recomputed = meet(ex)
            if declared != recomputed:
                FAILURES.append(f"{name}: epistemicLevel {declared!r} disagrees with the meet {recomputed!r} — "
                                f"a receipt may not claim more than its attestation/verification support")
            else:
                CHECKS[f"epistemic-meet:{name}:{declared}"] = True


def check_negatives() -> None:
    # A receipt claiming Proved while unsigned must be caught by the meet recompute.
    rr = load(ROOT / "examples" / "release_receipt.unsigned.json")
    forged = {**rr, "epistemicLevel": "Proved"}
    if release_meet(forged) == "Proved":
        FAILURES.append("negative: an unsigned verified release recomputed as Proved — the meet is not fail-closed")
    else:
        CHECKS["negative:unsigned-cannot-be-proved"] = True


def main() -> int:
    check(RELEASE_SCHEMA, RELEASE_EXAMPLES, release_meet)
    check(SYNC_SCHEMA, SYNC_EXAMPLES, sync_meet)
    check_negatives()
    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
