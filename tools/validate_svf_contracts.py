#!/usr/bin/env python3
"""Validate SourceOS SVF contract declarations.

This validator checks repo-local SVF contract shape and safety posture. It
does not execute declared actions and does not issue receipts.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "svf" / "sourceos-contract-validation-basic.json"
MAKEFILE_PATH = ROOT / "Makefile"

EXPECTED_POLICY_ID = "svf:policy:sourceos.contract-readonly"
EXPECTED_PLAN_ID = "svf:plan:sourceos.contract-validation-basic"
EXPECTED_PROFILE_REF = "svf:profile:sourceos.contracts"
ALLOWED_CLAIMS = {"schema_conformant", "fixtures_validated", "policy_boundary_preserved", "non_production_only"}
REQUIRED_ACTIONS = {
    "svf:action:sourceos.control-plane-examples",
    "svf:action:sourceos.nlboot-examples",
    "svf:action:sourceos.lattice-data-governai-examples",
    "svf:action:sourceos.ops-history-examples",
    "svf:action:sourceos.runtime-observability-examples",
    "svf:action:sourceos.lifecycle-boundary-examples",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def make_targets() -> set[str]:
    text = MAKEFILE_PATH.read_text(encoding="utf-8")
    targets: set[str] = set()
    for line in text.splitlines():
        if not line or line.startswith("\t") or line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_.:-]+)\s*:", line)
        if match:
            targets.add(match.group(1))
    return targets


def result(check_id: str, passed: bool, diagnostics: list[str] | None = None) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "diagnostics": diagnostics or []}


def missing(actual: list[str], expected: set[str]) -> list[str]:
    actual_set = set(actual)
    return sorted(item for item in expected if item not in actual_set)


def validate() -> dict[str, Any]:
    contract = read_json(CONTRACT_PATH)
    targets = make_targets()
    results: list[dict[str, Any]] = []

    results.append(result("contract-id", contract.get("contract_id") == "svf:contract:sourceos.contract-validation-basic", [str(contract.get("contract_id"))]))
    results.append(result("profile-ref", contract.get("upstream_authority", {}).get("profile_ref") == EXPECTED_PROFILE_REF, [str(contract.get("upstream_authority", {}).get("profile_ref"))]))

    policy = contract.get("capability_policy", {})
    results.append(result("policy-id", policy.get("policy_id") == EXPECTED_POLICY_ID, [str(policy.get("policy_id"))]))
    results.append(result("policy-production-disallowed", policy.get("production_environment_allowed") is False))
    results.append(result("policy-network-none", policy.get("network_modes") == ["network_none"], [str(policy.get("network_modes"))]))
    results.append(result("policy-credential-none", policy.get("credential_modes") == ["credential_none"], [str(policy.get("credential_modes"))]))
    results.append(result("policy-non-claims-present", isinstance(policy.get("non_claims"), list) and len(policy.get("non_claims", [])) >= 3))

    actions = contract.get("actions", [])
    action_ids = [action.get("action_id") for action in actions]
    results.append(result("required-actions-present", not missing(action_ids, REQUIRED_ACTIONS), missing(action_ids, REQUIRED_ACTIONS)))
    results.append(result("action-ids-unique", len(action_ids) == len(set(action_ids))))

    for action in actions:
        action_id = action.get("action_id", "unknown")
        prefix = f"action:{action_id}"
        binding = action.get("binding", {})
        capability = action.get("capability", {})
        claims = action.get("claim_scopes", [])
        bad_claims = [claim for claim in claims if claim not in ALLOWED_CLAIMS]

        results.append(result(f"{prefix}:binding-kind-make-target", binding.get("kind") == "make_target", [str(binding.get("kind"))]))
        results.append(result(f"{prefix}:target-exists", isinstance(binding.get("entrypoint"), str) and binding.get("entrypoint") in targets, [str(binding.get("entrypoint"))]))
        results.append(result(f"{prefix}:network-none", capability.get("network_mode") == "network_none", [str(capability.get("network_mode"))]))
        results.append(result(f"{prefix}:credential-none", capability.get("credential_mode") == "credential_none", [str(capability.get("credential_mode"))]))
        results.append(result(f"{prefix}:backend-local", capability.get("backend") == "local", [str(capability.get("backend"))]))
        results.append(result(f"{prefix}:claims-allowed", not bad_claims, bad_claims))
        results.append(result(f"{prefix}:non-claims-present", isinstance(action.get("non_claims"), list) and len(action.get("non_claims", [])) >= 1))

    plan = contract.get("plan", {})
    plan_actions = plan.get("actions", [])
    plan_refs = [step.get("action_ref") for step in plan_actions]
    missing_refs = [action_ref for action_ref in plan_refs if action_ref not in action_ids]
    missing_required_refs = missing(plan_refs, REQUIRED_ACTIONS)
    bad_plan_claims = [claim for claim in plan.get("claim_scopes", []) if claim not in ALLOWED_CLAIMS]

    results.append(result("plan-id", plan.get("plan_id") == EXPECTED_PLAN_ID, [str(plan.get("plan_id"))]))
    results.append(result("plan-mode-advisory", plan.get("mode") == "advisory", [str(plan.get("mode"))]))
    results.append(result("plan-policy-ref", plan.get("policy_ref") == EXPECTED_POLICY_ID, [str(plan.get("policy_ref"))]))
    results.append(result("plan-action-refs-resolve", not missing_refs, [str(item) for item in missing_refs]))
    results.append(result("plan-includes-required-actions", not missing_required_refs, missing_required_refs))
    results.append(result("plan-claims-allowed", not bad_plan_claims, bad_plan_claims))
    results.append(result("plan-non-claims-present", isinstance(plan.get("non_claims"), list) and len(plan.get("non_claims", [])) >= 3))

    passed = all(item["passed"] for item in results)
    return {
        "validator": "sourceos.svf-contracts.validator.v1",
        "passed": passed,
        "action_count": len(actions),
        "result_count": len(results),
        "results": results,
    }


def main() -> int:
    validation = validate()
    print(json.dumps(validation, indent=2, sort_keys=True))
    if not validation["passed"]:
        print("FAIL: SourceOS SVF contracts", file=sys.stderr)
        return 1
    print("PASS: SourceOS SVF contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
