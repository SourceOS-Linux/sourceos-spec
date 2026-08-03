from promote_model import decide_promotion, _seal

CH = {"name": "GBM-fraud", "ver": "v4", "metric": "AUC", "val": 0.962}
CL = {"name": "GNN-fraud", "ver": "v1", "metric": "AUC", "val": 0.971}
WORSE = {"name": "X", "ver": "v1", "metric": "AUC", "val": 0.95}


def test_promote_when_better_and_eval_passed_unregulated():
    d = decide_promotion("fraud", CH, CL, eval_passed=True)
    assert d["verdict"] == "promote"
    assert d["receipt"]["receipt_hash"].startswith("sha256:")


def test_regulated_blocks_without_signoff():
    d = decide_promotion("credit", CH, CL, eval_passed=True, regulated=True)
    assert d["verdict"] == "blocked"


def test_regulated_promotes_with_signoff():
    d = decide_promotion("credit", CH, CL, eval_passed=True, regulated=True, signed_off=True)
    assert d["verdict"] == "promote"


def test_hold_when_no_improvement():
    assert decide_promotion("fraud", CH, WORSE, eval_passed=True)["verdict"] == "hold"


def test_shadow_when_better_but_no_eval():
    assert decide_promotion("fraud", CH, CL)["verdict"] == "shadow"


def test_fail_closed_default_never_promotes():
    # defaults: eval_passed=False → never promote, even for a clear winner
    assert decide_promotion("fraud", CH, CL)["verdict"] != "promote"


def test_drift_is_flagged():
    d = decide_promotion("credit", CH, CL, eval_passed=True, drift=0.11)
    assert d["flags"] and "drift" in d["flags"][0]


def test_receipt_is_deterministic_replayable():
    a = decide_promotion("fraud", CH, CL, eval_passed=True)["receipt"]["receipt_hash"]
    b = decide_promotion("fraud", CH, CL, eval_passed=True)["receipt"]["receipt_hash"]
    assert a == b  # same inputs → same seal (occurred_at excluded from the hash)
