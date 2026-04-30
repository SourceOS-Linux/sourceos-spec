.PHONY: validate validate-control-plane-examples validate-nlboot-examples

validate: validate-control-plane-examples validate-nlboot-examples
	@echo "OK: validate"

validate-control-plane-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_control_plane_examples.py

validate-nlboot-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_nlboot_examples.py
