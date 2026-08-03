"""Bounded non-negative integer / bounded-payload validation — generalized.

ESTATE SAFETY KIT — canonical source. See ../PROVENANCE.md for what this closes, which
repo hit the defect first, and the vendoring contract every consumer must follow. Do not
edit a vendored copy directly — edit this file, re-vendor, done.

THE DEFECT, first caught in prophet-platform's compute-gateway exhaust guard
(`apps/compute-gateway/src/compute_gateway/engine.py`, closed in PR #1118 after an
adversarial review of PR #1104 flagged it): "must be a non-negative int" is a type/sign
check, NOT a size bound, because Python ints are arbitrary precision.

    def _bad_nonneg_int(v) -> bool:
        return isinstance(v, bool) or not isinstance(v, int) or v < 0

passes `isinstance(v, int) and v >= 0` for a 1.9-million-digit integer just fine. A field
declared "a non-negative int" that is actually unbounded is exactly the "dimension nobody
enumerated" shape prophet-platform#1071 warned about generally: every individual field
check was declarative, not enforcing, and only an aggregate JSON-size backstop caught the
smuggled payload — which means a caller who trips it gets a catch-all reason with no idea
which field regressed.

THE FIX: an explicit upper bound alongside the type/sign check, applied to every int field
a validator touches — not just the ones someone remembered while writing the schema.
`MAX_NONNEG_INT = 2**63 - 1` (int64 max) is the default: above any realistic byte count or
event tally (it exceeds exabyte scale), but small enough to refuse a digit-encoded blob
dressed as a "number". Callers with a tighter natural ceiling (a page count, a retry count)
should pass their own `max_value` — the default is a sane BACKSTOP, not a recommendation
that every field actually needs 63 bits of headroom.

WHY THIS MATTERS BEYOND ONE FIELD: the same "type check without a size bound" shape closes
over labels and free-text too (a "short label string" with no `max_len` is not bounded), so
this module also carries `bad_bounded_str` / `check_bounded_str` for that half of the same
defect class, and `check_total_size` as the deliberately-last aggregate backstop — sized by
measurement of the legitimate ceiling, not guessed, and consulted last so it does not
restate the per-field assumptions it exists to catch when they are wrong.
"""
from __future__ import annotations

__all__ = [
    "MAX_NONNEG_INT",
    "bad_nonneg_int",
    "check_nonneg_int",
    "bad_bounded_str",
    "check_bounded_str",
    "check_total_size",
]

# int64 max. See module docstring for the sizing rationale.
MAX_NONNEG_INT: int = 2**63 - 1


def bad_nonneg_int(v: object, *, max_value: int = MAX_NONNEG_INT) -> bool:
    """Return True if `v` is NOT an acceptable bounded non-negative int.

    `bool` is excluded first — `isinstance(True, int)` is True in Python, so a caller
    passing a bool through a field typed "int" would otherwise silently pass.
    """
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        return True
    return v > max_value


def check_nonneg_int(v: object, field: str, *, max_value: int = MAX_NONNEG_INT) -> str | None:
    """Return None if `v` passes for `field`, else a field-scoped reason string — never a
    catch-all. Mirrors the reason-string shape compute-gateway's callers already parse:
    "<field> must be a bounded non-negative int (<= <max_value>)"."""
    if bad_nonneg_int(v, max_value=max_value):
        return f"{field} must be a bounded non-negative int (<= {max_value})"
    return None


def bad_bounded_str(v: object, *, max_len: int, allow_empty: bool = True) -> bool:
    """Return True if `v` is NOT an acceptable bounded string: must be `str`, within
    `max_len`, and non-empty unless `allow_empty=True`. The same "type check with no size
    bound" defect applies to strings — a label field with no `max_len` is not bounded
    just because it is typed `str`."""
    if not isinstance(v, str):
        return True
    if not allow_empty and len(v) == 0:
        return True
    return len(v) > max_len


def check_bounded_str(v: object, field: str, *, max_len: int, allow_empty: bool = True) -> str | None:
    """Return None if `v` passes for `field`, else a field-scoped reason string."""
    if bad_bounded_str(v, max_len=max_len, allow_empty=allow_empty):
        return f"{field} must be a bounded string (<= {max_len} chars)"
    return None


def check_total_size(payload: object, *, max_bytes: int, dumps=None) -> str | None:
    """Aggregate backstop: serialize `payload` (JSON by default) and refuse it over
    `max_bytes`. Deliberately the LAST check a caller should run, and deliberately NOT
    derived from the per-field bounds above — deriving it would make it restate the same
    assumptions it exists to catch when one of them is wrong or missing. Closes the
    dimensions nobody enumerated a per-field bound for at all, at the cost of a reason
    that cannot say which field is at fault (that imprecision is the tradeoff for being
    the check that still fires when a per-field bound was simply never written).

    `dumps` is injectable so a caller already serializing the payload for other reasons
    (or wanting non-JSON accounting) is not forced to serialize it twice with a different
    encoder; defaults to `json.dumps(payload, separators=(",", ":"))` (compact, matching
    what would actually go over the wire).
    """
    if dumps is None:
        import json as _json

        def dumps(p: object) -> str:
            return _json.dumps(p, separators=(",", ":"))

    size = len(dumps(payload).encode("utf-8"))
    if size > max_bytes:
        return f"payload is {size} bytes, exceeds the {max_bytes}-byte aggregate cap"
    return None
