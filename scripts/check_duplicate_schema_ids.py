#!/usr/bin/env python3
"""Fail if JSON Schemas define duplicate $id values.

This guardrail prevents the spec from drifting into multi-authority schema identity.

We scan:
- schemas/*.json
- schemas/control-plane/*.json
- schemas/control-plane/*.schema.json

Rules:
- Each `$id` must be unique across the repository.
- If a schema lacks `$id`, it is ignored (some sub-schemas may omit it).

Exit:
- 0 if no duplicates found
- 1 if duplicates exist
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    repo = Path(__file__).resolve().parents[1]

    globs = [
        repo / "schemas",
        repo / "schemas" / "control-plane",
    ]

    paths: list[Path] = []
    for root in globs:
        if not root.exists():
            continue
        for p in root.glob("*.json"):
            paths.append(p)
        for p in root.glob("*.schema.json"):
            paths.append(p)

    seen: dict[str, Path] = {}
    dups: list[tuple[str, Path, Path]] = []

    for p in sorted(set(paths)):
        try:
            obj = load_json(p)
        except Exception as e:
            print(f"WARN: could not parse {p}: {e}", file=sys.stderr)
            continue

        sid = obj.get("$id")
        if not sid:
            continue

        if sid in seen:
            dups.append((sid, seen[sid], p))
        else:
            seen[sid] = p

    if dups:
        print("ERROR: duplicate schema $id values detected:", file=sys.stderr)
        for sid, a, b in dups:
            rel_a = a.relative_to(repo)
            rel_b = b.relative_to(repo)
            print(f"- {sid}\n  - {rel_a}\n  - {rel_b}", file=sys.stderr)
        return 1

    print(f"OK: {len(seen)} unique schema $id values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
