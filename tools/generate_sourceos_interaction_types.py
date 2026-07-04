#!/usr/bin/env python3
"""Generate SourceOSInteractionEvent TypeScript and Python type mirrors.

This is intentionally focused on the SourceOS interaction substrate instead of a
general-purpose JSON Schema compiler. The canonical source remains
schemas/SourceOSInteractionEvent.json. Downstream repos may vendor the generated
artifacts or run this script from a pinned sourceos-spec revision.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "SourceOSInteractionEvent.json"
TS_OUT = ROOT / "generated" / "typescript" / "sourceos-interaction-event.ts"
PY_OUT = ROOT / "generated" / "python" / "sourceos_interaction_event.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated artifacts are stale.")
    args = parser.parse_args()

    schema = load_schema()
    ts_content = generate_typescript(schema)
    py_content = generate_python(schema)

    outputs = {
        TS_OUT: ts_content,
        PY_OUT: py_content,
    }

    if args.check:
        stale = [path for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale generated artifact: {path.relative_to(ROOT)}")
            return 1
        return 0

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")

    return 0


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    if schema.get("title") != "SourceOSInteractionEvent":
        raise SystemExit("unexpected schema title; expected SourceOSInteractionEvent")
    return schema


def prop(schema: dict[str, Any], *path: str) -> dict[str, Any]:
    cursor: Any = schema
    for key in path:
        cursor = cursor[key]
    if not isinstance(cursor, dict):
        raise TypeError(f"schema path does not resolve to object: {'.'.join(path)}")
    return cursor


def enum_values(schema: dict[str, Any], *path: str) -> list[str]:
    values = prop(schema, *path).get("enum")
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise TypeError(f"schema path does not expose string enum: {'.'.join(path)}")
    return values


def ts_union(values: list[str]) -> str:
    return " | ".join(json.dumps(value) for value in values)


def py_literal(values: list[str]) -> str:
    return "Literal[" + ", ".join(repr(value) for value in values) + "]"


def generated_header(comment: str) -> str:
    return f"""{comment} Generated from schemas/SourceOSInteractionEvent.json.
{comment} Do not edit by hand. Run: python tools/generate_sourceos_interaction_types.py

"""


def generate_typescript(schema: dict[str, Any]) -> str:
    event_classes = ts_union(enum_values(schema, "properties", "eventClass"))
    surface_kinds = ts_union(enum_values(schema, "properties", "surface", "properties", "surfaceKind"))
    modes = ts_union(enum_values(schema, "properties", "mode"))
    actor_kinds = ts_union(enum_values(schema, "properties", "actor", "properties", "actorKind"))
    participant_roles = ts_union(enum_values(schema, "properties", "participants", "items", "properties", "role"))
    task_statuses = ts_union(enum_values(schema, "properties", "task", "properties", "status"))
    steering_kinds = ts_union(enum_values(schema, "properties", "steeringIntent", "properties", "steeringKind"))
    steering_statuses = ts_union(enum_values(schema, "properties", "steeringIntent", "properties", "status"))
    payload_modes = ts_union(enum_values(schema, "properties", "payloadMode"))
    required = ", ".join(schema["required"])

    return generated_header("//") + f"""export const SOURCEOS_INTERACTION_EVENT_REQUIRED = {json.dumps(schema["required"], indent=2)} as const

export type SourceOSInteractionEventClass = {event_classes}
export type SourceOSInteractionSurfaceKind = {surface_kinds}
export type SourceOSInteractionMode = {modes}
export type SourceOSInteractionActorKind = {actor_kinds}
export type SourceOSInteractionParticipantRole = {participant_roles}
export type SourceOSInteractionTaskStatus = {task_statuses}
export type SourceOSSteeringKind = {steering_kinds}
export type SourceOSSteeringStatus = {steering_statuses}
export type SourceOSInteractionPayloadMode = {payload_modes}

export interface SourceOSInteractionSurface {{
  surfaceKind: SourceOSInteractionSurfaceKind
  sourcePlane: string
  clientRef?: string | null
}}

export interface SourceOSInteractionSession {{
  sessionId: string
  conversationRef?: string | null
  roomRef?: string | null
  threadRef?: string | null
  workroomRef?: string | null
  topicRef?: string | null
  opsHistoryEventRef?: string | null
}}

export interface SourceOSInteractionActor {{
  actorRef: string
  actorKind: SourceOSInteractionActorKind
  agentRegistryRef?: string | null
  onBehalfOfRef?: string | null
}}

export interface SourceOSInteractionParticipant {{
  role: SourceOSInteractionParticipantRole
  participantRef: string
  agentRegistryRef?: string | null
}}

export interface SourceOSInteractionTask {{
  taskRef?: string | null
  status?: SourceOSInteractionTaskStatus
  modelHint?: string | null
  modelRouted?: string | null
  provider?: string | null
  latencyMs?: number | null
}}

export interface SourceOSSteeringIntent {{
  steeringKind?: SourceOSSteeringKind
  featureRef?: string | null
  strength?: number | null
  status?: SourceOSSteeringStatus
}}

export interface SourceOSGovernanceTrace {{
  policyAdmitted: boolean
  policyRef?: string | null
  policyDecisionRefs?: string[]
  grantRefs?: string[]
  memoryScopeRef?: string | null
  memoryWritten: boolean
  contextPackRefs?: string[]
  requestHash?: string | null
  evidenceHash?: string | null
  providerRouteEvidenceRef?: string | null
  agentPlaneRunRef?: string | null
  evidenceRefs?: string[]
  replayRef?: string | null
}}

export interface SourceOSInteractionIntegrity {{
  eventHash?: string | null
  signature?: string | null
}}

