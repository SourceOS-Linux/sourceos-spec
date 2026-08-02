#!/usr/bin/env python3
"""Validate the Ingestion-Pipeline contract family (the parse -> chunk -> embed seam).

This family exists to end a concrete failure: the estate's ingestion/embedding
pipeline lived only in Noetica's agent-machine doc-store, embedding with its own
ollama client, while prophet-platform already ran a sovereign apps/embeddings
service — two implementations, no guarantee the vectors were even in the same
space. The contract makes the seam portable AND makes vector-space drift
impossible by construction.

Six checks, not one:
  1. schema conformance — every schema is a valid draft-2020-12 document and each
     canonical example validates against its schema;
  2. strictness bar — every schema holds the tranche-0001 bar: top-level
     additionalProperties: false, specVersion pinned to the 0.1.0 const, an
     anchored urn:srcos: id pattern, and a type const equal to the title;
  3. document integrity — IngestedDocument.extractionDigest is RECOMPUTED from the
     document's own `text` (sha256), never read back. A stored digest is an
     assertion about pinning; a recomputed one is pinning;
  4. span soundness — the check the chunk grain exists for. Every Chunk resolves
     to a real IngestedDocument, its span is in-bounds (0 <= start < end <= len),
     its text is EXACTLY documentText[start:end], and its contentHash is the
     sha256 of that text. A chunk that survives all four cannot silently misquote
     the document it cites;
  5. shared vector space — the reason this family exists. EmbeddingRequest pins the
     sovereign model and dimension by const; every embedded Chunk must name that
     same model, that same dimension, and carry a vector of exactly that length.
     A chunk embedded under another model, or truncated to another dimension, is
     a vector in a different space and is refused here rather than compared
     silently downstream;
  6. grounding soundness — every ExtractedEntity resolves to a real document and
     each of its mention spans selects the entity's surface form out of the
     document text, so a claimed grounding always points at real evidence;
plus 7. negative vectors — every case in fixtures/ingestion-pipeline/conformance.json
     FAILS validation, and fails on the exact JSON-Schema keyword it names in
     `failValidator` (so a vector that fails for an unrelated reason is caught).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

DOCUMENT_SCHEMA = "IngestedDocument.json"
CHUNK_SCHEMA = "Chunk.json"
ENTITY_SCHEMA = "ExtractedEntity.json"
EMBED_SCHEMA = "EmbeddingRequest.json"
SCHEMA_NAMES = [DOCUMENT_SCHEMA, CHUNK_SCHEMA, ENTITY_SCHEMA, EMBED_SCHEMA]

DOCUMENT_EXAMPLES = ["ingested_document.json"]
CHUNK_EXAMPLES = ["ingestion_chunk.0.json", "ingestion_chunk.1.json"]
ENTITY_EXAMPLES = ["extracted_entity.json"]
EMBED_EXAMPLES = ["embedding_request.json"]

PAIRS = (
    [(DOCUMENT_SCHEMA, e) for e in DOCUMENT_EXAMPLES]
    + [(CHUNK_SCHEMA, e) for e in CHUNK_EXAMPLES]
    + [(ENTITY_SCHEMA, e) for e in ENTITY_EXAMPLES]
    + [(EMBED_SCHEMA, e) for e in EMBED_EXAMPLES]
)

FAILURES: list[str] = []
CHECKS: dict[str, bool] = {}


def fail(msg: str) -> None:
    FAILURES.append(msg)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------------- 1. conformance
def check_conformance(schemas: dict[str, dict]) -> None:
    for name, schema in schemas.items():
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
            CHECKS[f"schema-valid:{name}"] = True
        except jsonschema.SchemaError as exc:
            fail(f"schema invalid: {name}: {exc.message}")

    for schema_name, example_name in PAIRS:
        example = load(ROOT / "examples" / example_name)
        errors = sorted(jsonschema.Draft202012Validator(schemas[schema_name]).iter_errors(example), key=str)
        if errors:
            for err in errors:
                fail(f"example {example_name} vs {schema_name}: {err.message}")
        else:
            CHECKS[f"example:{example_name}"] = True


# ---------------------------------------------------------------- 2. strictness
def check_strictness(schemas: dict[str, dict]) -> None:
    for name in SCHEMA_NAMES:
        schema = schemas[name]
        if schema.get("additionalProperties") is not False:
            fail(f"{name}: top-level additionalProperties must be false")
        if schema["properties"]["specVersion"].get("const") != "0.1.0":
            fail(f"{name}: specVersion must be pinned to const 0.1.0")
        pattern = schema["properties"]["id"].get("pattern", "")
        if not (pattern.startswith("^urn:srcos:") and pattern.endswith("$")):
            fail(f"{name}: id pattern must be an anchored urn:srcos: pattern")
        if schema["properties"]["type"].get("const") != schema["title"]:
            fail(f"{name}: type const must equal title")
        CHECKS[f"strictness:{name}"] = True


# ------------------------------------------------------- 3. document integrity
def check_document_integrity(documents: dict[str, dict]) -> None:
    for name, doc in documents.items():
        recomputed = sha256(doc["text"])
        if doc["extractionDigest"] != recomputed:
            fail(f"{name}: extractionDigest is not the sha256 of its own text "
                 f"(stored {doc['extractionDigest']}, recomputed {recomputed})")
        else:
            CHECKS[f"document-integrity:{name}"] = True


# ----------------------------------------------------------- 4. span soundness
def check_span_soundness(documents: dict[str, dict], chunks: dict[str, dict]) -> None:
    text_by_urn = {d["id"]: d["text"] for d in documents.values()}
    for name, ch in chunks.items():
        text = text_by_urn.get(ch["documentRef"])
        if text is None:
            fail(f"{name}: documentRef {ch['documentRef']} resolves to no IngestedDocument in the example set")
            continue
        CHECKS[f"span:{name}:document-resolves"] = True

        start, end = ch["span"]["start"], ch["span"]["end"]
        if not (0 <= start < end <= len(text)):
            fail(f"{name}: span ({start},{end}) is out of bounds for a document of length {len(text)}")
            continue
        CHECKS[f"span:{name}:in-bounds"] = True

        if text[start:end] != ch["text"]:
            fail(f"{name}: chunk text is not documentText[{start}:{end}] — the span does not select the chunk it claims")
        else:
            CHECKS[f"span:{name}:span-selects-text"] = True

        if ch["contentHash"] != sha256(ch["text"]):
            fail(f"{name}: contentHash is not the sha256 of the chunk text")
        else:
            CHECKS[f"span:{name}:content-addressed"] = True


# ------------------------------------------------------ 5. shared vector space
def check_shared_vector_space(embed_requests: dict[str, dict], chunks: dict[str, dict]) -> None:
    # The pin is the contract itself (const), materialised by the canonical example.
    pins = {(r["model"], r["dimension"]) for r in embed_requests.values()}
    if len(pins) != 1:
        fail(f"embedding requests disagree on the pinned (model, dimension): {pins} — there must be exactly one space")
        return
    pin_model, pin_dim = next(iter(pins))
    CHECKS["vector-space:single-pin"] = True

    embedded = 0
    for name, ch in chunks.items():
        emb = ch.get("embedding")
        if emb is None:
            continue
        embedded += 1
        if emb["model"] != pin_model:
            fail(f"{name}: embedded under {emb['model']!r}, not the pinned {pin_model!r} — a different, incomparable space")
        elif emb["dimension"] != pin_dim:
            fail(f"{name}: embedding dimension {emb['dimension']} != pinned {pin_dim} — a truncated space is not the same space")
        elif len(emb["vector"]) != emb["dimension"]:
            fail(f"{name}: vector length {len(emb['vector'])} != declared dimension {emb['dimension']} — the vector does not fit its own space")
        else:
            CHECKS[f"vector-space:{name}:in-shared-space"] = True

    if embedded == 0:
        fail("no example chunk carries an embedding — the shared-vector-space path is untested prose")
    else:
        CHECKS["vector-space:path-exercised"] = True


# ---------------------------------------------------------- 6. grounding soundness
def check_grounding(documents: dict[str, dict], entities: dict[str, dict]) -> None:
    text_by_urn = {d["id"]: d["text"] for d in documents.values()}
    for name, ent in entities.items():
        text = text_by_urn.get(ent["documentRef"])
        if text is None:
            fail(f"{name}: documentRef {ent['documentRef']} resolves to no IngestedDocument in the example set")
            continue
        CHECKS[f"grounding:{name}:document-resolves"] = True

        ok = True
        for i, mention in enumerate(ent["mentions"]):
            start, end = mention["span"]["start"], mention["span"]["end"]
            if not (0 <= start < end <= len(text)):
                fail(f"{name}: mention {i} span ({start},{end}) is out of bounds")
                ok = False
            elif text[start:end] != ent["surface"]:
                fail(f"{name}: mention {i} span does not select the surface form {ent['surface']!r} — grounding points at nothing")
                ok = False
        if ok:
            CHECKS[f"grounding:{name}:mentions-select-surface"] = True


# ------------------------------------------------------------ 7. negative vectors
def check_negative_vectors(schemas: dict[str, dict]) -> None:
    fixture = load(ROOT / "fixtures" / "ingestion-pipeline" / "conformance.json")
    for i, case in enumerate(fixture["cases"]):
        schema = schemas[case["schema"]]
        expected = case.get("failValidator")
        try:
            jsonschema.validate(case["document"], schema)
        except jsonschema.ValidationError as exc:
            # Assert it failed for the RIGHT reason — the named JSON-Schema keyword —
            # not merely that it failed somewhere. A negative vector that fails on an
            # unrelated rule is not testing what its `reason` claims.
            if expected is not None and exc.validator != expected:
                fail(f"negative vector {i} ({case['schema']}) failed on {exc.validator!r}, "
                     f"not the expected {expected!r}: {case['reason']}")
            else:
                CHECKS[f"negative:{i}:{case['schema']}:{exc.validator}"] = True
            continue
        fail(f"negative vector {i} ({case['schema']}) unexpectedly PASSED: {case['reason']}")


def main() -> int:
    schemas = {name: load(ROOT / "schemas" / name) for name in SCHEMA_NAMES}
    documents = {n: load(ROOT / "examples" / n) for n in DOCUMENT_EXAMPLES}
    chunks = {n: load(ROOT / "examples" / n) for n in CHUNK_EXAMPLES}
    entities = {n: load(ROOT / "examples" / n) for n in ENTITY_EXAMPLES}
    embed_requests = {n: load(ROOT / "examples" / n) for n in EMBED_EXAMPLES}

    check_conformance(schemas)
    check_strictness(schemas)
    check_document_integrity(documents)
    check_span_soundness(documents, chunks)
    check_shared_vector_space(embed_requests, chunks)
    check_grounding(documents, entities)
    check_negative_vectors(schemas)

    for msg in FAILURES:
        print(f"FAIL: {msg}", file=sys.stderr)

    ok = not FAILURES and all(CHECKS.values())
    print(json.dumps({"ok": ok, "checks": CHECKS}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
