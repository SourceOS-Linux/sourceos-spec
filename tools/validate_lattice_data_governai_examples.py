#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "schemas" / "DataProduct.json", ROOT / "examples" / "data_product.json"),
    (ROOT / "schemas" / "DataContract.json", ROOT / "examples" / "data_contract.json"),
    (ROOT / "schemas" / "QualityProfile.json", ROOT / "examples" / "quality_profile.json"),
    (ROOT / "schemas" / "AnnotationSet.json", ROOT / "examples" / "annotation_set.json"),
    (ROOT / "schemas" / "EvaluationBundle.json", ROOT / "examples" / "evaluation_bundle.json"),
    (ROOT / "schemas" / "Factsheet.json", ROOT / "examples" / "factsheet.json"),
    (ROOT / "schemas" / "PublicationArtifact.json", ROOT / "examples" / "publication_artifact.json"),
]


def validate_pair(schema_path: Path, example_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema).check_schema(schema)
    example = json.loads(example_path.read_text(encoding="utf-8"))
    jsonschema.validate(example, schema)


def main() -> int:
    checks: dict[str, bool] = {}
    for schema_path, example_path in PAIRS:
        validate_pair(schema_path, example_path)
        checks[example_path.name] = True
    print(json.dumps({"ok": all(checks.values()), "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
