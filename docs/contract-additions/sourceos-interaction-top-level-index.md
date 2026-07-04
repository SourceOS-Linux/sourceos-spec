# SourceOS Interaction Substrate Top-Level Index

Status: informational index

The SourceOS interaction substrate is the governed noetic/chat/task event path connecting browser chat, task-boundary coordination, execution evidence, and terminal rendering.

Start here:

- Canonical schema: `schemas/SourceOSInteractionEvent.json`
- Base example: `examples/sourceos-interaction-event.json`
- Generated TypeScript artifact: `generated/typescript/sourceos-interaction-event.ts`
- Generated Python artifact: `generated/python/sourceos_interaction_event.py`
- Substrate catalog: `docs/contract-additions/sourceos-interaction-catalog.md`
- Reference flow: `docs/contract-additions/sourceos-interaction-reference-flow.md`
- Noetica placement addendum: `docs/contract-additions/sourceos-interaction-noetica-placement-addendum.md`
- Reference manifest: `examples/interaction-flow/noetica-superconscious-agentplane-agentterm.flow.json`

Implemented downstream roles:

- `SocioProphet/Noetica`: browser chat / desktop surface and governance-trail emitter, with future runtime emission placed at the typed transport / local-service boundary.
- `SourceOS-Linux/agent-term`: terminal governance-trace renderer.
- `SocioProphet/superconscious`: task-boundary reference binding.
- `SocioProphet/agentplane`: evidence and replay reference binding.

Validation commands:

```bash
python tools/validate_sourceos_interaction_examples.py
python tools/generate_sourceos_interaction_types.py --check
python tools/validate_interaction_flow_reference.py
```

Authority split:

- `sourceos-spec` owns schema and generated contract artifacts.
- Surfaces own rendering and user interaction.
- Noetica transport/local-service boundary is the preferred future emission placement for live Noetica events.
- Superconscious owns task-boundary coordination.
- AgentPlane owns evidence and replay references.
- Policy, identity/grants, and memory remain separate authority planes.
