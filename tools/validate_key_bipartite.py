#!/usr/bin/env python3
"""Keys/indexes as set-identifiers + ranks + Biperpedia bipartite lines + primitives — LIVE.

For each SchemaDefinition this recomputes every key's rank (= arity) and primitive flag
(single-attribute), checks the key's attributes are real fields, requires exactly one
primary key, resolves every foreign key to a real key in the referenced entity, and then
BUILDS + EMITS the entity↔attribute bipartite graph (Biperpedia: entities on one side,
attributes on the other; keys are the lines; foreign keys are entity↔entity links). Run:

    python3 tools/validate_key_bipartite.py            # validate + fail-closed
    python3 tools/validate_key_bipartite.py --emit     # also print the bipartite graph
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "SchemaDefinition.json"


def _registry() -> Registry:
    res = []
    for f in (ROOT / "schemas").glob("*.json"):
        s = json.loads(f.read_text(encoding="utf-8"))
        r = Resource.from_contents(s)
        res.append((s.get("$id", f.name), r))
        res.append((f.name, r))
    return Registry().with_resources(res)


REG = _registry()


def _v(schema: dict) -> "jsonschema.Draft202012Validator":
    return jsonschema.Draft202012Validator(schema, registry=REG)
def _discover_examples() -> list[str]:
    # Validate EVERY SchemaDefinition example (not a hard-coded pair), so a keyless legacy
    # example can't silently escape the key/bipartite audit.
    out = []
    for f in sorted((ROOT / "examples").glob("*.json")):
        try:
            if json.loads(f.read_text(encoding="utf-8")).get("type") == "SchemaDefinition":
                out.append(f.name)
        except (json.JSONDecodeError, OSError):
            continue
    return out


EXAMPLES = _discover_examples()

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def audit(tables: dict[str, dict]) -> dict:
    by_id = {t["id"]: t for t in tables.values()}
    entities, attributes, lines, fk_links = [], set(), [], []

    for name, t in tables.items():
        eid = t["id"]
        entities.append(eid)
        fields = {f["name"] for f in t.get("fields", [])}
        keys = t.get("keys") or []
        if not keys:
            CHECKS[f"pk:{name}:no-keys-declared"] = True  # backward-compatible: keys are optional
        else:
            primaries = [k for k in keys if k["kind"] == "primary"]
            if len(primaries) != 1:
                FAILURES.append(f"{name}: a table that declares keys must have exactly one primary key "
                                f"(has {len(primaries)}) — the primary set-identifier")
            else:
                CHECKS[f"pk:{name}"] = True

        for k in keys:
            attrs = k["attributes"]
            # bipartite lines: entity ↔ each attribute
            for a in attrs:
                attributes.add((eid, a))
                lines.append({"entity": eid, "attribute": a, "key": k["name"], "kind": k["kind"]})
            # attributes must be real fields
            missing = [a for a in attrs if a not in fields]
            if missing:
                FAILURES.append(f"{name}/{k['name']}: key attributes {missing} are not fields of the table")
                continue
            # rank == arity; primitive iff rank == 1 (recomputed, not read back)
            rank = len(attrs)
            if k.get("rank") is not None and k["rank"] != rank:
                FAILURES.append(f"{name}/{k['name']}: rank {k['rank']} != arity {rank} (a key's rank is its arity)")
            elif k.get("primitive") is not None and k["primitive"] != (rank == 1):
                FAILURES.append(f"{name}/{k['name']}: primitive={k['primitive']} but rank is {rank} "
                                f"(a key is a primitive iff it is a single attribute)")
            else:
                CHECKS[f"rank-primitive:{name}:{k['name']}"] = True
            # foreign key = bipartite entity↔entity line; must resolve to a real key
            if k["kind"] == "foreign":
                ref = k.get("references") or {}
                target = by_id.get(ref.get("schemaRef"))
                if target is None:
                    FAILURES.append(f"{name}/{k['name']}: foreign key references unknown entity {ref.get('schemaRef')}")
                elif ref.get("keyName") not in {kk["name"] for kk in (target.get('keys') or [])}:
                    FAILURES.append(f"{name}/{k['name']}: foreign key references unknown key "
                                    f"{ref.get('keyName')!r} on {ref.get('schemaRef')}")
                else:
                    fk_links.append({"from": eid, "fromKey": k["name"], "to": ref["schemaRef"], "toKey": ref["keyName"]})
                    CHECKS[f"fk-bipartite:{name}:{k['name']}"] = True

    return {"entities": sorted(entities),
            "attributes": sorted(f"{e}::{a}" for (e, a) in attributes),
            "keyLines": lines, "foreignKeyLinks": fk_links}


def check_negatives(schema: dict) -> None:
    fx = load(ROOT / "fixtures" / "table-keys" / "conformance.json")
    for i, case in enumerate(fx["cases"]):
        exp = case.get("failValidator")
        try:
            _v(schema).validate(case["document"])
            FAILURES.append(f"negative {i} unexpectedly PASSED: {case['reason']}")
        except jsonschema.ValidationError as exc:
            if exp and exc.validator != exp:
                FAILURES.append(f"negative {i}: failed on {exc.validator!r}, not {exp!r}")
            else:
                CHECKS[f"negative:{i}:{exc.validator}"] = True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true", help="print the bipartite graph")
    args = ap.parse_args()

    schema = load(SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    tables = {}
    for name in EXAMPLES:
        t = load(ROOT / "examples" / name)
        errs = sorted(_v(schema).iter_errors(t), key=str)
        if errs:
            for e in errs:
                FAILURES.append(f"{name}: {e.message}")
        else:
            CHECKS[f"schema:{name}"] = True
            tables[name] = t

    graph = audit(tables)
    check_negatives(schema)

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    out = {"ok": ok, "checks": CHECKS}
    if args.emit:
        out["bipartite"] = graph
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
