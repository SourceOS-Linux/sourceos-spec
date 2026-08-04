#!/usr/bin/env python3
"""Prove every semantic gate in validate_fingerprint_stack.py BITES.

A validator that passes tells you nothing until you have watched it fail. This mutates the
conformant examples one invariant at a time and requires the validator to reject each
mutation with the expected message. A gate that stays green under its own mutation is a gate
with no teeth, and is reported as a failure of the CHECKER, not of the data.

This exists because the closest precedent in this repo shipped exactly that defect: the
trained DataClass classifiers (#264) declared a monotonicity constraint whose fixture held
the monotone feature constant, so the constraint bound nothing and the test passed vacuously
(#265). Schema negative vectors live in fixtures/fingerprint-stack/conformance.json; this
file covers the SEMANTIC checks, which no schema can express.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
FIXTURES = ROOT / "fixtures" / "fingerprint-stack"

FP_A = "column_fingerprint.customer_id.json"
FP_B = "column_fingerprint.repurposed_status.json"
DRIFT = "column_drift.repurposed_status.json"
REPORT = "estate_admissibility_report.phase0.json"
GRAPH = "ontodt_graph.json"
POLICY = "classification_enforcement_policy.json"


def layer(doc: dict, name: str) -> dict:
    return next(le for le in doc["layerEvidence"] if le["layer"].startswith(name))


# Each mutation: (label, target file, mutate fn, substring the rejection must contain).
MUTATIONS: list[tuple[str, str, object, str]] = [
    ("quantizer cache drifts from evidence", FP_A,
     lambda d: d["stance"].update(value="NEG"), "cannot outrun its evidence"),
    ("asymmetric thresholds unattested", FP_A,
     lambda d: d["stance"]["thresholds"].update(tauNeg=0.5), "negation-equivariance"),
    ("glut without a recorded origin", FP_B,
     lambda d: d["stance"].update(inadmissibleOrigin=None), "without an origin"),
    ("pooled evidence overstated", FP_A,
     lambda d: d["pooling"]["pooled"].update(alpha=0.95), "!= recomputed"),
    ("inadmissible layer still contributes", FP_B,
     lambda d: layer(d, "L5")["evidence"].update(alpha=0.9), "must contribute ZERO"),
    ("guard raises evidence instead of lowering", FP_A,
     lambda d: d["stance"]["evidence"].update(alpha=0.99), "may only lower stance"),
    ("probabilistic sum without a certificate", FP_A,
     lambda d: d["pooling"].update(operator="probabilistic-sum"), "independence certificate"),
    ("POS below the effective-independence floor", FP_A,
     lambda d: d["quorum"].update(nEffFloor=6.0), "below floor"),
    ("n_eff asserted, not derived", FP_A,
     lambda d: d["quorum"].update(nEff=5.9), "participation ratio"),
    ("unearned coverage across composition", FP_B,
     lambda d: d["stance"]["composition"].update(effectiveEpsilon=0.1), "coverage does not compose"),
    ("inferred signal speaking as loudly as declared", FP_B,
     lambda d: layer(d, "L6")["evidence"].update(alpha=0.9), "above the cap"),
    ("L4 conflict recorded as a weak match", FP_A,
     lambda d: layer(d, "L4")["witness"].update(conflictSet=["mean"]), "is not a glut"),
    ("profiling self-promoted to a hard axiom", FP_A,
     lambda d: layer(d, "L2")["witness"].update(promotedToHardAxiom=True), "without steward attestation"),
    ("drift flag set independently of the measurement", DRIFT,
     lambda d: d.update(distance=0.01), "recomputes to"),
    ("silent repurpose misread as a redesign", DRIFT,
     lambda d: d.update(schemaChanged=True), "measurement gives"),
    ("glut never reaches a human", DRIFT,
     lambda d: d.update(stewardQueueRef=None), "behaviour, not a claim"),
    ("L5 survives its own drift flag", FP_B,
     lambda d: layer(d, "L5")["admissibility"].update(admissible=True, reason=None),
     "must be inadmissible"),
    ("estate claims POS below the floor", REPORT,
     lambda d: d["quorum"].update(posAvailable=True), "honest outputs are ZERO and NEG only"),
    ("glossary admissible before a glossary exists", REPORT,
     lambda d: d["layers"][2].update(admissible=True, reason=None), "catalog-derived bootstrap"),
    ("parthood and subtyping share an arrow", GRAPH,
     lambda d: d["subtypeOf"].append(["email-address", "client-record"]), "X1 violated"),
    ("open-world count reported as a number", GRAPH,
     lambda d: d["aggregateQueries"][0].update(answerInterval=[41, 41]), "is an interval, not a number"),
    ("contradictions folded into the count", GRAPH,
     lambda d: d["aggregateQueries"][0].update(inadmissibleReported=0), "reported separately"),
    ("attribute enumeration walks subtyping", GRAPH,
     lambda d: d["partEnumerations"][0].update(relation="subtypeOf"), "enumeration of PARTS"),
    ("unknown data served without anyone deciding", POLICY,
     lambda d: d["resourceClasses"][0].update(attestationRef=None), "or an accident"),
    ("fail-open bought back by attestation on restricted data", POLICY,
     lambda d: d["resourceClasses"][2].update(
         zeroBehavior="fail-open", attestationRef="urn:srcos:attestation:override"),
     "no attestation buys that back"),
]


def run_validator(workdir: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(workdir / "tools" / "validate_fingerprint_stack.py")],
        capture_output=True, text=True, cwd=workdir,
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    originals = {
        n: json.loads((EXAMPLES / n).read_text()) for n in (FP_A, FP_B, DRIFT, REPORT, POLICY)
    } | {GRAPH: json.loads((FIXTURES / GRAPH).read_text())}

    failures: list[str] = []
    results: dict[str, bool] = {}

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "repo"
        # Mirror only what the validator reads; symlink the rest so mutation is isolated.
        for sub in ("schemas", "tools", "examples", "fixtures"):
            (work / sub).mkdir(parents=True, exist_ok=True)
        for src, dst in (
            (ROOT / "schemas", work / "schemas"),
            (ROOT / "tools", work / "tools"),
            (ROOT / "examples", work / "examples"),
        ):
            for f in src.glob("*.json"):
                (dst / f.name).write_bytes(f.read_bytes())
            for f in src.glob("*.py"):
                (dst / f.name).write_bytes(f.read_bytes())
        (work / "fixtures" / "fingerprint-stack").mkdir(parents=True, exist_ok=True)
        for f in FIXTURES.glob("*.json"):
            (work / "fixtures" / "fingerprint-stack" / f.name).write_bytes(f.read_bytes())

        # Sanity: the unmutated mirror must PASS, or every mutation "passes" for the wrong reason.
        rc, out = run_validator(work)
        if rc != 0:
            print("FAIL: unmutated mirror does not validate — mutation results would be meaningless",
                  file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        results["baseline-mirror-passes"] = True

        for label, target, mutate, expect in MUTATIONS:
            doc = copy.deepcopy(originals[target])
            mutate(doc)
            path = (work / "fixtures" / "fingerprint-stack" / target) if target == GRAPH \
                else (work / "examples" / target)
            path.write_text(json.dumps(doc, indent=2))
            rc, out = run_validator(work)
            path.write_text(json.dumps(originals[target], indent=2))

            if rc == 0:
                failures.append(f"NO TEETH: {label!r} was accepted — this gate does not bite")
                results[label] = False
            elif expect not in out:
                failures.append(f"WRONG REASON: {label!r} rejected, but not for {expect!r}")
                results[label] = False
            else:
                results[label] = True

    for m in failures:
        print(f"FAIL: {m}", file=sys.stderr)
    ok = not failures
    print(json.dumps({"ok": ok, "gatesProvenToBite": len(MUTATIONS), "results": results},
                     indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
