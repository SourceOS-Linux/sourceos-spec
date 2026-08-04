#!/usr/bin/env python3
"""Contract reconciliation — make sourceos-spec the ACTUATED single authority, not a passive one.

The estate is designed so every contract has ONE canonical home (sourceos-spec) and consumers
vendor copies. But nothing enforced it, so contracts got authored elsewhere and never percolated
back (AutonomyAdmissionReceipt, QuorumProof are live in services yet absent from the spec). This
tool is the detection spine for that failure, built on the EXISTING SourceOSRepoManifest design
(ownedSchemas / authorityRepos):

  --emit-registry            Write registry/contract-registry.json from this repo's schemas: the
                             canonical {name -> {$id, sha256, path}} index (the single authority).

  --check-consumer M DIR     Reconcile a consumer against the registry, fail-closed on three gaps:
      ORPHAN       a schema the consumer vendors that no authority repo owns  (GAP 1: percolation)
      STALE        a vendored copy whose sha256 != the canonical one          (GAP 2: propagation)
      UNREGISTERED a schema $id that resolves to no registry entry            (GAP 3: authority)

Every gap it reports is a contract that would otherwise drift silently — exactly how the canon
stopped self-updating.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_GLOBS = ["schemas/**/*.json"]
REGISTRY_PATH = ROOT / "registry" / "contract-registry.json"


def _sha256(text: str) -> str:
    # hash the CANONICAL form (sorted keys) so formatting differences aren't false drift.
    try:
        obj = json.loads(text)
        canon = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    except json.JSONDecodeError:
        canon = text
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _name_of(schema: dict, path: pathlib.Path) -> str:
    sid = schema.get("$id", "")
    if sid:
        return sid.rstrip("/").split("/")[-1].removesuffix(".json").removesuffix(".schema")
    return path.stem.removesuffix(".schema")


def build_registry(root: pathlib.Path = ROOT) -> dict:
    """The canonical index of every $id'd schema this authority repo owns."""
    entries: dict[str, dict] = {}
    for glob in SCHEMA_GLOBS:
        for path in sorted(root.glob(glob)):
            text = path.read_text(encoding="utf-8")
            try:
                schema = json.loads(text)
            except json.JSONDecodeError:
                continue
            sid = schema.get("$id")
            if not sid:
                continue  # sub-schemas without an $id are not canonical contracts
            name = _name_of(schema, path)
            entries[name] = {"$id": sid, "sha256": _sha256(text),
                             "path": str(path.relative_to(root))}
    return {"authority": "SourceOS-Linux/sourceos-spec", "count": len(entries), "contracts": entries}


def check_consumer(manifest_path: pathlib.Path, schemas_dir: pathlib.Path,
                   registry: dict) -> list[str]:
    """Reconcile a consumer's vendored schemas against the canonical registry. Fail-closed."""
    errors: list[str] = []
    by_id = {c["$id"]: (name, c) for name, c in registry["contracts"].items()}
    by_name = registry["contracts"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    owned = set(manifest.get("ownedSchemas", []))  # schemas this consumer authors itself (allowed)
    authority_repos = set(manifest.get("authorityRepos", [])) or {"SourceOS-Linux/sourceos-spec"}
    spec_is_authority = "SourceOS-Linux/sourceos-spec" in authority_repos

    if not schemas_dir.exists():
        return [f"consumer schema dir {schemas_dir} does not exist"]

    for path in sorted(schemas_dir.glob("*.json")):
        text = path.read_text(encoding="utf-8")
        try:
            schema = json.loads(text)
        except json.JSONDecodeError:
            continue
        name = _name_of(schema, path)
        sid = schema.get("$id")

        if name in owned:
            continue  # the consumer legitimately authors this one

        reg = by_name.get(name) or (by_id.get(sid, (None, None))[1] if sid else None)
        if reg is None:
            # GAP 1 / GAP 3: used by a consumer, owned by no authority — no canonical home.
            errors.append(
                f"ORPHAN: '{name}' ({path.name}) is vendored but not in the spec registry and "
                f"not in this repo's ownedSchemas — it has no canonical home. Upstream it to "
                f"sourceos-spec (or declare it in ownedSchemas if this repo is its authority)."
            )
            continue
        if not spec_is_authority:
            errors.append(f"UNREGISTERED: '{name}' resolves to the spec but this manifest does not "
                          f"name sourceos-spec as an authorityRepo")
        if _sha256(text) != reg["sha256"]:
            # GAP 2: the vendored copy has drifted from canonical — a propagation was missed.
            errors.append(
                f"STALE: '{name}' ({path.name}) sha256 {_sha256(text)[:19]}… != canonical "
                f"{reg['sha256'][:19]}… — re-sync from sourceos-spec:{reg['path']}"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit-registry", action="store_true", help="write registry/contract-registry.json")
    ap.add_argument("--check-consumer", nargs=2, metavar=("MANIFEST", "SCHEMAS_DIR"),
                    help="reconcile a consumer's vendored schemas against the registry")
    args = ap.parse_args(argv)

    registry = build_registry()

    if args.emit_registry:
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY_PATH.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {REGISTRY_PATH.relative_to(ROOT)} — {registry['count']} canonical contracts")
        return 0

    if args.check_consumer:
        manifest, schemas_dir = args.check_consumer
        errors = check_consumer(pathlib.Path(manifest), pathlib.Path(schemas_dir), registry)
        if errors:
            print("contract reconciliation FAILED:")
            for e in errors:
                print("  ✗ " + e)
            return 1
        print(f"consumer reconciled OK against {registry['count']} canonical contracts")
        return 0

    print(f"canonical registry: {registry['count']} contracts. Use --emit-registry or --check-consumer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
