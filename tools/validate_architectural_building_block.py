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
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "ArchitecturalBuildingBlock.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "architectural-building-block.example.json"

# Vendor names that must never appear as a role, and case-variant spellings of a legitimate
# role. Both are asserted by feeding them to the SCHEMA as real documents — see INVARIANT 1.
#
# There used to be a `_VENDOR_ROLES_FORBIDDEN` regex here and a loop that matched it against
# six hardcoded strings. The loop built a document (`e = deepcopy(example); e["role"] = v`)
# and then never used it, so the regex was only ever tested against its own fixtures. With
# `role: "postgres"` in the shipped example this file exited 0 AND printed
# "OK 6 vendor-named roles caught by the deny list". A control that reports catching what it
# has not looked at is worse than an absent one: it produces evidence.
#
# The deny list is gone. `role` is now a closed enum in the schema, so rejection happens in
# the artefact every consumer already validates against, not in a private regex here.
_VENDOR_ROLES = ["postgres", "PostgreSQL", "mysql", "AWS", "MSTR", "kubernetes", "DB2", "ADLS"]

# The compounding failure a deny list cannot catch. macOS ships `extension` (45×), `Extension`
# (2×), `DiagnosticExtension` (8×), `diagnosticextension` (5×) and `diagnostic` (3×) across its
# 627 sandbox containers — a freeform role field after fifteen years without a grammar.
_CASE_VARIANTS = ["database", "Database", "DataBase", "DATABASE ", " DATABASE", "data solution platform"]


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

    # INVARIANT 1 — role is a CLOSED enum, and rejection happens in the schema, applied to a
    # real document. Every case below mutates the shipped example and asks the schema.
    print("  INVARIANT 1 — role names FUNCTIONS from a closed set, not vendors or variants")
    before = len(failures)
    for v in _VENDOR_ROLES:
        case(f"vendor name as role ({v!r})", broken(lambda b, v=v: b.__setitem__("role", v)), False)
    for v in _CASE_VARIANTS:
        case(f"case/whitespace variant as role ({v!r})", broken(lambda b, v=v: b.__setitem__("role", v)), False)
    case("unlisted role invented at the call site",
         broken(lambda b: b.__setitem__("role", "VECTOR INDEX")), False)
    ok = len(failures) == before
    print(f"    {'OK  ' if ok else 'FAIL'} {len(_VENDOR_ROLES)} vendor names, "
          f"{len(_CASE_VARIANTS)} case/whitespace variants and 1 unlisted role rejected "
          "BY THE SCHEMA, as documents")

    # The mutation test. Without it, the cases above pass whenever the schema rejects for ANY
    # reason, and would keep passing if `role` were reverted to a freeform string while some
    # unrelated constraint did the rejecting. Drop the enum, confirm 'postgres' is accepted.
    print("  INVARIANT 1a — the enum is what does the work (mutation test)")
    checks += 1
    loose = copy.deepcopy(schema)
    loose["properties"]["role"] = {"type": "string", "minLength": 1}
    loose_validator = Draft202012Validator(loose)
    vendor_doc = copy.deepcopy(example)
    vendor_doc["role"] = "postgres"
    if list(loose_validator.iter_errors(vendor_doc)):
        failures.append(
            "mutation test inconclusive: with the role enum removed, role='postgres' was STILL "
            "rejected — so the enum is not the constraint doing the work and INVARIANT 1 above "
            "proves nothing about it"
        )
        print("    FAIL enum removed but document still rejected — INVARIANT 1 proves nothing")
    else:
        print("    OK   enum removed ⇒ role='postgres' accepted; restored ⇒ rejected. "
              "The enum is load-bearing.")

    # INVARIANT 2 — the shipped example demonstrates the required shape.
    print("  INVARIANT 2 — reads and writes explicit (may be empty)")
    before = len(failures)
    checks += 1
    if not isinstance(example.get("protocol", {}).get("reads"), list):
        failures.append("example must declare protocol.reads explicitly")
    if not isinstance(example.get("protocol", {}).get("writes"), list):
        failures.append("example must declare protocol.writes explicitly")
    print(f"    {'OK  ' if len(failures) == before else 'FAIL'} example declares both, and shape "
          "reject case above covers the missing-field failure")

    # INVARIANT 3 — a conformanceTest pointer must RESOLVE. `format: uri-reference` is a syntax
    # check that resolves nothing; this field shipped pointing at a file that did not exist and
    # validated clean. Absence is documented as meaningful; a dangling pointer is not — it reads
    # as "held to shared vectors" to every consumer that does not go looking.
    print("  INVARIANT 3 — conformanceTest resolves, or is absent on purpose")
    checks += 1
    ptr = example.get("conformanceTest")
    if ptr is None:
        print("    OK   example declares no conformanceTest — absence is meaningful per schema "
              "(conformance is per-implementation until shared vectors exist)")
    elif (REPO_ROOT / ptr).is_file():
        print(f"    OK   {ptr} resolves")
    else:
        failures.append(
            f"conformanceTest {ptr!r} does not resolve to a file under {REPO_ROOT}. A pointer to "
            "a suite that is not there is worse than absence — drop the field or add the suite."
        )

    # Negative control on INVARIANT 3. A resolve check never observed refusing is
    # indistinguishable from no resolve check.
    checks += 1
    probe = copy.deepcopy(example)
    probe["conformanceTest"] = "conformance/does-not-exist-negative-control.json"
    if (REPO_ROOT / probe["conformanceTest"]).exists():
        failures.append("negative control is not negative: the probe path exists on disk")
    elif not (REPO_ROOT / probe["conformanceTest"]).is_file():
        print("    OK   negative control: a dangling pointer IS detected as unresolvable")

    if failures:
        print(f"\n{len(failures)} failure(s) of {checks} checks:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print(f"\nOK ArchitecturalBuildingBlock: {checks} checks. "
          "abbId must be ABB.NN; role comes from a CLOSED enum so vendor names and case "
          "variants are rejected by the schema on real documents (mutation-tested); "
          "protocol reads and writes must be explicit; conformanceTest must resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
