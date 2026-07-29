#!/usr/bin/env python3
"""Every declared conformance vector must be executed by something.

Four of the seven §9 vectors — T2, T3, T5 and T6 — were declared in
fixtures/pattern-warrant/conformance.json and run by no code. They read as
coverage: a reviewer opening the fixture sees seven named properties with
expectations, and nothing distinguishes the three that were checked from the
four that were not.

That is the same construction habit this repo set out to name — a governance
artifact fully declared and never read. A conformance vector nothing executes
asserts exactly as much as a comment, while looking considerably more like a
guarantee.

This closes the loop structurally rather than by vigilance: adding a vector to a
fixture without wiring it into a validator now fails the build.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"

# Vector-set fixture -> the callable that must cover its ids.
# A new conformance fixture with no entry here is itself a failure: it would
# otherwise be declared and unexecuted, which is the condition being prevented.
COVERAGE = {
    "pattern-warrant/conformance.json": ("validate_pattern_warrant_examples", "executed_vector_ids"),
}


def declared_ids(path: Path) -> list[str]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    vectors = doc.get("vectors", doc if isinstance(doc, list) else [])
    return [v["id"] for v in vectors if isinstance(v, dict) and "id" in v]


def main() -> int:
    sys.path.insert(0, str(ROOT / "tools"))
    failures: list[str] = []

    fixtures = sorted(p for p in FIXTURES.rglob("conformance.json"))
    if not fixtures:
        print("no conformance fixtures found", file=sys.stderr)
        return 1

    for path in fixtures:
        rel = str(path.relative_to(FIXTURES))
        if rel not in COVERAGE:
            failures.append(
                f"{rel}: declares vectors but no validator is registered in COVERAGE; "
                "an unexecuted vector set is indistinguishable from coverage it does not provide"
            )
            continue

        module_name, attr = COVERAGE[rel]
        module = __import__(module_name)
        executed = set(getattr(module, attr)())
        declared = declared_ids(path)

        missing = [v for v in declared if v not in executed]
        if missing:
            failures.append(
                f"{rel}: vector(s) {', '.join(missing)} declared but executed by nothing"
            )
        # A validator claiming to cover a vector the fixture never declared is the
        # mirror defect: coverage reported against a property no one specified.
        phantom = [v for v in executed if v not in declared]
        if phantom:
            failures.append(
                f"{rel}: validator reports vector(s) {', '.join(sorted(phantom))} "
                "that the fixture does not declare"
            )
        if not missing and not phantom:
            print(f"  {len(declared)}/{len(declared)} vectors executed  {rel}  ({', '.join(declared)})")

    if failures:
        print(f"\n{len(failures)} failure(s):\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("\nOK every declared conformance vector is executed by a validator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
