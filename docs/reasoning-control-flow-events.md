# Reasoning Control-Flow Events

**Status:** additive extension to `ReasoningEvent` (v2). Backward-compatible: `eventType`
stays a free string and `controlFlow` is optional.

## Purpose

`ReasoningRun` records run lifecycle; it did not carry the *control-flow* of a run
(the sequence of tool calls, branches, and delegated sub-runs). Downstream
narration-fidelity verification (SP-TRACE-CFR) recovers orchestration structure from
this control flow to check that an agent's stated narration matches what it actually
did. This extension lets emitters (Noetica → Superconscious → AgentPlane → AgentTerm,
TurtleTerm, BearBrowser) produce that structure.

**Privacy posture (intentional):** control-flow events carry *operational structure
only* — a site id, a branch label, a guard position, a sub-run id — never raw model
reasoning. `traceLevel` and `trustLevel` continue to scope disclosure and provenance.
This is the "verify what the agent did, not what it thought" guarantee.

## Reserved control-flow eventTypes

| `eventType` | `controlFlow` fields | Recovered structure |
|---|---|---|
| `reasoning.tool.called` | `site` | a tool-call node |
| `reasoning.decision.branched` | `site`, `branchTaken`, `guardPosition?` | branch / loop guard (pre=WHILE, post=DO_WHILE) |
| `reasoning.subrun.spawned` | `site`, `sidechainId` | delegated sub-run entry (SESE) |
| `reasoning.subrun.joined` | `site`, `sidechainId` | delegated sub-run return |
| `reasoning.run.completed` | `site` | terminal |

`site` is a stable orchestration-site identity (the decision-fold key — not a payload
hash). Events are consumed in the run's causal order.

## Argument-level provenance

A `reasoning.tool.called` event MAY set `controlFlow.arg` to name the argument whose
provenance carries this event's `trustLevel`. Consumers map `trustLevel` onto an
integrity lattice for argument-level information-flow control (e.g. an argument derived
from `untrusted-observation` is denied at a trusted sink).

## Consumer

AgentPlane's `sp-run narration-gate` / `sp-run attest-run` project a stream of these
events into a control-flow segment, recover it with two engines, compare it against the
agent's narration claims, and emit a signed run attestation. See
`agentplane/tools/trace_cfr_reasoning_bridge.py`.
