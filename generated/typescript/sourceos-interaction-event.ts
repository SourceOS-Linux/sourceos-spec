// Generated from schemas/SourceOSInteractionEvent.json.
// Do not edit by hand. Run: python tools/generate_sourceos_interaction_types.py

export const SOURCEOS_INTERACTION_EVENT_REQUIRED = [
  "interactionEventId",
  "type",
  "specVersion",
  "eventClass",
  "occurredAt",
  "surface",
  "mode",
  "session",
  "actor",
  "payloadMode",
  "governanceTrace"
] as const

export type SourceOSInteractionEventClass = "interaction.session_started" | "interaction.message_posted" | "interaction.task_submitted" | "interaction.task_stream_delta" | "interaction.task_completed" | "interaction.task_failed" | "interaction.governance_trace" | "interaction.steering_intent" | "interaction.memory_scope_bound" | "interaction.context_pack_bound" | "interaction.policy_decision" | "interaction.approval_requested" | "interaction.approval_recorded" | "interaction.redacted"
export type SourceOSInteractionSurfaceKind = "noetica" | "agent-term" | "matrix" | "prophet-workspace" | "superconscious" | "agentplane" | "api" | "other"
export type SourceOSInteractionMode = "standalone" | "sourceos" | "dry-run" | "replay"
export type SourceOSInteractionActorKind = "human" | "agent" | "service" | "bot" | "system"
export type SourceOSInteractionParticipantRole = "user" | "assistant" | "operator" | "agent" | "provider" | "tool" | "observer"
export type SourceOSInteractionTaskStatus = "submitted" | "streaming" | "success" | "failure" | "blocked" | "unavailable" | "not_configured"
export type SourceOSSteeringKind = "none" | "neuronpedia_feature" | "local_sae" | "sourceos_local" | "other"
export type SourceOSSteeringStatus = "requested" | "applied" | "noop" | "not_configured" | "blocked"
export type SourceOSInteractionPayloadMode = "metadata-only" | "summary" | "ref-only" | "inline-bounded" | "redacted"

export interface SourceOSInteractionSurface {
  surfaceKind: SourceOSInteractionSurfaceKind
  sourcePlane: string
  clientRef?: string | null
}

export interface SourceOSInteractionSession {
  sessionId: string
  conversationRef?: string | null
  roomRef?: string | null
  threadRef?: string | null
  workroomRef?: string | null
  topicRef?: string | null
  opsHistoryEventRef?: string | null
}

export interface SourceOSInteractionActor {
  actorRef: string
  actorKind: SourceOSInteractionActorKind
  agentRegistryRef?: string | null
  onBehalfOfRef?: string | null
}

export interface SourceOSInteractionParticipant {
  role: SourceOSInteractionParticipantRole
  participantRef: string
  agentRegistryRef?: string | null
}

export interface SourceOSInteractionTask {
  taskRef?: string | null
  status?: SourceOSInteractionTaskStatus
  modelHint?: string | null
  modelRouted?: string | null
  provider?: string | null
  latencyMs?: number | null
}

export interface SourceOSSteeringIntent {
  steeringKind?: SourceOSSteeringKind
  featureRef?: string | null
  strength?: number | null
  status?: SourceOSSteeringStatus
}

export interface SourceOSGovernanceTrace {
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
}

export interface SourceOSInteractionIntegrity {
  eventHash?: string | null
  signature?: string | null
}

export interface SourceOSInteractionEvent {
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
}

// Required top-level fields in the canonical schema: interactionEventId, type, specVersion, eventClass, occurredAt, surface, mode, session, actor, payloadMode, governanceTrace
