#!/usr/bin/env python3
"""General referential-integrity gate for every schema in schemas/.

The estate has 340 schemas and ~135 ``$ref`` links, but the per-example
validators only exercise the schemas that happen to ship examples. A schema that
declares a ``$ref`` to a moved, renamed, or mistyped target sails straight
through: nothing loads the schema, so nothing notices the reference resolves to
NOTHING. That is the declared-not-enforced defect at the spec's own reference
layer — a schema promising a contract ("this field conforms to
``ContentRef.json#/$defs/x``") that points at a hole.

This validator makes that unrepresentable. For every ``schemas/*.json`` it asserts:

  1. the file is valid JSON and a structurally valid JSON Schema (Draft 2020-12
     metaschema — ``check_schema``); and
  2. every ``$ref`` — internal ``#/…``, relative ``File.json`` (optionally with a
     ``#/…`` fragment), or canonical ``$id`` URI — resolves to an existing schema
     AND an existing pointer target inside it.

Self-exclusion (a self-validating checker must exclude itself, or it "passes" by
never testing its own logic): the real scan targets ``schemas/`` ONLY, and this
validator lives in ``tools/`` — never in the scanned set. Its teeth are proven on
every run by an inline negative control built from SYNTHETIC in-memory schemas
(a dangling file ref, a dangling internal pointer, a malformed schema) — none of
which touch ``schemas/``, so the proof can never pollute the thing being proven.
If that negative control ever fails to trip, the validator exits non-zero and
refuses to certify anything: a gate that cannot fail certifies nothing.

  validate_schema_references.py                 # scan schemas/ (default)
  validate_schema_references.py --schema-dir X  # scan an alternate dir
  validate_schema_references.py --self-test     # run only the negative control
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError:  # pragma: no cover - environment guard
    sys.stderr.write("validate_schema_references: needs `jsonschema` (pip install --user jsonschema)\n")
    raise


# ── pure helpers (no I/O; these are what the negative control pins) ───────────
def iter_refs(node: Any) -> Iterator[str]:
    """Yield every string ``$ref`` value anywhere in a schema document."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                yield value
            else:
                yield from iter_refs(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_refs(item)


def resolve_pointer(doc: Any, fragment: str) -> bool:
    """True if an RFC-6901 JSON pointer fragment resolves inside ``doc``."""
    parts = [p.replace("~1", "/").replace("~0", "~")
             for p in fragment.lstrip("/").split("/") if p != ""]
    node = doc
    for part in parts:
        if isinstance(node, dict):
            if part not in node:
                return False
            node = node[part]
        elif isinstance(node, list):
            try:
                idx = int(part)
            except ValueError:
                return False
            if idx < 0 or idx >= len(node):
                return False
            node = node[idx]
        else:
            return False
    return True


def resolve_ref(ref: str, current_doc: dict, by_id: dict[str, dict],
                by_file: dict[str, dict]) -> tuple[bool, str]:
    """Resolve one ``$ref`` to (ok, reason). Reason is empty when ok."""
    file_part, _, fragment = ref.partition("#")
    if file_part == "":
        target = current_doc
    elif file_part in by_file:                       # "ContentRef.json"
        target = by_file[file_part]
    elif file_part in by_id:                          # full canonical "$id" URI
        target = by_id[file_part]
    elif Path(file_part).name in by_file:            # any path/URL ending in Name.json
        target = by_file[Path(file_part).name]
    else:
        return False, f"$ref to missing schema: {ref!r}"
    if fragment.strip("/") == "":
        return True, ""
    if resolve_pointer(target, fragment):
        return True, ""
    return False, f"$ref pointer does not resolve: {ref!r}"


# ── I/O ───────────────────────────────────────────────────────────────────────
def load_all(schema_dir: Path) -> tuple[dict[str, dict], dict[str, dict], list[tuple[str, str]]]:
    by_file: dict[str, dict] = {}
    by_id: dict[str, dict] = {}
    load_errors: list[tuple[str, str]] = []
    for path in sorted(schema_dir.glob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            load_errors.append((path.name, f"unreadable/invalid JSON: {e}"))
            continue
        by_file[path.name] = doc
        sid = doc.get("$id") if isinstance(doc, dict) else None
        if isinstance(sid, str):
            by_id[sid] = doc
    return by_file, by_id, load_errors


def check_all(schema_dir: Path) -> tuple[list[tuple[str, str]], int, int]:
    by_file, by_id, findings = load_all(schema_dir)
    ref_count = 0
    for name, doc in by_file.items():
        if not isinstance(doc, dict):
            findings.append((name, "top-level schema is not a JSON object"))
            continue
        try:
            Draft202012Validator.check_schema(doc)
        except SchemaError as e:
            findings.append((name, f"not a valid JSON Schema: {e.message}"))
        for ref in iter_refs(doc):
            ref_count += 1
            ok, reason = resolve_ref(ref, doc, by_id, by_file)
            if not ok:
                findings.append((name, reason))
    return findings, len(by_file), ref_count


# ── negative control: prove the gate has teeth, on every run ──────────────────
def _is_rejected_schema(doc: dict) -> bool:
    try:
        Draft202012Validator.check_schema(doc)
        return False
    except SchemaError:
        return True


def _negative_control() -> bool:
    good = {"$id": "https://schemas.srcos.ai/v2/_NC_Good.json", "type": "object",
            "$defs": {"a": {"type": "string"}}}
    by_file = {"_NC_Good.json": good}
    by_id = {good["$id"]: good}
    checks = [
        ("dangling file $ref is caught", resolve_ref("_NC_Missing.json", good, by_id, by_file)[0] is False),
        ("dangling internal pointer is caught", resolve_ref("#/$defs/missing", good, by_id, by_file)[0] is False),
        ("dangling file+fragment is caught", resolve_ref("_NC_Good.json#/$defs/missing", good, by_id, by_file)[0] is False),
        ("valid file $ref resolves", resolve_ref("_NC_Good.json", good, by_id, by_file)[0] is True),
        ("valid internal pointer resolves", resolve_ref("#/$defs/a", good, by_id, by_file)[0] is True),
        ("valid $id $ref resolves", resolve_ref(good["$id"], good, by_id, by_file)[0] is True),
        ("malformed schema is caught", _is_rejected_schema({"type": 123})),
        ("valid schema is accepted", not _is_rejected_schema(good)),
    ]
    passed = all(ok for _, ok in checks)
    for name, ok in checks:
        print(f"    {'OK  ' if ok else 'FAIL'} negative control: {name}")
    return passed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Referential-integrity gate for schemas/.")
    ap.add_argument("--schema-dir", default="schemas", help="directory of *.json schemas to scan")
    ap.add_argument("--self-test", action="store_true", help="run only the negative control")
    args = ap.parse_args(argv)

    # The gate certifies nothing unless it has first proven it can fail.
    if not _negative_control():
        print("FAIL: negative control did not trip — the validator has no teeth; refusing to certify")
        return 2
    if args.self_test:
        print("OK: negative control passed")
        return 0

    schema_dir = Path(args.schema_dir)
    if not schema_dir.is_dir():
        print(f"FAIL: --schema-dir {schema_dir} is not a directory")
        return 2
    findings, n_schemas, n_refs = check_all(schema_dir)
    if n_schemas == 0:
        print(f"FAIL: no schemas found in {schema_dir} — refusing to report a green scan of nothing")
        return 2
    if findings:
        print(f"FAIL: {len(findings)} referential-integrity defect(s) across {n_schemas} schemas:")
        for name, reason in sorted(findings):
            print(f"  {name}: {reason}")
        return 1
    print(f"OK: {n_schemas} schemas structurally valid; all {n_refs} $refs resolve to a real target")
    return 0


if __name__ == "__main__":
    sys.exit(main())
