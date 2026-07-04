# SourceOS Interaction Noetica Placement Addendum

Status: placement addendum  
Related downstream implementation: `SocioProphet/Noetica#45`

## Purpose

Noetica has advanced from a browser-only shell toward a Phase 1H desktop/local-service architecture. The SourceOS interaction substrate remains valid, but future Noetica runtime emission should attach at the typed transport and local-service boundary rather than directly inside the UI shell.

## Placement rule

Preferred future placement:

```text
Noetica AppShell
  -> typed client transport boundary
  -> local service boundary or browser/dev fallback route
  -> SourceOSInteractionEvent
  -> optional AgentTerm / Superconscious / AgentPlane references
```

This preserves the existing authority split:

- Noetica owns UI and desktop shell presentation.
- Noetica transport owns client dispatch and response-stream parsing.
- Noetica local service boundary owns durable local service/status semantics when implemented.
- `SourceOS-Linux/sourceos-spec` owns the interaction event schema and generated artifacts.
- AgentTerm, Superconscious, and AgentPlane retain their rendering, task-boundary, and evidence/replay roles.
- Policy Fabric, Agent Registry, and Memory Mesh remain separate authority planes.

## Transitional fallback

Browser/dev routes may continue to produce SourceOS-interaction-compatible metadata during Phase 1H. They should be treated as fallback compatibility surfaces, not the final authority boundary for the desktop product.

## Fixture relationship

Noetica now carries fixture-only examples for future transport/local-service-shaped interaction events:

- `tests/fixtures/sourceos-interaction/noetica-local-service-status.interaction.json`
- `tests/fixtures/sourceos-interaction/noetica-chat-completion-via-transport.interaction.json`

These fixtures are guidance for later runtime wiring. They do not claim that live event export is complete.

## Non-goals

- No live transport bridge is introduced by this addendum.
- No runtime authority is moved into Noetica.
- No policy, memory, identity, grant, execution evidence, or replay authority is changed.
- No private reasoning, raw transcripts, raw shell output, browser history, secrets, credentials, or raw execution logs are valid payloads.
