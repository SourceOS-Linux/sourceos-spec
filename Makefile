.PHONY: validate validate-resource-contract validate-measurement validate-value-type validate-source-locator validate-sourceos-repo-manifest validate-mesh-action-registry validate-control-plane-examples validate-nlboot-examples validate-lattice-data-governai-examples validate-ops-history-examples validate-runtime-observability-examples validate-interpretability-examples validate-lifecycle-boundary-examples validate-svf-contracts validate-sync-cycle-receipts validate-onboarding-examples validate-runtime-causality-examples validate-agentic-os-examples validate-triparty-examples validate-labor-market-examples validate-supply-chain-risk-examples validate-reasoning-examples validate-mpcc-event-examples validate-knowledge-nugget-examples validate-semantic-action-examples validate-epistemic-kernel-examples validate-ab-update-examples validate-device-service-examples validate-duplicate-schema-ids validate-lawful-dispatch-receipt validate-architectural-building-block validate-agent-passport-examples validate-seam-definition-examples validate-agent-system-vocabulary validate-genesis-inception-examples validate-measurement validate-world-model-examples validate-eval-item-examples validate-ingestion-pipeline-examples validate-data-acquisition-examples validate-glossary-alignment-examples

validate: validate-glossary-alignment-examples validate-data-acquisition-examples validate-ingestion-pipeline-examples validate-control-plane-examples validate-nlboot-examples validate-lattice-data-governai-examples validate-ops-history-examples validate-runtime-observability-examples validate-interpretability-examples validate-lifecycle-boundary-examples validate-svf-contracts validate-sync-cycle-receipts validate-onboarding-examples validate-runtime-causality-examples validate-agentic-os-examples validate-triparty-examples validate-labor-market-examples validate-supply-chain-risk-examples validate-reasoning-examples validate-mpcc-event-examples validate-knowledge-nugget-examples validate-semantic-action-examples validate-epistemic-kernel-examples validate-ab-update-examples validate-device-service-examples validate-duplicate-schema-ids validate-value-type validate-source-locator validate-sourceos-repo-manifest validate-mesh-action-registry validate-lawful-dispatch-receipt validate-architectural-building-block validate-agent-passport-examples validate-seam-definition-examples validate-agent-system-vocabulary validate-genesis-inception-examples validate-measurement validate-world-model-examples validate-eval-item-examples validate-resource-contract
	@echo "OK: validate"

validate-ingestion-pipeline-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_ingestion_pipeline_examples.py

validate-glossary-alignment-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_glossary_alignment_examples.py

validate-data-acquisition-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_data_acquisition_examples.py

validate-genesis-inception-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_genesis_inception_examples.py

validate-world-model-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_world_model_examples.py

validate-eval-item-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_eval_item_examples.py

validate-agent-system-vocabulary:
	python3 tools/validate_agent_system_vocabulary.py

validate-agent-passport-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_agent_passport_examples.py

validate-seam-definition-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_seam_definition_examples.py

validate-source-locator:
	python3 tools/validate_source_locator.py

validate-sourceos-repo-manifest:
	python3 tools/validate_sourceos_repo_manifest.py

validate-mesh-action-registry:
	python3 tools/validate_mesh_action_registry.py

# Truth = Law × Evidence, enforced by the contract rather than by each app's goodwill.
validate-lawful-dispatch-receipt:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_lawful_dispatch_receipt.py

# Reusable role-named technical components. Zurich E-RDA2 uses the same abstraction —
# an ABB names a FUNCTION (DATABASE, IMPLEMENTATION CONTROLLER) that any vendor can fill.
validate-resource-contract:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_resource_contract.py

validate-measurement:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_measurement.py

validate-architectural-building-block:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_architectural_building_block.py

validate-ab-update-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_ab_update_examples.py

# The duplicate-$$id guardrail already runs in CI (.github/workflows/validate.yml)
# but was not reachable from `make validate`, so a local run could not reproduce
# the check that gates the PR. Wiring it in costs nothing and removes a way for
# local and CI verdicts to disagree.
validate-device-service-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_device_service_examples.py

validate-duplicate-schema-ids:
	python3 scripts/check_duplicate_schema_ids.py

validate-knowledge-nugget-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_knowledge_nugget_examples.py

validate-semantic-action-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_semantic_action_examples.py

validate-epistemic-kernel-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_epistemic_kernel_examples.py

validate-mpcc-event-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_mpcc_event_examples.py

validate-reasoning-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_reasoning_examples.py

validate-agentic-os-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_agentic_os_examples.py

validate-triparty-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_triparty_examples.py

validate-labor-market-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_labor_market_examples.py

validate-supply-chain-risk-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_supply_chain_risk_examples.py

validate-control-plane-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_control_plane_examples.py

validate-nlboot-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_nlboot_examples.py

validate-lattice-data-governai-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_lattice_data_governai_examples.py

validate-ops-history-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_ops_history_examples.py

validate-runtime-causality-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_runtime_causality_examples.py
validate-onboarding-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_onboarding_examples.py
validate-runtime-observability-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_runtime_observability_examples.py

validate-interpretability-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_interpretability_examples.py

validate-lifecycle-boundary-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_lifecycle_boundary_examples.py

validate-svf-contracts:
	python3 tools/validate_svf_contracts.py

validate-sync-cycle-receipts:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_sync_cycle_receipts.py

validate-value-type:
	python3 tools/validate_value_type.py
