#!/usr/bin/env python3
"""Cross-plane champion → challenger promotion, fail-closed, with a sealed RunReceipt.

One promotion contract both planes (cloud lattice + local agent-machine) call. A
challenger is promoted ONLY when it beats the champion AND has passed the eval gate;
a regulated target additionally requires examiner sign-off. Every decision emits a
RunReceipt whose hash is deterministic over the decision inputs — so a promotion is
replayable: re-run the same inputs, get the same receipt. Nothing self-promotes:
eval_passed and signed_off default False.
"""
from __future__ import annotations

import datetime
import hashlib
import json
from typing import Any, Dict, List

DRIFT_THRESHOLD = 0.10  # PSI above this flags the target for review


def _seal(payload: Dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def decide_promotion(
    target: str,
    champion: Dict[str, Any],
    challenger: Dict[str, Any],
    *,
    drift: float = 0.0,
    eval_passed: bool = False,
    regulated: bool = False,
    signed_off: bool = False,
) -> Dict[str, Any]:
    """Return {verdict, reason, flags, receipt}. Verdict ∈ promote|hold|shadow|blocked."""
    improved = challenger.get("val", 0) > champion.get("val", 0)
    delta = round(challenger.get("val", 0) - champion.get("val", 0), 4)

    if not eval_passed:
        verdict = "shadow" if improved else "hold"
        reason = ("challenger leads but has not passed the eval gate — held in shadow"
                  if improved else "no improvement and eval gate not passed")
    elif not improved:
        verdict, reason = "hold", (
            f"challenger {challenger.get('metric')} {challenger.get('val')} "
            f"does not beat champion {champion.get('val')}")
    elif regulated and not signed_off:
        verdict, reason = "blocked", "regulated target — examiner sign-off required before promotion"
    else:
        verdict, reason = "promote", f"challenger beats champion by {delta} and passed the eval gate"

    flags: List[str] = []
    if drift > DRIFT_THRESHOLD:
        flags.append(f"PSI drift {drift} exceeds {DRIFT_THRESHOLD} — target flagged for review")

    decision_core = {
        "kind": "RunReceipt",
        "recordType": "ModelPromotion",
        "target": target,
        "champion": {"name": champion.get("name"), "ver": champion.get("ver"), "val": champion.get("val")},
        "challenger": {"name": challenger.get("name"), "ver": challenger.get("ver"), "val": challenger.get("val")},
        "delta": delta,
        "drift": drift,
        "eval_passed": eval_passed,
        "regulated": regulated,
        "signed_off": signed_off,
        "verdict": verdict,
    }
    receipt = dict(decision_core)
    receipt["receipt_hash"] = _seal(decision_core)  # deterministic → replayable
    receipt["occurred_at"] = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {"verdict": verdict, "reason": reason, "flags": flags, "receipt": receipt}
