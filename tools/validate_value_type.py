#!/usr/bin/env python3
"""Validate the ValueType structural algebra.

Field types were bare strings — `dataType: "string"`, constrained by nothing and
documented only by the examples in its own description — with optionality as a
sibling boolean and no way at all to express an element type. An array of person
references and a scalar string were the same term to every consumer.

Two properties carry most of the weight, and both are asserted here by rejection:

  * an element type is REQUIRED on every collection, because a collection whose
    element type is unstated is a collection nothing can validate;
  * `optional` does not nest, because a doubly-absent value is not a distinct
    state and permitting it would create two encodings of one thing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"

failures: list[str] = []


def build_validator():
    import jsonschema
    from referencing import Registry, Resource

    resources = []
    for name in ("ValueType.json", "ValidValues.json", "EntityField.json", "TagAssignment.json"):
        path = SCHEMAS / name
        if path.exists():
            schema = json.loads(path.read_text(encoding="utf-8"))
            resources.append((schema["$id"], Resource.from_contents(schema)))
            # Also register by bare filename, since sibling $refs are relative.
            resources.append((name, Resource.from_contents(schema)))
    registry = Registry().with_resources(resources)
    root = json.loads((SCHEMAS / "ValueType.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(root)
    return jsonschema.Draft202012Validator(root, registry=registry)


def case(validator, label: str, term: dict, should_pass: bool) -> None:
    errors = sorted(validator.iter_errors(term), key=lambda e: list(e.path))
    accepted = not errors
    if accepted != should_pass:
        want = "accepted" if should_pass else "rejected"
        got = "accepted" if accepted else f"rejected ({errors[0].message[:90]})"
        failures.append(f"{label}: expected {want}, was {got}")
    else:
        print(f"  {'ACCEPTED' if accepted else 'REJECTED'} {label}")


def main() -> int:
    v = build_validator()

    STR = {"kind": "scalar", "scalar": "string"}
    PERSON = {"kind": "scalar", "scalar": "person"}

    # ── Constructors compose ──────────────────────────────────────────────────
    case(v, "scalar string", STR, True)
    case(v, "attributedString is its own scalar, not string",
         {"kind": "scalar", "scalar": "attributedString"}, True)
    case(v, "person is a primitive, not a bespoke entity per schema", PERSON, True)
    case(v, "optional string", {"kind": "optional", "of": STR}, True)
    case(v, "array of person — the term a bare dataType could not express",
         {"kind": "array", "of": PERSON}, True)
    case(v, "optional array of person (nesting)",
         {"kind": "optional", "of": {"kind": "array", "of": PERSON}}, True)
    case(v, "set of entity references",
         {"kind": "set", "of": {"kind": "entity", "entityRef": "MailMessage", "domain": "mail"}}, True)
    case(v, "enumeration with cases", {"kind": "enumeration", "cases": ["draft", "sent"]}, True)
    case(v, "measurement carries its dimension",
         {"kind": "measurement", "dimension": "information", "unit": "byte"}, True)
    case(v, "record of named typed members",
         {"kind": "record", "fields": [{"name": "to", "title": "To", "type": {"kind": "array", "of": PERSON}}]}, True)
    case(v, "array with cardinality bounds", {"kind": "array", "of": STR, "minItems": 1}, True)

    # ── Negative controls ─────────────────────────────────────────────────────
    case(v, "array with NO element type", {"kind": "array"}, False)
    case(v, "set with NO element type", {"kind": "set"}, False)
    case(v, "optional with nothing inside", {"kind": "optional"}, False)
    case(v, "optional(optional(T)) — absence does not nest",
         {"kind": "optional", "of": {"kind": "optional", "of": STR}}, False)
    case(v, "unknown scalar name", {"kind": "scalar", "scalar": "varchar"}, False)
    case(v, "unknown constructor", {"kind": "tuple", "of": STR}, False)
    case(v, "entity with no entityRef — points somewhere unstated", {"kind": "entity"}, False)
    case(v, "measurement with no dimension — a bare number for a physical quantity",
         {"kind": "measurement", "unit": "kg"}, False)
    case(v, "enumeration with no cases", {"kind": "enumeration", "cases": []}, False)
    case(v, "enumeration with duplicate cases",
         {"kind": "enumeration", "cases": ["a", "a"]}, False)
    case(v, "bare legacy string is not a ValueType", "string", False)
    case(v, "undeclared member on a scalar",
         {"kind": "scalar", "scalar": "string", "length": 10}, False)
    case(v, "record field missing its type",
         {"kind": "record", "fields": [{"name": "to"}]}, False)

    # ── EntityField accepts the structural type ───────────────────────────────
    import jsonschema
    from referencing import Registry, Resource
    resources = []
    for name in ("ValueType.json", "ValidValues.json", "EntityField.json", "TagAssignment.json"):
        p = SCHEMAS / name
        if p.exists():
            s = json.loads(p.read_text(encoding="utf-8"))
            resources.append((s["$id"], Resource.from_contents(s)))
            resources.append((name, Resource.from_contents(s)))
    ef_schema = json.loads((SCHEMAS / "EntityField.json").read_text(encoding="utf-8"))
    ef = jsonschema.Draft202012Validator(ef_schema, registry=Registry().with_resources(resources))
    field = {
        "name": "recipients",
        "dataType": "array",
        "valueType": {"kind": "optional", "of": {"kind": "array", "of": PERSON}},
    }
    errs = sorted(ef.iter_errors(field), key=lambda e: list(e.path))
    if errs:
        failures.append(f"EntityField must accept a structural valueType: {errs[0].message}")
    else:
        print("  ACCEPTED EntityField carrying optional(array(person))")

    if failures:
        print(f"\n{len(failures)} failure(s):\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("\nOK ValueType composes, and a collection cannot omit its element type")
    return 0


if __name__ == "__main__":
    sys.exit(main())
