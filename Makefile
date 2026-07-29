.PHONY: validate validate-control-plane-examples validate-nlboot-examples validate-lattice-data-governai-examples validate-ops-history-examples validate-runtime-observability-examples validate-interpretability-examples validate-lifecycle-boundary-examples validate-svf-contracts validate-sync-cycle-receipts validate-onboarding-examples validate-runtime-causality-examples validate-agentic-os-examples validate-triparty-examples validate-labor-market-examples validate-supply-chain-risk-examples validate-reasoning-examples validate-mpcc-event-examples validate-epistemic-kernel-examples

validate: validate-control-plane-examples validate-nlboot-examples validate-lattice-data-governai-examples validate-ops-history-examples validate-runtime-observability-examples validate-interpretability-examples validate-lifecycle-boundary-examples validate-svf-contracts validate-sync-cycle-receipts validate-onboarding-examples validate-runtime-causality-examples validate-agentic-os-examples validate-triparty-examples validate-labor-market-examples validate-supply-chain-risk-examples validate-reasoning-examples validate-mpcc-event-examples validate-epistemic-kernel-examples
	@echo "OK: validate"

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
