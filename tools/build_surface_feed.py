#!/usr/bin/env python3
"""Build a surface feed JSON from real runtime state.

Each Tier-2 surface (b11 / e11 / turn-witness) reads ./data/<name>.json at load
and declares its provenance. This producer is the "wire to live state" seam: the
runtime calls it with the real payload (netwatch snapshot, consent-plane catalog,
parsed turns) and it stamps provenance="live". Called with no live input, it keeps
the committed sample and stamps provenance="sample" — so the surface never lies
about whether it is showing live or seed data.

Pure stdlib so it runs the same in CI, on device, and in tests.
"""
from __future__ import annotations
import argparse, datetime, json, sys
from pathlib import Path

REQUIRED = {
    "b11": ["spaces", "tripwires", "transitions"],
    "e11": ["surfaces", "receipts", "governor"],
    "turn-witness": ["turns"],
}
SOURCE_HINT = {
    "b11": "netwatch snapshot + guardrail-fabric transitions",
    "e11": "consent-plane catalog (spaces_v1.yaml) + receipt stream + Governor queue",
    "turn-witness": "App-Intents parser output",
}


def assemble(surface: str, payload: dict, live: bool) -> dict:
    if surface not in REQUIRED:
        raise ValueError(f"unknown surface {surface!r}; expected {sorted(REQUIRED)}")
    missing = [k for k in REQUIRED[surface] if k not in payload]
    if missing:
        raise ValueError(f"{surface}: payload missing required keys {missing}")
    for k in REQUIRED[surface]:
        if not isinstance(payload[k], list):
            raise ValueError(f"{surface}: '{k}' must be a list")
    feed = {
        "provenance": "live" if live else "sample",
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": SOURCE_HINT[surface] if live else f"sample seed ({SOURCE_HINT[surface]})",
    }
    feed.update({k: payload[k] for k in payload})
    return feed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build a surface feed from real state.")
    ap.add_argument("--surface", required=True, choices=sorted(REQUIRED))
    ap.add_argument("--input", type=Path, help="JSON payload from the runtime; omit to re-stamp the sample")
    ap.add_argument("--out", type=Path, help="output path (default docs/surfaces/data/<surface>.json)")
    a = ap.parse_args(argv)
    out = a.out or Path(__file__).resolve().parents[1] / "docs" / "surfaces" / "data" / f"{a.surface}.json"
    if a.input:
        payload = json.loads(a.input.read_text())
        live = True
    else:
        payload = {k: v for k, v in json.loads(out.read_text()).items()
                   if k not in ("provenance", "generated_at", "source")}
        live = False
    feed = assemble(a.surface, payload, live)
    out.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n")
    print(f"{a.surface}: wrote {out} (provenance={feed['provenance']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