export interface SourceOSInteractionEvent {{
  interactionEventId: string
  type: "SourceOSInteractionEvent"
  specVersion: string
  eventClass: SourceOSInteractionEventClass
  occurredAt: string
  surface: SourceOSInteractionSurface
  mode: SourceOSInteractionMode
  session: SourceOSInteractionSession
  actor: SourceOSInteractionActor
  participants?: SourceOSInteractionParticipant[]
  task?: SourceOSInteractionTask | null
  steeringIntent?: SourceOSSteeringIntent | null
  governanceTrace: SourceOSGovernanceTrace
  payloadMode: SourceOSInteractionPayloadMode
  payload?: Record<string, unknown> | null
  sourceEventRefs?: string[]
  redactionRefs?: string[]
  integrity?: SourceOSInteractionIntegrity | null
}}

// Required top-level fields in the canonical schema: {required}
"""


def generate_python(schema: dict[str, Any]) -> str:
    event_classes = py_literal(enum_values(schema, "properties", "eventClass"))
    surface_kinds = py_literal(enum_values(schema, "properties", "surface", "properties", "surfaceKind"))
    modes = py_literal(enum_values(schema, "properties", "mode"))
    actor_kinds = py_literal(enum_values(schema, "properties", "actor", "properties", "actorKind"))
    participant_roles = py_literal(enum_values(schema, "properties", "participants", "items", "properties", "role"))
    task_statuses = py_literal(enum_values(schema, "properties", "task", "properties", "status"))
    steering_kinds = py_literal(enum_values(schema, "properties", "steeringIntent", "properties", "steeringKind"))
    steering_statuses = py_literal(enum_values(schema, "properties", "steeringIntent", "properties", "status"))
    payload_modes = py_literal(enum_values(schema, "properties", "payloadMode"))

    return generated_header("#") + f"""from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict


SOURCEOS_INTERACTION_EVENT_REQUIRED = {schema["required"]!r}

SourceOSInteractionEventClass = {event_classes}
SourceOSInteractionSurfaceKind = {surface_kinds}
SourceOSInteractionMode = {modes}
SourceOSInteractionActorKind = {actor_kinds}
SourceOSInteractionParticipantRole = {participant_roles}
SourceOSInteractionTaskStatus = {task_statuses}
SourceOSSteeringKind = {steering_kinds}
SourceOSSteeringStatus = {steering_statuses}
SourceOSInteractionPayloadMode = {payload_modes}


class SourceOSInteractionSurface(TypedDict):
    surfaceKind: SourceOSInteractionSurfaceKind
    sourcePlane: str
    clientRef: NotRequired[str | None]


class SourceOSInteractionSession(TypedDict):
    sessionId: str
    conversationRef: NotRequired[str | None]
    roomRef: NotRequired[str | None]
    threadRef: NotRequired[str | None]
    workroomRef: NotRequired[str | None]
    topicRef: NotRequired[str | None]
    opsHistoryEventRef: NotRequired[str | None]


class SourceOSInteractionActor(TypedDict):
    actorRef: str
    actorKind: SourceOSInteractionActorKind
    agentRegistryRef: NotRequired[str | None]
    onBehalfOfRef: NotRequired[str | None]


class SourceOSInteractionParticipant(TypedDict):
    role: SourceOSInteractionParticipantRole
    participantRef: str
    agentRegistryRef: NotRequired[str | None]


class SourceOSInteractionTask(TypedDict, total=False):
    taskRef: str | None
    status: SourceOSInteractionTaskStatus
    modelHint: str | None
    modelRouted: str | None
    provider: str | None
    latencyMs: int | None


class SourceOSSteeringIntent(TypedDict, total=False):
    steeringKind: SourceOSSteeringKind
    featureRef: str | None
    strength: float | None
    status: SourceOSSteeringStatus


class SourceOSGovernanceTrace(TypedDict):
    policyAdmitted: bool
    memoryWritten: bool
    policyRef: NotRequired[str | None]
    policyDecisionRefs: NotRequired[list[str]]
    grantRefs: NotRequired[list[str]]
    memoryScopeRef: NotRequired[str | None]
    contextPackRefs: NotRequired[list[str]]
    requestHash: NotRequired[str | None]
    evidenceHash: NotRequired[str | None]
    providerRouteEvidenceRef: NotRequired[str | None]
    agentPlaneRunRef: NotRequired[str | None]
    evidenceRefs: NotRequired[list[str]]
    replayRef: NotRequired[str | None]


class SourceOSInteractionIntegrity(TypedDict, total=False):
    eventHash: str | None
    signature: str | None


class SourceOSInteractionEvent(TypedDict):
    interactionEventId: str
    type: Literal["SourceOSInteractionEvent"]
    specVersion: str
    eventClass: SourceOSInteractionEventClass
    occurredAt: str
    surface: SourceOSInteractionSurface
    mode: SourceOSInteractionMode
    session: SourceOSInteractionSession
    actor: SourceOSInteractionActor
    payloadMode: SourceOSInteractionPayloadMode
    governanceTrace: SourceOSGovernanceTrace
    participants: NotRequired[list[SourceOSInteractionParticipant]]
    task: NotRequired[SourceOSInteractionTask | None]
    steeringIntent: NotRequired[SourceOSSteeringIntent | None]
    payload: NotRequired[dict[str, Any] | None]
    sourceEventRefs: NotRequired[list[str]]
    redactionRefs: NotRequired[list[str]]
    integrity: NotRequired[SourceOSInteractionIntegrity | None]
"""


if __name__ == "__main__":
    raise SystemExit(main())
