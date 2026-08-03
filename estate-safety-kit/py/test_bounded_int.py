"""Pins the bounded-int / bounded-payload validators against the exact defect they close:
a type/sign check that Python's arbitrary-precision ints make unbounded in practice.

Ported from prophet-platform's `apps/compute-gateway/tests/test_gateway_hardening.py`
(the digit-encoded-payload tests added in PR #1118) plus new tests for the generalized
string and aggregate-size helpers this module adds beyond the original single-purpose
`_bad_nonneg_int`.
"""
from __future__ import annotations

import sys

import pytest

from bounded_int import (
    MAX_NONNEG_INT,
    bad_nonneg_int,
    check_nonneg_int,
    bad_bounded_str,
    check_bounded_str,
    check_total_size,
)


def _giant_int_from_digits(mb: float) -> int:
    """A decimal-digit-encoded int of ~`mb` megabytes — the exact smuggling shape #1118
    closed. Python 3.11+'s own PYTHONINTMAXSTRDIGITS guard (default 4300) already blocks
    constructing this from a literal at the default limit, so bump it locally, mirroring
    the upstream fixture."""
    digits = int(mb * 1_000_000)
    if sys.get_int_max_str_digits() < digits + 64:
        sys.set_int_max_str_digits(digits + 64)
    return int("9" * digits)


class TestBadNonnegInt:
    def test_negative_is_bad(self):
        assert bad_nonneg_int(-1) is True

    def test_bool_is_bad_even_though_isinstance_int_is_true(self):
        # isinstance(True, int) is True in Python — bool must be excluded explicitly,
        # or a caller passing True/False through an "int" field silently passes.
        assert bad_nonneg_int(True) is True
        assert bad_nonneg_int(False) is True

    def test_non_int_is_bad(self):
        assert bad_nonneg_int("3") is True
        assert bad_nonneg_int(3.0) is True
        assert bad_nonneg_int(None) is True

    def test_ordinary_values_pass(self):
        assert bad_nonneg_int(0) is False
        assert bad_nonneg_int(42) is False
        assert bad_nonneg_int(MAX_NONNEG_INT) is False

    def test_over_max_is_bad(self):
        assert bad_nonneg_int(MAX_NONNEG_INT + 1) is True

    def test_petabyte_scale_int_accepted(self):
        # The fix must not become a limit on legitimate usage — 10**15 is petabyte-scale,
        # well over any realistic byte tally, well under the int64 ceiling.
        assert bad_nonneg_int(10**15) is False

    def test_digit_encoded_giant_int_rejected_by_the_field_bound(self):
        # The exact defect: a 1.9-MB decimal-digit int passes isinstance(v, int) and
        # v >= 0. Must be rejected BY THE UPPER BOUND, which is what this whole module
        # exists to add.
        giant = _giant_int_from_digits(1.9)
        assert bad_nonneg_int(giant) is True

    def test_custom_max_value_is_honoured(self):
        assert bad_nonneg_int(101, max_value=100) is True
        assert bad_nonneg_int(100, max_value=100) is False


class TestCheckNonnegInt:
    def test_passes_returns_none(self):
        assert check_nonneg_int(42, "bytesIn") is None

    def test_fails_returns_field_scoped_reason(self):
        reason = check_nonneg_int(-1, "bytesIn")
        assert reason is not None
        assert "bytesIn" in reason
        assert "bounded non-negative int" in reason

    def test_digit_encoded_payload_named_by_field_not_a_catch_all(self):
        giant = _giant_int_from_digits(1.9)
        reason = check_nonneg_int(giant, "counts.dropped")
        assert reason is not None
        assert "counts.dropped must be a bounded non-negative int" in reason


class TestBoundedStr:
    def test_over_max_len_is_bad(self):
        assert bad_bounded_str("x" * 300, max_len=256) is True

    def test_within_max_len_passes(self):
        assert bad_bounded_str("x" * 256, max_len=256) is False

    def test_non_str_is_bad(self):
        assert bad_bounded_str(123, max_len=256) is True

    def test_empty_rejected_when_disallowed(self):
        assert bad_bounded_str("", max_len=256, allow_empty=False) is True
        assert bad_bounded_str("", max_len=256, allow_empty=True) is False

    def test_check_bounded_str_reason(self):
        reason = check_bounded_str("x" * 999, "adapter", max_len=256)
        assert reason is not None
        assert "adapter" in reason


class TestCheckTotalSize:
    def test_small_payload_passes(self):
        assert check_total_size({"a": 1}, max_bytes=1024) is None

    def test_oversized_payload_fails_with_byte_count(self):
        payload = {"blob": "x" * 5000}
        reason = check_total_size(payload, max_bytes=1024)
        assert reason is not None
        assert "aggregate cap" in reason

    def test_catches_a_payload_legal_per_field_but_illegal_in_aggregate(self):
        # The whole point of the aggregate backstop: many individually-legal fields can
        # still sum to a real payload. 10_000 entries * two 256-char strings, each within
        # a plausible per-field bound, is still ~5MB in aggregate.
        payload = {"items": [{"a": "x" * 256, "b": "y" * 256} for _ in range(10_000)]}
        assert check_total_size(payload, max_bytes=2 * 1024 * 1024) is not None

    def test_injectable_dumps(self):
        calls = []

        def fake_dumps(p):
            calls.append(p)
            return "{}"

        assert check_total_size({"x": 1}, max_bytes=10, dumps=fake_dumps) is None
        assert calls == [{"x": 1}]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
