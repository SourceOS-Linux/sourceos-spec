#!/usr/bin/env python3
"""Assert a vendored estate-safety-kit copy is byte-identical to the canonical source it
claims to be pinned to.

The consumer-side half of the vendoring contract described in ../PROVENANCE.md: each
consumer (socioprophet's app-vue/client-vue, prophet-platform's health-twin, ...) copies a
file from this kit VERBATIM and records a `PROVENANCE.txt` alongside it naming the source
repo, path, and commit SHA it was copied from. A `version` field, or a comment saying "kept
in sync", is not evidence — the only evidence that a vendored copy is still what it claims
to be is the bytes matching what is actually at that pinned commit. This is the estate's
existing vendor-freshness discipline (see prophet-platform's
`tools/assert_vendored_engine_marker.py`), applied to source files instead of a tarball
member: same shape, byte comparison instead of marker-substring containment, because a
small source file can be diffed exactly rather than merely probed for a discriminating
string.

Two sources for the canonical bytes, so this runs the same way locally and in CI:

  --source-root PATH   read `PATH/<source-path>` directly (a local sourceos-spec checkout,
                        e.g. this repo, or a CI job that actions/checkout's it as a sibling).
                        Ignores whatever commit that checkout currently has PATH at — it
                        reads the working tree as-is, so pass a checkout that is actually
                        AT `source-commit` (or accept this as "does the file match what is
                        on disk right now", a looser but zero-network check).
  (no --source-root)   fetch `https://raw.githubusercontent.com/<source-repo>/<source-commit>
                        /<source-path>` over the network. This is the one that actually
                        proves the pin (the exact historical commit), and is what CI should
                        run.

Usage:
  check_vendored_safety_kit.py <vendored-file> [--provenance PROVENANCE.txt]
                                [--source-root PATH] [--timeout SECONDS]

PROVENANCE.txt is `key: value` lines (see ../PROVENANCE.md for the full contract):
  source-repo:   SourceOS-Linux/sourceos-spec
  source-path:   estate-safety-kit/js/urlSafe.ts
  source-commit: <40-hex sha>
  vendored-path: (informational; not required to match the CLI argument)

Exit 0 and print a receipt on success; exit 1 with the reason on failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

# A vendored safety-kit file is source code measured in KB, not a bundle. 4 MiB is
# generous headroom over anything this kit will ever hold and still bounds a fetch of
# unverified-until-hashed bytes, matching the discipline in assert_vendored_engine_marker.py
# (never read a not-yet-trusted artifact unbounded into memory).
MAX_FETCH_BYTES = 4 * 1024 * 1024

_SHA_RE_LEN = 40  # git commit SHAs this tool accepts are full, not abbreviated —
                   # an abbreviated SHA is not a stable pin (it can become ambiguous
                   # as the repo grows) and silently truncating to it here would let
                   # a PROVENANCE.txt entry look pinned when it is not.


def parse_provenance(path: Path) -> dict[str, str]:
    if not path.exists():
        raise SystemExit(f"ERR: provenance file not found: {path}")
    fields: dict[str, str] = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise SystemExit(f"ERR: {path}:{lineno}: not a 'key: value' line: {raw!r}")
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    for required in ("source-repo", "source-path", "source-commit"):
        if not fields.get(required):
            raise SystemExit(f"ERR: {path} is missing required field {required!r}")
    commit = fields["source-commit"]
    if len(commit) != _SHA_RE_LEN or not all(c in "0123456789abcdef" for c in commit.lower()):
        raise SystemExit(
            f"ERR: {path} source-commit {commit!r} is not a full 40-hex commit SHA — "
            "an abbreviated or symbolic ref is not a stable pin"
        )
    return fields


def fetch_canonical(fields: dict[str, str], *, source_root: Path | None, timeout: float) -> bytes:
    if source_root is not None:
        p = source_root / fields["source-path"]
        if not p.exists():
            raise SystemExit(f"ERR: {p} does not exist under --source-root {source_root}")
        data = p.read_bytes()
        if len(data) > MAX_FETCH_BYTES:
            raise SystemExit(f"ERR: {p} is {len(data)} bytes, over the {MAX_FETCH_BYTES}-byte cap — refusing to read")
        return data

    url = (
        f"https://raw.githubusercontent.com/{fields['source-repo']}/"
        f"{fields['source-commit']}/{fields['source-path']}"
    )
    req = urllib.request.Request(url, headers={"Accept": "text/plain"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read(MAX_FETCH_BYTES + 1)
    except HTTPError as exc:
        raise SystemExit(f"ERR: fetching {url} failed: HTTP {exc.code}")
    except URLError as exc:
        raise SystemExit(f"ERR: fetching {url} failed: {exc.reason}")
    if len(data) > MAX_FETCH_BYTES:
        raise SystemExit(f"ERR: {url} is over the {MAX_FETCH_BYTES}-byte cap — refusing to read")
    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vendored_file", type=Path)
    ap.add_argument("--provenance", type=Path, default=None,
                    help="defaults to PROVENANCE.txt next to the vendored file")
    ap.add_argument("--source-root", type=Path, default=None,
                    help="read the canonical file from a local checkout instead of fetching over the network")
    ap.add_argument("--timeout", type=float, default=15.0)
    args = ap.parse_args(argv)

    if not args.vendored_file.exists():
        print(f"ERR: vendored file not found: {args.vendored_file}", file=sys.stderr)
        return 1

    provenance_path = args.provenance or (args.vendored_file.parent / "PROVENANCE.txt")
    fields = parse_provenance(provenance_path)

    vendored_bytes = args.vendored_file.read_bytes()
    canonical_bytes = fetch_canonical(fields, source_root=args.source_root, timeout=args.timeout)

    vendored_digest = hashlib.sha256(vendored_bytes).hexdigest()
    canonical_digest = hashlib.sha256(canonical_bytes).hexdigest()
    drifted = vendored_bytes != canonical_bytes

    receipt = {
        "tool": "sourceos-spec.check_vendored_safety_kit.v1",
        "vendored_file": str(args.vendored_file),
        "provenance_file": str(provenance_path),
        "source_repo": fields["source-repo"],
        "source_path": fields["source-path"],
        "source_commit": fields["source-commit"],
        "vendored_sha256": vendored_digest,
        "canonical_sha256": canonical_digest,
        "byte_identical": not drifted,
        "checked_against": "local --source-root" if args.source_root else "raw.githubusercontent.com (network)",
        "non_claims": [
            "Proves byte-identity to the file at the pinned commit; does NOT judge whether "
            "that commit is itself trustworthy or current — see PROVENANCE.md's re-vendoring "
            "section for that.",
        ],
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if drifted:
        print(
            f"ERR: {args.vendored_file} has DRIFTED from {fields['source-repo']}@"
            f"{fields['source-commit']}:{fields['source-path']} — re-vendor the file or "
            "update the pin, do not hand-edit the vendored copy",
            file=sys.stderr,
        )
        return 1
    print(f"OK: {args.vendored_file} is byte-identical to the pinned source", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
