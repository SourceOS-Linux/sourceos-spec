#!/usr/bin/env python3
"""The reconciliation tool catches the three drift gaps that stopped the canon self-updating."""
import json
import pathlib

import reconcile_contracts as rc

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _write(d: pathlib.Path, name: str, obj: dict):
    (d / name).write_text(json.dumps(obj), encoding="utf-8")


def test_registry_has_known_contracts():
    reg = rc.build_registry()
    assert reg["count"] > 100
    assert "BootProofRecord" in reg["contracts"]           # properly synced


def test_previously_orphaned_contracts_are_now_upstreamed():
    # AutonomyAdmissionReceipt + QuorumProof were live in services but absent from the spec.
    # This branch upstreams them under the canonical sourceos.dev kebab-versioned names, so they
    # now have a home. (The PascalCase consumer copies still need re-vendoring — see CONTRACTS.md.)
    reg = rc.build_registry()
    assert "quorum-proof.v1.1" in reg["contracts"]
    assert "autonomy-admission-receipt.v0.2" in reg["contracts"]


def test_clean_vendored_copy_reconciles(tmp_path):
    reg = rc.build_registry()
    boot = reg["contracts"]["BootProofRecord"]
    schemas = tmp_path / "schemas"; schemas.mkdir()
    # copy the canonical schema verbatim
    (schemas / "BootProofRecord.json").write_text((ROOT / boot["path"]).read_text(), encoding="utf-8")
    manifest = tmp_path / "m.json"; manifest.write_text(json.dumps({"authorityRepos": ["SourceOS-Linux/sourceos-spec"]}))
    assert rc.check_consumer(manifest, schemas, reg) == []


def test_orphan_is_caught(tmp_path):
    reg = rc.build_registry()
    schemas = tmp_path / "schemas"; schemas.mkdir()
    _write(schemas, "AutonomyAdmissionReceipt.v0.2.json",
           {"$id": "https://socioprophet.org/contracts/AutonomyAdmissionReceipt.v0.2.json", "title": "AutonomyAdmissionReceipt"})
    manifest = tmp_path / "m.json"; manifest.write_text(json.dumps({"authorityRepos": ["SourceOS-Linux/sourceos-spec"]}))
    errs = rc.check_consumer(manifest, schemas, reg)
    assert any(e.startswith("ORPHAN") and "AutonomyAdmissionReceipt" in e for e in errs), errs


def test_owned_schema_is_allowed(tmp_path):
    # A repo that legitimately AUTHORS a schema (declares it in ownedSchemas) is not an orphan.
    reg = rc.build_registry()
    schemas = tmp_path / "schemas"; schemas.mkdir()
    _write(schemas, "MyOwnThing.json", {"$id": "https://x/MyOwnThing.json", "title": "MyOwnThing"})
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps({"ownedSchemas": ["MyOwnThing"], "authorityRepos": ["SourceOS-Linux/sourceos-spec"]}))
    assert rc.check_consumer(manifest, schemas, reg) == []


def test_stale_copy_is_caught(tmp_path):
    reg = rc.build_registry()
    boot = reg["contracts"]["BootProofRecord"]
    original = json.loads((ROOT / boot["path"]).read_text())
    original["__drift__"] = "a field the consumer's stale copy has that canonical does not"
    schemas = tmp_path / "schemas"; schemas.mkdir()
    _write(schemas, "BootProofRecord.json", original)
    manifest = tmp_path / "m.json"; manifest.write_text(json.dumps({"authorityRepos": ["SourceOS-Linux/sourceos-spec"]}))
    errs = rc.check_consumer(manifest, schemas, reg)
    assert any(e.startswith("STALE") and "BootProofRecord" in e for e in errs), errs


def test_missing_consumer_dir_fails_closed(tmp_path):
    reg = rc.build_registry()
    errs = rc.check_consumer(tmp_path / "nope.json", tmp_path / "nope", reg)
    assert errs and "does not exist" in errs[0]
