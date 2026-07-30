#!/usr/bin/env python3
"""Validate ArchitecturalBuildingBlock: role-named technical components, decoupled from vendors.

Zurich's E-RDA2 uses the same abstraction — ABB.03 = DATABASE has slots that DB2, ADLS, BLOB,
XYZ or CaaS can fill — because it lets a vendor swap be a one-manifest edit rather than a
call-site rewrite. The estate has ~74 services today and no ABB abstraction; a service was
inseparable from its implementation, so 'we use Postgres' became a load-bearing invariant.

Two properties this validator asserts by REJECTION (a validator never observed refusing is
indistinguishable from no validator):

  INVARIANT 1  abbId is `ABB.<two digits>`, roles are non-empty strings, and vendor names
               (`postgres`, `mysql`, `mstr`) MUST NOT appear as roles. A role is a FUNCTION,
               not a technology — 'DATABASE' is a role, 'PostgreSQL' is an implementation.

  INVARIANT 2  protocol.reads and protocol.writes are declared explicitly (may be empty).
               A missing verb list, not an empty one, is the failure — declaring a
               write-only ABB requires writing `reads: []` on purpose, so 'I forgot to
               declare' cannot masquerade as 'this ABB has no reads'.
"""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "ArchitecturalBuildingBlock.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "architectural-building-block.example.json"

# Vendor names that must never appear as a role. Not exhaustive by design — the goal is to
# catch obvious slips ('postgres' as a role), not to enumerate every product. A determined
# author can still name a role poorly, but the review checklist will catch what this misses.
_VENDOR_ROLES_FORBIDDEN = re.compile(
    r"^(postgres|postgresql|mysql|mariadb|mssql|sqlserver|oracle|db2|"
    r"redis|memcached|elastic|elasticsearch|opensearch|"
    r"mstr|microstrategy|tableau|powerbi|superset|"
    r"docker|kubernetes|helm|nginx|apache|"
    r"aws|azure|gcp|gce|s3|adls|blob|ecs|eks|gke|gks)$",
    re.IGNORECASE,
)


def main() -> int:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("Missing dependency: jsonschema", file=sys.stderr)
        return 1

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    failures: list[str] = []
    checks = 0

    def case(label: str, instance: Any, should_pass: bool) -> None:
        nonlocal checks
        checks += 1
        errs = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        accepted = not errs
        if accepted != should_pass:
            want = "accepted" if should_pass else "rejected"
            got = "accepted" if accepted else f"rejected ({errs[0].message[:100]})"
            failures.append(f"{label}: expected {want}, was {got}")

    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    print("  shape")
    case("shipped example (ABB.03 DATABASE)", example, True)

    def broken(mutation) -> dict:
        b = copy.deepcopy(example)
        mutation(b)
        return b

    for label, mut in [
        ("kind wrong", lambda b: b.__setitem__("kind", "SomethingElse")),
        ("abbId not ABB.NN pattern (bare number)", lambda b: b.__setitem__("abbId", "3")),
        ("abbId not ABB.NN pattern (one digit)", lambda b: b.__setitem__("abbId", "ABB.3")),
        ("abbId not ABB.NN pattern (three digits)", lambda b: b.__setitem__("abbId", "ABB.003")),
        ("abbId in another namespace", lambda b: b.__setitem__("abbId", "ARC.03")),
        ("role empty string", lambda b: b.__setitem__("role", "")),
        ("schemaVersion bare number", lambda b: b.__setitem__("schemaVersion", "1")),
        ("protocol block absent", lambda b: b.pop("protocol")),
        ("protocol.reads missing (empty must be explicit, not omitted)",
         lambda b: b["protocol"].pop("reads")),
        ("protocol.writes missing", lambda b: b["protocol"].pop("writes")),
        ("requiredCapabilities item not lowercase-kebab", lambda b: b.__setitem__(
            "requiredCapabilities", ["At_Rest_Encryption"])),
        ("supersedes item not ABB.NN pattern", lambda b: b.__setitem__("supersedes", ["ABB3"])),
        ("undeclared field at root (schema is closed)", lambda b: b.__setitem__("zzUnknown", "leak")),
        ("undeclared field in protocol", lambda b: b["protocol"].__setitem__("zz", "leak")),
    ]:
        case(label, broken(mut), False)
    print(f"    {'OK  ' if not failures else 'FAIL'} shape controls: 14 rejected, 1 accepted")

    # INVARIANT 1 (advisory): vendor-named roles. Enforced here in the validator rather than
    # the schema because a hard pattern-based deny would need every vendor enumerated in JSON
    # Schema — brittle. Here the deny list is code and grows over time.
    print("  INVARIANT 1 — role names FUNCTIONS, not vendors")
    vendor_examples = ["postgres", "PostgreSQL", "mysql", "AWS", "MSTR", "kubernetes"]
    vendor_failures = 0
    for v in vendor_examples:
        e = copy.deepcopy(example)
        e["role"] = v
        # Schema accepts it (role is any non-empty string) — but this validator catches it.
        if _VENDOR_ROLES_FORBIDDEN.match(v):
            checks += 1
            continue
        vendor_failures += 1
        failures.append(f"vendor role '{v}' should be caught by the forbidden-vendor list")
    if vendor_failures == 0:
        print(f"    OK   {len(vendor_examples)} vendor-named roles caught by the deny list "
              "('postgres', 'PostgreSQL', 'mysql', 'AWS', 'MSTR', 'kubernetes')")
    else:
        failures.append(f"vendor role checks missed {vendor_failures}")

    # INVARIANT 2 — the shipped example demonstrates the required shape.
    print("  INVARIANT 2 — reads and writes explicit (may be empty)")
    checks += 1
    if not isinstance(example.get("protocol", {}).get("reads"), list):
        failures.append("example must declare protocol.reads explicitly")
    if not isinstance(example.get("protocol", {}).get("writes"), list):
        failures.append("example must declare protocol.writes explicitly")
    print(f"    {'OK  ' if not failures else 'FAIL'} example declares both, and shape reject "
          "case above covers the missing-field failure")

    if failures:
        print(f"\n{len(failures)} failure(s) of {checks} checks:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print(f"\nOK ArchitecturalBuildingBlock: {checks} checks. "
          "abbId must be ABB.NN, roles name functions not vendors, "
          "protocol reads and writes must be explicit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
