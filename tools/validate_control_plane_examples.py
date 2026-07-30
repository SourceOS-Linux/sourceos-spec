#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "control-plane" / "ReleaseSet.json", ROOT / "examples" / "release_set.json"),
    (ROOT / "schemas" / "control-plane" / "Fingerprint.json", ROOT / "examples" / "fingerprint.json"),
    (ROOT / "schemas" / "control-plane" / "BootReleaseSet.json", ROOT / "examples" / "boot_release_set.json"),
    (ROOT / "schemas" / "control-plane" / "EnrollmentToken.json", ROOT / "examples" / "enrollment_token.json"),
]


SCHEMAS = ROOT / "schemas"


def resolve_legacy_ref(schema_path: Path, legacy_ref: str) -> Path:
    """Resolve a wrapper's `$ref`, refusing anything that escapes the schema tree.

    `$ref` is schema *content*, so it is attacker-controlled the moment anyone can open a
    pull request: this validator runs in CI (`make validate` -> the aggregate target,
    invoked by .github/workflows/validate-ops-history.yml), and the unconfined
    `(schema_path.parent / legacy_ref).resolve()` let a planted `../../../..` ref make it
    read arbitrary files on the runner. Demonstrated before this guard existed: it read a
    file outside the repository entirely and still exited 0.

    The boundary is the `schemas/` tree, NOT the wrapper's own directory. Both shapes in
    use are legitimate and must keep working:
        ReleaseSet.json   -> "../ReleaseSet.json"            (up into schemas/)
        BootReleaseSet.json -> "./boot-release-set.schema.json" (sibling)
    Confining to the wrapper's directory would reject the first and break the gate — the
    tighter rule is not the safer one here, it is just the wrong one.
    """
    if "\x00" in legacy_ref:
        raise ValueError(f"{schema_path.name}: $ref contains NUL")
    base = SCHEMAS.resolve()
    target = (schema_path.parent / legacy_ref).resolve()
    if target != base and base not in target.parents:
        raise ValueError(
            f"{schema_path.name}: $ref {legacy_ref!r} resolves to {target}, outside {base}; "
            "a legacy $ref must name a schema inside the schema tree"
        )
    return target


def validate_pair(schema_path: Path, example_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema).check_schema(schema)
    legacy_ref = schema.get("allOf", [{}])[0].get("$ref")
    # The wrapper schema delegates validation to the legacy sibling schema it $refs
    # (a relative path like "./release-set.schema.json"), so resolve it against the
    # wrapper's directory. (Path.with_name rejects names containing "/".)
    validation_schema_path = resolve_legacy_ref(schema_path, legacy_ref) if legacy_ref else schema_path
    validation_schema = json.loads(validation_schema_path.read_text(encoding="utf-8"))
    example = json.loads(example_path.read_text(encoding="utf-8"))
    jsonschema.validate(example, validation_schema)


def main() -> int:
    checks: dict[str, bool] = {}
    for schema_path, example_path in PAIRS:
        validate_pair(schema_path, example_path)
        checks[example_path.name] = True
    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
