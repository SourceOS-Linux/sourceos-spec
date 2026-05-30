# Generated from schemas/SourceOSInteractionEvent.json.
# Do not edit by hand. Run: python tools/generate_sourceos_interaction_types.py

from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict


SOURCEOS_INTERACTION_EVENT_REQUIRED = ['interactionEventId', 'type', 'specVersion', 'eventClass', 'occurredAt', 'surface', 'mode', 'session', 'actor', 'payloadMode', 'governanceTrace']

SourceOSInteractionEventClass = Literal['interaction.session_started', 'interaction.message_posted', 'interaction.task_submitted', 'interaction.task_stream_delta', 'interaction.task_completed', 'interaction.task_failed', 'interaction.governance_trace', 'interaction.steering_intent', 'interaction.memory_scope_bound', 'interaction.context_pack_bound', 'interaction.policy_decision', 'interaction.approval_requested', 'interaction.approval_recorded', 'interaction.redacted']
SourceOSInteractionSurfaceKind = Literal['noetica', 'agent-term', 'matrix', 'prophet-workspace', 'superconscious', 'agentplane', 'api', 'other']
SourceOSInteractionMode = Literal['standalone', 'sourceos', 'dry-run', 'replay']
SourceOSInteractionActorKind = Literal['human', 'agent', 'service', 'bot', 'system']
SourceOSInteractionParticipantRole = Literal['user', 'assistant', 'operator', 'agent', 'provider', 'tool', 'observer']
SourceOSInteractionTaskStatus = Literal['submitted', 'streaming', 'success', 'failure', 'blocked', 'unavailable', 'not_configured']
SourceOSSteeringKind = Literal['none', 'neuronpedia_feature', 'local_sae', 'sourceos_local', 'other']
SourceOSSteeringStatus = Literal['requested', 'applied', 'noop', 'not_configured', 'blocked']
SourceOSInteractionPayloadMode = Literal['metadata-only', 'summary', 'ref-only', 'inline-bounded', 'redacted']


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
