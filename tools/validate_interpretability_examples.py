#!/usr/bin/env python3
"""Validate interpretability/SAE contract coverage fixtures.

The catalog fixture is intentionally compact. This validator expands each entry
into the three canonical contracts introduced in v0.1:

- ArtifactSourceLock
- ProviderBinding
- InterventionSpec

It then runs JSON Schema validation and semantic checks for the dimensions that
make the harness model-family agnostic without collapsing artifact kinds.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

CATALOG = ROOT / "examples/interpretability/sae-catalog.v0.json"
SOURCE_SCHEMA = ROOT / "schemas/interpretability/artifact-source-lock.v0.json"
PROVIDER_SCHEMA = ROOT / "schemas/interpretability/provider-binding.v0.json"
INTERVENTION_SCHEMA = ROOT / "schemas/interpretability/intervention-spec.v0.json"

REQUIRED_DECOMPOSITION_TYPES = {
    "standard_sae",
    "transcoder_clt",
    "weight_sparse_native",
    "lorsa_attention",
    "matryoshka_sae",
    "temporal_sae",
    "multi_topk_sae",
    "batch_topk_sae",
    "feature_splitting_study",
    "compound_decomposition",
}

REQUIRED_AUTHOR_CLASSES = {
    "model_author",
    "research_lab",
    "safety_research",
    "commercial_interp",
    "individual_researcher",
    "anonymous_review",
}

REQUIRED_INTERVENTIONS = {
    "feature_steering",
    "activation_cap",
    "reft_finetuning",
    "none",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def urn(kind: str, slug: str) -> str:
    return f"urn:srcos:interpretability:{kind}:{slug}"


def expand_source_lock(entry: dict[str, Any]) -> dict[str, Any]:
    slug = entry["slug"]
    source: dict[str, Any] = {
        "schema_version": "0.1.0",
        "lock_kind": "interpretability-artifact-source-lock",
        "lock_id": urn("source-lock", slug),
        "model_ref": entry["base_model"],
        "artifact_ref": f"artifact:{slug}",
        "decomposition_type": entry["decomposition_type"],
        "sae_training_method": entry["sae_training_method"],
        "site_type": entry["site_type"],
        "base_model_class": entry["base_model_class"],
        "embedded_decomposition": entry["embedded_decomposition"],
        "cross_layer": entry["cross_layer"],
        "neuronpedia_source_id": entry["neuronpedia_source_id"],
        "manifest_digest_sha256": digest(slug + entry["neuronpedia_source_id"]),
    }
    for key in ["nested_widths", "temporal_window", "compound_decompositions"]:
        if key in entry:
            source[key] = entry[key]
    if source["decomposition_type"] != "weight_sparse_native":
        source["decoder_ref"] = urn("decoder", slug)
    return source


def expand_provider_binding(entry: dict[str, Any]) -> dict[str, Any]:
    slug = entry["slug"]
    return {
        "schema_version": "0.1.0",
        "binding_kind": "interpretability-provider-binding",
        "binding_id": urn("provider-binding", slug),
        "source_lock_ref": urn("source-lock", slug),
        "provider_name": entry["slug"].split("-")[0],
        "release_name": entry["slug"],
        "author_class": entry["author_class"],
        "publication_state": entry["publication_state"],
        "claim_type": entry["claim_type"],
        "inference_endpoint_available": entry["inference_endpoint_available"],
        "commercial_license_required": entry["commercial_license_required"],
        "api_provider_class": entry["api_provider_class"],
        "deanonymization_pending": entry["deanonymization_pending"],
        "artifact_access_mode": "commercial_api" if entry["commercial_license_required"] else "hosted_feature_browser",
        "authority_chain_ref": f"urn:srcos:authority:interpretability:{slug}",
    }


def expand_intervention_spec(entry: dict[str, Any]) -> dict[str, Any]:
    slug = entry["slug"]
    kind = entry["intervention_kind"]
    spec: dict[str, Any] = {
        "schema_version": "0.1.0",
        "intervention_id": urn("intervention", slug),
        "source_lock_ref": urn("source-lock", slug),
        "intervention_kind": kind,
        "site_type": "not_applicable" if kind == "none" else entry["site_type"],
    }
    if kind == "feature_steering":
        spec.update(
            {
                "feature_ref": f"feature:{slug}:primary",
                "direction_ref": f"direction:{slug}:primary",
                "steering_strength": 1.0,
                "expected_behavior_delta": "target behavior changes under feature-direction intervention",
            }
        )
    elif kind == "activation_cap":
        spec.update(
            {
                "cap_value": 0.0,
                "cap_direction_ref": f"direction:{slug}:activation-axis",
                "cap_layer": 0,
                "cap_site_type": entry["site_type"],
                "expected_behavior_delta": "activation magnitude is bounded along the declared direction",
            }
        )
    elif kind == "reft_finetuning":
        spec.update(
            {
                "reft_method_class": "ReFT-R1",
                "finetuning_data_ref": "urn:srcos:dataset:axbench-reft-r1",
                "training_steps": 100,
                "expected_behavior_delta": "benchmark comparison against ReFT baseline is available",
            }
        )
    return spec


def validate_schema(instance: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda err: list(err.path))
    if errors:
        messages = []
        for err in errors[:10]:
            loc = ".".join(str(part) for part in err.path) or "<root>"
            messages.append(f"{label} {loc}: {err.message}")
        raise AssertionError("\n".join(messages))


def semantic_checks(entries: list[dict[str, Any]]) -> None:
    if len(entries) != 21:
        raise AssertionError(f"Expected 21 catalog entries, got {len(entries)}")

    slugs = [entry["slug"] for entry in entries]
    if len(slugs) != len(set(slugs)):
        raise AssertionError("Catalog slugs must be unique")

    decomposition_types = {entry["decomposition_type"] for entry in entries}
    missing_decomp = REQUIRED_DECOMPOSITION_TYPES - decomposition_types
    # LORSA appears as a required component of the compound CRM entry rather than
    # as a standalone row in this compact fixture.
    has_lorsa_component = any("lorsa_attention" in entry.get("compound_decompositions", []) for entry in entries)
    if missing_decomp != {"lorsa_attention"} or not has_lorsa_component:
        if missing_decomp:
            raise AssertionError(f"Missing decomposition coverage: {sorted(missing_decomp)}")

    author_classes = {entry["author_class"] for entry in entries}
    missing_authors = REQUIRED_AUTHOR_CLASSES - author_classes
    if missing_authors:
        raise AssertionError(f"Missing author class coverage: {sorted(missing_authors)}")

    intervention_kinds = {entry["intervention_kind"] for entry in entries}
    missing_interventions = REQUIRED_INTERVENTIONS - intervention_kinds
    if missing_interventions:
        raise AssertionError(f"Missing intervention coverage: {sorted(missing_interventions)}")

    for entry in entries:
        if entry["decomposition_type"] == "weight_sparse_native" and not entry["embedded_decomposition"]:
            raise AssertionError("weight_sparse_native requires embedded_decomposition=true")
        if entry["decomposition_type"] == "matryoshka_sae" and not entry.get("nested_widths"):
            raise AssertionError("matryoshka_sae requires nested_widths")
        if entry["decomposition_type"] == "temporal_sae" and not entry.get("temporal_window"):
            raise AssertionError("temporal_sae requires temporal_window")
        if entry["publication_state"] == "anonymous_review" and not entry["deanonymization_pending"]:
            raise AssertionError("anonymous_review publication requires deanonymization_pending=true")
        if entry["commercial_license_required"] and entry["api_provider_class"] not in {"commercial_steering_api", "hosted_api_features", "hosted_api_inference"}:
            raise AssertionError("commercial license requires commercial or hosted provider class")
        if entry["intervention_kind"] == "activation_cap" and entry["site_type"] == "not_applicable":
            raise AssertionError("activation_cap requires an applicable site")


def main() -> None:
    catalog = load_json(CATALOG)
    source_schema = load_json(SOURCE_SCHEMA)
    provider_schema = load_json(PROVIDER_SCHEMA)
    intervention_schema = load_json(INTERVENTION_SCHEMA)

    entries = catalog.get("entries", [])
    semantic_checks(entries)

    for entry in entries:
        source = expand_source_lock(entry)
        provider = expand_provider_binding(entry)
        intervention = expand_intervention_spec(entry)

        validate_schema(source, source_schema, f"source_lock:{entry['slug']}")
        validate_schema(provider, provider_schema, f"provider_binding:{entry['slug']}")
        validate_schema(intervention, intervention_schema, f"intervention_spec:{entry['slug']}")

    print("OK: interpretability SAE contract examples")


if __name__ == "__main__":
    main()
