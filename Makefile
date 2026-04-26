.PHONY: validate validate-control-plane-examples

validate: validate-control-plane-examples
	@echo "OK: validate"

validate-control-plane-examples:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/validate_control_plane_examples.py
