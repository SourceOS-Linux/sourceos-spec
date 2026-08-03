import datetime
import pytest
from build_surface_feed import assemble, REQUIRED


def _payload(surface):
    return {k: [{"x": 1}] for k in REQUIRED[surface]}


@pytest.mark.parametrize("surface", sorted(REQUIRED))
def test_live_payload_is_marked_live_with_required_keys(surface):
    f = assemble(surface, _payload(surface), live=True)
    assert f["provenance"] == "live"
    for k in REQUIRED[surface]:
        assert k in f
    # generated_at is a valid ISO-8601 Z timestamp
    datetime.datetime.fromisoformat(f["generated_at"].replace("Z", "+00:00"))


def test_sample_when_not_live():
    f = assemble("b11", _payload("b11"), live=False)
    assert f["provenance"] == "sample"


def test_missing_required_key_raises():
    bad = _payload("e11"); del bad["governor"]
    with pytest.raises(ValueError):
        assemble("e11", bad, live=True)


def test_non_list_required_key_raises():
    bad = _payload("turn-witness"); bad["turns"] = "nope"
    with pytest.raises(ValueError):
        assemble("turn-witness", bad, live=True)


def test_unknown_surface_raises():
    with pytest.raises(ValueError):
        assemble("nope", {}, live=True)
