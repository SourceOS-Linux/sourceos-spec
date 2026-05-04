.PHONY: validate validate-control-plane-examples validate-nlboot-examples validate-lattice-data-governai-examples validate-ops-history-examples

validate: validate-control-plane-examples validate-nlboot-examples validate-lattice-data-governai-examples validate-ops-history-examples
	@echo "OK: validate"

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
