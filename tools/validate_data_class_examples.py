#!/usr/bin/env python3
"""Validate the DataClass (OntoDT/OntoDQ) family + its cross-bindings (task #14).

A DataClass is the data-side governance node: ontologically typed (OntoDT), glossary-linked
(biz↔data), domain-bounded (ValidValues), optionally assigned by a TF-Lattice classifier that
is a CATALOGED model (ModelManifest) with a run on Ray/TritFabric and glossary-term labels.

Checks (fail-closed):
  1. schema conformance (with ValidValues $ref resolved);
  2. classifier integrity — kind pinned, modelRef→model-manifest, runRef→run, compute on
     ray|tritfabric, and every label a GlossaryTerm URN (labels live in the glossary);
  3. field↔class domain conformance — an EntityField.dataClassRef binding a DataClass in the
     set must share the DataClass domain 'kind' (a field can't claim a class it doesn't fit);
  4. negative vectors fail on their named keyword.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def registry() -> Registry:
    # Resolve local $refs (e.g. "ValidValues.json") by loading every schema under its $id
    # AND under its bare filename, so relative refs resolve without a network fetch.
    resources = []
    for f in SCHEMAS.glob("*.json"):
        schema = load(f)
        res = Resource.from_contents(schema)
        resources.append((schema.get("$id", f.name), res))
        resources.append((f.name, res))
    return Registry().with_resources(resources)


REG = registry()


def validator_for(schema: dict) -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(schema, registry=REG)


def check_conformance(dataclass_schema, field_schema, dcs, fields) -> None:
    # Validate each collection against its INTENDED schema explicitly — never pick the
    # schema from the instance's own `type`, or a mistyped doc validates against the wrong one.
    for collection, schema in ((dcs, dataclass_schema), (fields, field_schema)):
        for name, d in collection.items():
            errs = sorted(validator_for(schema).iter_errors(d), key=str)
            if errs:
                for e in errs:
                    FAILURES.append(f"{name}: {e.message}")
            else:
                CHECKS[f"schema:{name}"] = True


def check_classifier(dcs) -> None:
    for name, dc in dcs.items():
        clf = dc.get("classifier")
        if not clf:
            CHECKS[f"classifier:{name}:none"] = True
            continue
        if not isinstance(clf, dict):
            FAILURES.append(f"{name}: classifier must be an object")  # type-guard: don't crash on a bad shape
            continue
        labels = clf.get("labels") or []
        compute = clf.get("compute") if isinstance(clf.get("compute"), dict) else {}
        if not all(l.startswith("urn:srcos:glossary:") for l in labels):
            FAILURES.append(f"{name}: classifier labels must all be GlossaryTerm URNs (assigned in the glossary)")
        elif not str(clf.get("modelRef", "")).startswith("urn:srcos:model-manifest:"):
            FAILURES.append(f"{name}: classifier.modelRef must be a ModelManifest (cataloged model)")
        elif not str(clf.get("runRef", "")).startswith("urn:srcos:run:"):
            FAILURES.append(f"{name}: classifier.runRef must be a RunRecord URN (the training run that produced this model)")
        elif compute.get("platform") not in ("ray", "tritfabric"):
            FAILURES.append(f"{name}: classifier compute must run on ray|tritfabric")
        elif clf.get("head") != "logistic":
            FAILURES.append(f"{name}: per-class classifier head must be 'logistic' (one-vs-rest) so the class is individually testable")
        elif not str(clf.get("evalRunRef", "")).startswith("urn:srcos:run:"):
            FAILURES.append(f"{name}: per-class classifier must carry an evalRunRef (RunRecord URN) — the individual test for this class/label")
        else:
            CHECKS[f"classifier:{name}:logistic-individually-testable"] = True


def check_table_classifiers(tcs) -> None:
    """A TableClassifier is the n-ary SOFTMAX; it must align BOTH a LSA bag-of-words and a
    doc2vec sentence-encoder, and be a cataloged model on ray/tritfabric assigning N DataClasses."""
    for name, tc in tcs.items():
        kinds = {e.get("kind") for e in (tc.get("embeddings") or []) if isinstance(e, dict)}
        if tc.get("head") != "softmax":
            FAILURES.append(f"{name}: table classifier head must be 'softmax' (n-ary)")
        elif not {"lsa-bag-of-words", "doc2vec-sentence-encoder"} <= kinds:
            FAILURES.append(f"{name}: softmax must align BOTH lsa-bag-of-words AND doc2vec-sentence-encoder "
                            f"(the n-ary logit→class representations); have {sorted(kinds)}")
        elif not tc.get("modelRef", "").startswith("urn:srcos:model-manifest:"):
            FAILURES.append(f"{name}: modelRef must be a cataloged ModelManifest")
        elif not (tc.get("assignsClasses") and all(c.startswith("urn:srcos:data-class:") for c in tc["assignsClasses"])):
            FAILURES.append(f"{name}: assignsClasses must be DataClass URNs (the N of the n-ary)")
        else:
            CHECKS[f"table-classifier:{name}:softmax-lsa+doc2vec-cataloged"] = True


def check_field_conformance(dcs, fields) -> None:
    by_id = {dc["id"]: dc for dc in dcs.values()}
    for name, fld in fields.items():
        ref = fld.get("dataClassRef")
        if not ref:
            continue
        dc = by_id.get(ref)
        if dc is None:
            continue  # DataClass defined elsewhere
        field_kind = (fld.get("validValues") or {}).get("kind")
        class_kind = (dc.get("domain") or {}).get("kind")
        if field_kind and class_kind and field_kind != class_kind:
            FAILURES.append(f"{name}: validValues.kind {field_kind!r} does not conform to DataClass {ref} "
                            f"domain kind {class_kind!r}")
        else:
            CHECKS[f"field-conforms:{name}"] = True


def check_negatives(dataclass_schema) -> None:
    fx = load(ROOT / "fixtures" / "data-class" / "conformance.json")
    for i, case in enumerate(fx["cases"]):
        if case["schema"] != "DataClass.json":
            continue  # TableClassifier negatives handled in main() against their own schema
        expected = case.get("failValidator")
        try:
            validator_for(dataclass_schema).validate(case["document"])
        except jsonschema.ValidationError as exc:
            if expected is not None and exc.validator != expected:
                FAILURES.append(f"negative {i}: failed on {exc.validator!r}, not {expected!r}: {case['reason']}")
            else:
                CHECKS[f"negative:{i}:{exc.validator}"] = True
            continue
        FAILURES.append(f"negative {i} unexpectedly PASSED: {case['reason']}")


def main() -> int:
    dataclass_schema = load(SCHEMAS / "DataClass.json")
    field_schema = load(SCHEMAS / "EntityField.json")
    table_schema = load(SCHEMAS / "TableClassifier.json")
    dcs = {"data_class.currency.json": load(ROOT / "examples" / "data_class.currency.json")}
    fields = {"entity_field.revenue.json": load(ROOT / "examples" / "entity_field.revenue.json")}
    tcs = {"table_classifier.finance.json": load(ROOT / "examples" / "table_classifier.finance.json")}

    check_conformance(dataclass_schema, field_schema, dcs, fields)
    for name, tc in tcs.items():
        errs = sorted(validator_for(table_schema).iter_errors(tc), key=str)
        if errs:
            for e in errs:
                FAILURES.append(f"{name}: {e.message}")
        else:
            CHECKS[f"schema:{name}"] = True
    check_classifier(dcs)
    check_table_classifiers(tcs)
    check_field_conformance(dcs, fields)
    check_negatives(dataclass_schema)
    # TableClassifier negatives use their own schema
    fx = load(ROOT / "fixtures" / "data-class" / "conformance.json")
    for i, case in enumerate(fx["cases"]):
        if case["schema"] != "TableClassifier.json":
            continue
        try:
            validator_for(table_schema).validate(case["document"])
            FAILURES.append(f"negative {i} (TableClassifier) unexpectedly PASSED: {case['reason']}")
        except jsonschema.ValidationError as exc:
            exp = case.get("failValidator")
            if exp and exc.validator != exp:
                FAILURES.append(f"negative {i} (TableClassifier): failed on {exc.validator!r}, not {exp!r}")
            else:
                CHECKS[f"negative-tc:{i}:{exc.validator}"] = True

    for m in FAILURES:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
