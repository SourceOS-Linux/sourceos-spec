# Phase 2: Comprehensive Agent-Plane Schema Documentation

> **Branch:** `feat/agent-plane-core-schemas-v0`  
> **Spec base URL:** `https://schemas.srcos.ai/v2/`  
> **Status:** Draft – pending schema architect review

---

## Table of Contents

1. [Agent-Plane Schema Family Overview](#1-agent-plane-schema-family-overview)
2. [URN Namespace Strategy](#2-urn-namespace-strategy)
3. [Schema Relationships & Dependency Graph](#3-schema-relationships--dependency-graph)
4. [JSON Schema Validation Quickstart](#4-json-schema-validation-quickstart)
5. [OpenAPI/AsyncAPI Integration Binding](#5-openapiasyncapi-integration-binding)
6. [Complete Examples for Each Schema](#6-complete-examples-for-each-schema)
7. [Versioning & Compatibility Discipline](#7-versioning--compatibility-discipline)
8. [Integration with Imagelab Validators](#8-integration-with-imagelab-validators)
9. [Integration with Agentplane Artifacts](#9-integration-with-agentplane-artifacts)
10. [Follow-Up Roadmap](#10-follow-up-roadmap)
11. [Complete File Inventory](#11-complete-file-inventory)

---

## 1. Agent-Plane Schema Family Overview

The Agent-Plane schema family is a set of 13 JSON Schema documents (JSON Schema draft 2020-12) that together define the full contract layer for SourceOS agent execution, governance, memory, telemetry, and release management.

| # | Schema | `$id` suffix | Purpose |
|---|--------|-------------|---------|
| 1 | **ExecutionDecision** | `ExecutionDecision.json` | Records an allow / deny / ask / defer / rewrite verdict issued by the policy engine for a pending tool call or action within a session. Includes a `sha256:` integrity hash to prevent tampering. |
| 2 | **AgentSession** | `AgentSession.json` | Top-level envelope for a single agent run. Captures role, mode, substrate, surface configuration, and cross-references to skills, memory, decisions, and telemetry. |
| 3 | **ExecutionSurface** | `ExecutionSurface.json` | Inline sub-document (embedded by `AgentSession.$ref`) describing the execution environment: PTY, working directory, sandbox mode, network policy, and egress allowlist. |
| 4 | **SkillManifest** | `SkillManifest.json` | Declares a named skill's version, entry document, activation rules (commands / file patterns / intent tags), binary requirements, policy bindings, and safety flags. |
| 5 | **MemoryEntry** | `MemoryEntry.json` | Represents a single persistent memory item of kind `rule`, `learned`, or `recap`. Scoped to a workspace and optional session. Includes freshness metadata and TTL. |
| 6 | **SessionReceipt** | `SessionReceipt.json` | Closure document for a completed session. Aggregates artifact references, decision references, gate results, and final status. |
| 7 | **SessionReview** | `SessionReview.json` | Post-session review record: links back to the session, the generated summary, and any new `MemoryEntry` items learned during review. |
| 8 | **ExperimentFlag** | `ExperimentFlag.json` | Feature flag document with lifecycle states (`off → shadow → internal → beta → on → retired`) and an emergency kill-switch field. |
| 9 | **RolloutPolicy** | `RolloutPolicy.json` | Audience-targeted rollout rules for an `ExperimentFlag`. Each rule specifies an audience string, target state, and optional percentage. |
| 10 | **FrustrationSignal** | `FrustrationSignal.json` | Session-scoped signal capturing user frustration indicators (e.g. `strong-negative-language`, `cancel`, `tool-loop`). Used to trigger intervention or review. |
| 11 | **TelemetryEvent** | `TelemetryEvent.json` | Lightweight telemetry record tied to a session. Carries an `eventType` string and `severity` level (`debug / info / warn / error`). |
| 12 | **ReleaseReceipt** | `ReleaseReceipt.json` | Release-gate closure document. Records verified artifact hashes, named checks, and final `verified / failed / partial` status. |
| 13 | **EventEnvelope** | `EventEnvelope.json` | Generic event wrapper used by the AsyncAPI channels. Carries actor context, object reference, and a freeform payload. Optional `integrity` block for event signing. |

---

## 2. URN Namespace Strategy

All SourceOS entity identifiers follow the `urn:srcos:<segment>:` pattern. The URN is the primary key used by every schema's `id` field and in cross-document `*Ref` fields.

### Hierarchy

```
urn:srcos:
├── exec-decision:   → ExecutionDecision.id
├── session:         → AgentSession.id
├── surface:         → ExecutionSurface references
├── skill:           → SkillManifest.id
├── memory:          → MemoryEntry.id
├── receipt:session: → SessionReceipt.id
├── session-review:  → SessionReview.id
├── flag:            → ExperimentFlag.id
├── rollout:         → RolloutPolicy.id
├── frustration:     → FrustrationSignal.id
├── telemetry:       → TelemetryEvent.id
├── release-receipt: → ReleaseReceipt.id
├── event:           → EventEnvelope.eventId
├── tool:            → tool request cross-references
├── policy:          → policy cross-references
└── transcript:      → session transcript cross-references
```

### Validation Patterns

Each namespace segment is enforced with a JSON Schema `pattern` constraint:

| URN prefix | Regex pattern |
|------------|---------------|
| `urn:srcos:exec-decision:` | `^urn:srcos:exec-decision:` |
| `urn:srcos:session:` | `^urn:srcos:session:` |
| `urn:srcos:surface:` | `^urn:srcos:surface:` |
| `urn:srcos:skill:` | `^urn:srcos:skill:` |
| `urn:srcos:memory:` | `^urn:srcos:memory:` |
| `urn:srcos:receipt:session:` | `^urn:srcos:receipt:session:` |
| `urn:srcos:session-review:` | `^urn:srcos:session-review:` |
| `urn:srcos:flag:` | `^urn:srcos:flag:` |
| `urn:srcos:rollout:` | `^urn:srcos:rollout:` |
| `urn:srcos:frustration:` | `^urn:srcos:frustration:` |
| `urn:srcos:telemetry:` | `^urn:srcos:telemetry:` |
| `urn:srcos:release-receipt:` | `^urn:srcos:release-receipt:` |
| `urn:srcos:event:` | `^urn:srcos:event:` |

### ID Construction Convention

IDs are composed of:

```
urn:srcos:<segment>:<uuid-v4 or content-hash>
```

For example:
```
urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b
urn:srcos:exec-decision:018f2a3c-1111-7000-aaaa-bbbbccccdddd
```

Content-addressed IDs (e.g. for `MemoryEntry` rule records) may use a deterministic hash of the namespace and key fields.

---

## 3. Schema Relationships & Dependency Graph

The schemas form a directed acyclic reference graph. Arrows indicate "references" (via `*Ref` fields or embedded `$ref`).

```
ExperimentFlag ◄──── RolloutPolicy
                           │
AgentSession ──────────────┼──────► ExecutionSurface  (embedded $ref)
     │                     │
     ├──► SkillManifest ───┴──────► ExecutionSurface  (optional surfaceRef)
     │
     ├──► MemoryEntry
     │
     ├──► ExecutionDecision ◄──── SessionReceipt
     │         │
     │         └──► (policyRef → Policy URN, external)
     │
     ├──► TelemetryEvent
     │
     └──► SessionReceipt
               │
               ├──► SessionReview ──────► MemoryEntry  (learnedMemoryRefs)
               │
               └──► ReleaseReceipt  (via agentplane artifact layer)

FrustrationSignal ──► AgentSession  (sessionRef)
TelemetryEvent    ──► AgentSession  (sessionRef)
EventEnvelope     ──► (any objectId, wraps any payload)
```

### Key Embedded References

| Schema | Field | Target |
|--------|-------|--------|
| `AgentSession` | `surface` | `ExecutionSurface` (full inline `$ref`) |
| `AgentSession` | `skillRefs[]` | `SkillManifest.id` URNs |
| `AgentSession` | `memoryRefs[]` | `MemoryEntry.id` URNs |
| `AgentSession` | `decisionRefs[]` | `ExecutionDecision.id` URNs |
| `AgentSession` | `telemetryRefs[]` | `TelemetryEvent.id` URNs |
| `AgentSession` | `parentSessionRef` | `AgentSession.id` URN (optional) |
| `ExecutionDecision` | `sessionRef` | `AgentSession.id` URN |
| `SessionReceipt` | `sessionRef` | `AgentSession.id` URN |
| `SessionReceipt` | `decisionRefs[]` | `ExecutionDecision.id` URNs |
| `SessionReview` | `sessionRef` | `AgentSession.id` URN |
| `SessionReview` | `learnedMemoryRefs[]` | `MemoryEntry.id` URNs |
| `SkillManifest` | `executionSurfaceRef` | `ExecutionSurface` URN (optional) |
| `RolloutPolicy` | `flagRef` | `ExperimentFlag.id` URN |
| `FrustrationSignal` | `sessionRef` | `AgentSession.id` URN |
| `TelemetryEvent` | `sessionRef` | `AgentSession.id` URN |

---

## 4. JSON Schema Validation Quickstart

All schemas target **JSON Schema draft 2020-12** (`"$schema": "https://json-schema.org/draft/2020-12/schema"`).

### Python – `jsonschema`

```bash
pip install jsonschema
```

```python
import json
import jsonschema
from pathlib import Path

schemas_dir = Path("schemas")

def load_schema(name: str) -> dict:
    return json.loads((schemas_dir / name).read_text())

def validate(instance: dict, schema_name: str) -> None:
    schema = load_schema(schema_name)
    # Build a resolver so $ref to sibling schemas resolves correctly
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{schemas_dir.resolve()}/",
        referrer=schema,
    )
    validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
    validator.validate(instance)
    print(f"✅ {schema_name} – valid")

# Example
decision = {
    "id": "urn:srcos:exec-decision:018f2a3c-0000-7000-aaaa-bbbbccccdddd",
    "type": "ExecutionDecision",
    "specVersion": "2.0.0",
    "sessionRef": "urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b",
    "decision": "allow",
    "reason": "Policy check passed",
    "issuedAt": "2026-04-05T19:00:00Z",
    "decisionHash": "sha256:abc123def456"
}
validate(decision, "ExecutionDecision.json")
```

### Node.js – `ajv`

```bash
npm install ajv ajv-formats
```

```js
const Ajv = require("ajv/dist/2020");
const addFormats = require("ajv-formats");
const fs = require("fs");
const path = require("path");

const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);

const schemasDir = path.join(__dirname, "schemas");

// Pre-load all sibling schemas so $ref resolution works
for (const file of fs.readdirSync(schemasDir).filter(f => f.endsWith(".json"))) {
  const schema = JSON.parse(fs.readFileSync(path.join(schemasDir, file), "utf8"));
  ajv.addSchema(schema);
}

function validate(instance, schemaId) {
  const valid = ajv.validate(schemaId, instance);
  if (!valid) {
    console.error(`❌ ${schemaId}:`, ajv.errors);
    return false;
  }
  console.log(`✅ ${schemaId} – valid`);
  return true;
}

// Example
validate({
  id: "urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b",
  type: "AgentSession",
  specVersion: "2.0.0",
  role: "main",
  status: "running",
  mode: "execute",
  workspaceRef: "ws-primary",
  substrate: "local",
  surface: {
    pty: true, workdir: "/repo", background: false,
    reviewOnly: false, worktreeStrategy: "none",
    sandboxMode: "none", networkMode: "full",
    egressAllowlist: [], elevated: false
  },
  skillRefs: ["urn:srcos:skill:code-gen-v1"],
  memoryRefs: [],
  decisionRefs: [],
  telemetryRefs: [],
  time: { startedAt: "2026-04-05T19:00:00Z" }
}, "https://schemas.srcos.ai/v2/AgentSession.json");
```

---

## 5. OpenAPI/AsyncAPI Integration Binding

The two patch files (`openapi.agent-plane.patch.yaml` and `asyncapi.agent-plane.patch.yaml`) are **additive fragments** designed to be merged into the base `openapi.yaml` and `asyncapi.yaml` respectively.

### OpenAPI Endpoints Added

| Operation ID | Method + Path | Request Schema | Response Schema |
|-------------|---------------|----------------|-----------------|
| `upsertAgentSession` | `POST /v2/sessions` | `AgentSession.json` | `200 ok` |
| `decideExecution` | `POST /v2/execution/decide` | `ExecutionDecision.json` | `ExecutionDecision.json` |
| `upsertSkillManifest` | `POST /v2/skills` | `SkillManifest.json` | `200 ok` |
| `upsertMemoryEntry` | `POST /v2/memory` | `MemoryEntry.json` | `200 ok` |
| `recordSessionReceipt` | `POST /v2/receipts/session` | `SessionReceipt.json` | `200 ok` |

#### Merging the OpenAPI Patch

```bash
# Using yq (https://github.com/mikefarah/yq):
yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' \
  openapi.yaml openapi.agent-plane.patch.yaml > openapi.merged.yaml
```

### AsyncAPI Channels Added

| Channel | Message Name | Payload |
|---------|-------------|---------|
| `srcos.v2.session.events` | `SessionEvent` | `EventEnvelope.json` |
| `srcos.v2.execution.events` | `ExecutionEvent` | `EventEnvelope.json` |
| `srcos.v2.skill.events` | `SkillEvent` | `EventEnvelope.json` |
| `srcos.v2.memory.events` | `MemoryEvent` | `EventEnvelope.json` |
| `srcos.v2.receipt.events` | `ReceiptEvent` | `EventEnvelope.json` |

All async events use the `EventEnvelope` wrapper. The `eventType` field carries the concrete schema name (e.g. `"AgentSession.updated"`, `"ExecutionDecision.issued"`), and the `payload` field carries the full document.

#### Merging the AsyncAPI Patch

```bash
yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' \
  asyncapi.yaml asyncapi.agent-plane.patch.yaml > asyncapi.merged.yaml
```

---

## 6. Complete Examples for Each Schema

### 6.1 ExecutionDecision

```json
{
  "id": "urn:srcos:exec-decision:018f2a3c-0000-7000-aaaa-bbbbccccdddd",
  "type": "ExecutionDecision",
  "specVersion": "2.0.0",
  "sessionRef": "urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b",
  "toolRequestRef": "urn:srcos:tool:018f2a40-beef-7000-0000-111122223333",
  "decision": "allow",
  "reason": "Tool call is within sanctioned scope; policy check passed.",
  "obligations": ["log-output", "verify-post-condition"],
  "policyRef": "urn:srcos:policy:default-agent-safety-v1",
  "issuedAt": "2026-04-05T19:00:00Z",
  "expiresAt": "2026-04-05T19:30:00Z",
  "decisionHash": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
}
```

### 6.2 AgentSession

```json
{
  "id": "urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b",
  "type": "AgentSession",
  "specVersion": "2.0.0",
  "role": "main",
  "status": "running",
  "mode": "execute",
  "workspaceRef": "ws-sourceos-spec",
  "worktreeRef": null,
  "substrate": "local",
  "surface": {
    "pty": true,
    "workdir": "/home/runner/work/sourceos-spec",
    "background": false,
    "reviewOnly": false,
    "worktreeStrategy": "none",
    "sandboxMode": "none",
    "networkMode": "allowlist",
    "egressAllowlist": ["github.com", "schemas.srcos.ai"],
    "elevated": false,
    "protectedPaths": [".git", ".github"]
  },
  "provider": "github-copilot",
  "skillRefs": [
    "urn:srcos:skill:code-gen-v1",
    "urn:srcos:skill:documentation-v1"
  ],
  "memoryRefs": [
    "urn:srcos:memory:018f2a00-aaaa-7000-0000-ffffffffffff"
  ],
  "transcriptRef": "urn:srcos:transcript:018f2a3b-dead-7000-0000-000000000000",
  "decisionRefs": [
    "urn:srcos:exec-decision:018f2a3c-0000-7000-aaaa-bbbbccccdddd"
  ],
  "telemetryRefs": [],
  "time": {
    "startedAt": "2026-04-05T19:00:00Z",
    "endedAt": null
  }
}
```

### 6.3 ExecutionSurface

```json
{
  "pty": false,
  "workdir": "/workspace/agent-run",
  "background": true,
  "reviewOnly": false,
  "worktreeStrategy": "create-temp",
  "sandboxMode": "container",
  "networkMode": "allowlist",
  "egressAllowlist": ["pypi.org", "npmjs.com"],
  "elevated": false,
  "protectedPaths": ["/etc", "/usr"],
  "approvalProfile": "strict"
}
```

### 6.4 SkillManifest

```json
{
  "id": "urn:srcos:skill:code-gen-v1",
  "type": "SkillManifest",
  "specVersion": "2.0.0",
  "name": "code-gen",
  "version": "1.0.0",
  "entryDoc": "skills/code-gen/README.md",
  "description": "Generates, edits, and refactors source code files across supported languages.",
  "activationRules": {
    "commands": ["edit", "create", "refactor"],
    "filePatterns": ["*.ts", "*.py", "*.go", "*.java"],
    "intentTags": ["implement", "fix", "scaffold"]
  },
  "requires": {
    "binaries": ["git"],
    "anyBins": ["node", "python3", "go"],
    "tools": ["bash"]
  },
  "executionSurfaceRef": null,
  "policyBindings": ["urn:srcos:policy:code-safety-v1"],
  "artifactOutputs": ["session-artifact", "diff-artifact"],
  "reviewMode": false,
  "allowShellExecution": true,
  "protectedPaths": [".git", ".env", "*.pem"]
}
```

### 6.5 MemoryEntry

```json
{
  "id": "urn:srcos:memory:018f2a00-aaaa-7000-0000-ffffffffffff",
  "type": "MemoryEntry",
  "specVersion": "2.0.0",
  "kind": "rule",
  "namespace": "sourceos-spec",
  "key": "schema-id-pattern",
  "payloadRef": "memory://blobs/018f2a00-aaaa-7000-0000-ffffffffffff",
  "authoritativeRef": "https://schemas.srcos.ai/v2/",
  "citationRefs": [
    "https://github.com/SourceOS-Linux/sourceos-spec/blob/main/schemas/AgentSession.json"
  ],
  "scope": {
    "workspace": "ws-sourceos-spec",
    "pathPrefixes": ["schemas/"],
    "sessionRef": null
  },
  "freshness": {
    "learnedAt": "2026-04-05T18:00:00Z",
    "reviewedAt": "2026-04-05T19:00:00Z",
    "ttl": null
  }
}
```

### 6.6 SessionReceipt

```json
{
  "id": "urn:srcos:receipt:session:018f2a99-dead-7000-0000-000000000000",
  "type": "SessionReceipt",
  "specVersion": "2.0.0",
  "sessionRef": "urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b",
  "status": "success",
  "artifactRefs": [
    "artifact://session/018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b"
  ],
  "decisionRefs": [
    "urn:srcos:exec-decision:018f2a3c-0000-7000-aaaa-bbbbccccdddd"
  ],
  "gateResults": ["policy-gate:pass", "review-gate:pass"],
  "capturedAt": "2026-04-05T19:30:00Z"
}
```

### 6.7 SessionReview

```json
{
  "id": "urn:srcos:session-review:018f2b00-cafe-7000-0000-000000000001",
  "type": "SessionReview",
  "specVersion": "2.0.0",
  "sessionRef": "urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b",
  "summaryRef": "memory://blobs/018f2b00-cafe-7000-0000-000000000001",
  "learnedMemoryRefs": [
    "urn:srcos:memory:018f2a00-aaaa-7000-0000-ffffffffffff"
  ],
  "followupRefs": [
    "https://github.com/SourceOS-Linux/sourceos-spec/issues/5"
  ],
  "reviewedAt": "2026-04-05T19:35:00Z"
}
```

### 6.8 ExperimentFlag

```json
{
  "id": "urn:srcos:flag:multi-agent-coordination-v1",
  "type": "ExperimentFlag",
  "specVersion": "2.0.0",
  "name": "multi-agent-coordination",
  "state": "shadow",
  "owner": "platform-team",
  "description": "Enables parallel sub-agent spawning with shared memory bus.",
  "killSwitch": true
}
```

### 6.9 RolloutPolicy

```json
{
  "id": "urn:srcos:rollout:018f2c00-feed-7000-0000-000000000002",
  "type": "RolloutPolicy",
  "specVersion": "2.0.0",
  "flagRef": "urn:srcos:flag:multi-agent-coordination-v1",
  "rules": [
    { "audience": "internal-eng",   "state": "on",     "percentage": null },
    { "audience": "beta-partners",  "state": "beta",   "percentage": 20   },
    { "audience": "general",        "state": "shadow",  "percentage": 5    }
  ],
  "notes": "Gradual rollout – monitor frustration signals before expanding beta."
}
```

### 6.10 FrustrationSignal

```json
{
  "id": "urn:srcos:frustration:018f2d00-babe-7000-0000-000000000003",
  "type": "FrustrationSignal",
  "specVersion": "2.0.0",
  "sessionRef": "urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b",
  "signal": "tool-loop",
  "count": 4,
  "capturedAt": "2026-04-05T19:15:00Z"
}
```

### 6.11 TelemetryEvent

```json
{
  "id": "urn:srcos:telemetry:018f2e00-face-7000-0000-000000000004",
  "type": "TelemetryEvent",
  "specVersion": "2.0.0",
  "sessionRef": "urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b",
  "eventType": "tool.call.completed",
  "severity": "info",
  "capturedAt": "2026-04-05T19:05:00Z"
}
```

### 6.12 ReleaseReceipt

```json
{
  "id": "urn:srcos:release-receipt:018f2f00-a1b2-7000-0000-000000000005",
  "type": "ReleaseReceipt",
  "specVersion": "2.0.0",
  "releaseTarget": "sourceos-agent-runtime@2.0.0",
  "sourceRef": "urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b",
  "artifactHashes": [
    "sha256:abc123def456abc123def456abc123def456abc123def456abc123def456abc1",
    "sha256:000fffaabbcc000fffaabbcc000fffaabbcc000fffaabbcc000fffaabbcc0001"
  ],
  "checks": ["unit-tests:pass", "integration-tests:pass", "schema-lint:pass"],
  "status": "verified",
  "verifiedAt": "2026-04-05T20:00:00Z"
}
```

### 6.13 EventEnvelope

```json
{
  "eventId": "urn:srcos:event:018f3000-e5e5-7000-0000-000000000006",
  "eventType": "AgentSession.updated",
  "specVersion": "2.0.0",
  "occurredAt": "2026-04-05T19:00:01Z",
  "actor": {
    "subjectId": "user:mdheller",
    "ip": "203.0.113.1"
  },
  "objectId": "urn:srcos:session:018f2a3b-4c5d-7e6f-8a9b-0c1d2e3f4a5b",
  "payload": {
    "status": "running"
  },
  "integrity": {
    "eventHash": "sha256:cafebabecafebabecafebabecafebabecafebabecafebabecafebabecafebabe",
    "signature": null
  }
}
```

---

## 7. Versioning & Compatibility Discipline

### SemVer Strategy

All schemas follow **Semantic Versioning 2.0.0** expressed in the `specVersion` field of every document:

| Change type | Version bump | Example |
|------------|--------------|---------|
| New **required** field or enum value removed | **MAJOR** | `1.x.x → 2.0.0` |
| New **optional** field added; new enum value added | **MINOR** | `2.0.x → 2.1.0` |
| Documentation fix, description update, no structural change | **PATCH** | `2.0.0 → 2.0.1` |

### Backward Compatibility Rules

1. **Never remove a field** that is required by any in-production consumer. Deprecate it with `"deprecated": true` in the schema annotation first.
2. **Never change an existing `enum` value** without a MAJOR bump. Adding new enum values is a MINOR bump.
3. **Never tighten an existing `pattern` or `format`** constraint. Relaxing a pattern is a MINOR bump.
4. **`additionalProperties: false`** is enforced on all schemas to prevent undocumented field drift. Any new field must be explicitly added via a schema change.

### Schema File Naming

Schema files are named after the schema `title` and live in the `schemas/` directory. The `$id` URI (`https://schemas.srcos.ai/v2/<Title>.json`) reflects the major version (`v2`) in the path component. A new major version (v3) would live in a parallel `https://schemas.srcos.ai/v3/` namespace.

### Deprecation Path

1. Annotate deprecated field with a description note in the schema.
2. Publish a MINOR release that flags the deprecation in the registry changelog.
3. After one major release cycle (minimum 90 days), remove in a MAJOR bump.

---

## 8. Integration with Imagelab Validators

[Imagelab](https://github.com/SociOS-Linux/imagelab) provides capability descriptor patches and schema validators that act as admission controllers for agent artifacts. The binding between Imagelab validators and these schemas works as follows:

### Validator Entry Points

Imagelab validators expose a module-level `validate(payload: dict) -> ValidationResult` function. The `ValidationResult` contract is:

```python
@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]
    schema: str          # e.g. "ExecutionDecision"
```

### Binding Table

| Validator class | Schema validated | Admission context |
|----------------|-----------------|-------------------|
| `ExecutionDecisionValidator` | `ExecutionDecision.json` | Pre-execution policy gate |
| `SkillManifestValidator` | `SkillManifest.json` | Skill registration / activation |
| `SessionReceiptValidator` | `SessionReceipt.json` | Session closure gate |

### Admission Webhook Flow

```
[Agent Runtime]
     │  POST /v2/execution/decide  (ExecutionDecision payload)
     ▼
[Imagelab Admission Webhook]
     │  validate(payload, "ExecutionDecision")
     ▼
  valid?
  ├── YES → forward to agent-plane API
  └── NO  → reject with 422 + error details
```

### Capability Descriptor Patch

The `capd/imagelab.capd.patch.yaml` in the Imagelab repo declares the validator entrypoints and their schema bindings. Once merged, Imagelab can be registered as a validation sidecar to any agent-plane deployment.

---

## 9. Integration with Agentplane Artifacts

[Agentplane](https://github.com/SocioProphet/agentplane) manages the artifact lifecycle produced by agent sessions. The artifact schemas cross-reference the SourceOS-spec schemas as follows:

### Artifact ↔ Schema Binding

| Agentplane artifact | References (from sourceos-spec) | Usage |
|--------------------|---------------------------------|-------|
| `SessionArtifact` | `AgentSession.id`, `SessionReceipt.id` | Bundles session output with its receipt |
| `PromotionArtifact` | `SessionReceipt.id`, `ReleaseReceipt.id` | Records promotion decision and target |
| `ReversalArtifact` | `SessionReceipt.id`, `ExecutionDecision.id` | Records reversal decision and reason |

### Artifact Lifecycle

```
AgentSession (running)
     │ completes
     ▼
SessionReceipt (captured) ──────────────────► SessionArtifact (bundled)
                                                       │
                              ┌────────────────────────┤
                              │                        │
                    passed gate?                  failed gate?
                              │                        │
                              ▼                        ▼
                    PromotionArtifact          ReversalArtifact
                    (releaseTarget set)        (blockFurtherUse: true)
                              │
                              ▼
                    ReleaseReceipt (verified)
```

### SessionReceipt → SessionArtifact Key Fields

When Agentplane creates a `SessionArtifact`, it copies:
- `sessionRef` ← `AgentSession.id`
- `capturedAt` ← `SessionReceipt.capturedAt`
- `status` ← derived from `SessionReceipt.status`
- `gateResults` ← `SessionReceipt.gateResults`

---

## 10. Follow-Up Roadmap

### Phase 2.5 – Schema Hardening (next sprint)

- [ ] Add JSON Schema `$defs` for reusable sub-types (e.g. `SrcoURN`, `Sha256Hash`, `ISOTimestamp`) to eliminate pattern duplication across schemas
- [ ] Add `examples` annotations to each schema property for IDE tooling
- [ ] Publish schemas to `https://schemas.srcos.ai/v2/` with CORS headers for browser-based validators
- [ ] Add `GET /v2/schemas/{name}` endpoint to the OpenAPI spec

### Phase 3 – Runtime Enforcement

- [ ] Wire `ExecutionDecisionValidator` into the agent runtime as a synchronous policy gate
- [ ] Integrate `FrustrationSignal` capture into the session loop (detect `tool-loop`, `repeated-failure`)
- [ ] Connect `TelemetryEvent` emission to the AsyncAPI `srcos.v2.execution.events` channel
- [ ] Implement `ReleaseReceipt` generation in the CI gate of the Agentplane artifact promotion flow

### Phase 3.5 – Governance Extensions

- [ ] Add `MemoryEntry.kind = "governance"` for cross-session policy memory
- [ ] Extend `RolloutPolicy` to support time-boxed rollout windows (`activeFrom`, `activeTo`)
- [ ] Add `AgentSession.coalitionRef` for multi-agent coalition tracking
- [ ] Define `AuditTrail` schema linking `ExecutionDecision` + `FrustrationSignal` + `TelemetryEvent` into a single audit record

### Phase 4 – Toolchain Integration

- [ ] prophet-cli `srcos schema validate <file>` command for local schema validation
- [ ] VS Code extension with JSON Schema language server integration
- [ ] Schema diff tooling for automated compatibility checks in CI
- [ ] Schema registry with version history and deprecation tracking

---

## 11. Complete File Inventory

All 15 files introduced or modified in PR `feat/agent-plane-core-schemas-v0`:

| # | File | Lines | Purpose |
|---|------|-------|---------|
| 1 | `schemas/ExecutionDecision.json` | 87 | Policy gate verdict for a tool call or action; carries integrity hash |
| 2 | `schemas/AgentSession.json` | 157 | Top-level session envelope; inline-refs `ExecutionSurface` |
| 3 | `schemas/ExecutionSurface.json` | 77 | Execution environment config (sandbox, network, worktree strategy) |
| 4 | `schemas/SkillManifest.json` | 125 | Skill declaration with activation rules, binary requirements, safety flags |
| 5 | `schemas/MemoryEntry.json` | 115 | Persistent memory item with scope, freshness, and TTL |
| 6 | `schemas/SessionReceipt.json` | 66 | Session closure record: artifacts, decisions, gate results, status |
| 7 | `schemas/SessionReview.json` | 26 | Post-session review linking session to summary and learned memories |
| 8 | `schemas/ExperimentFlag.json` | 18 | Feature flag with lifecycle states and kill-switch |
| 9 | `schemas/RolloutPolicy.json` | 28 | Audience-targeted rollout rules for an experiment flag |
| 10 | `schemas/FrustrationSignal.json` | 17 | Session-scoped user frustration signal for intervention triggering |
| 11 | `schemas/TelemetryEvent.json` | 17 | Lightweight telemetry event with severity level |
| 12 | `schemas/ReleaseReceipt.json` | 19 | Release-gate closure: artifact hashes, checks, verified status |
| 13 | `openapi.agent-plane.patch.yaml` | 56 | Additive OpenAPI fragment wiring 5 REST endpoints to schemas |
| 14 | `asyncapi.agent-plane.patch.yaml` | 27 | Additive AsyncAPI fragment wiring 5 event channels to `EventEnvelope` |
| 15 | `schemas/README.md` | 81 | Agent-plane schema documentation overview (URN patterns, examples, validation) |

> **Note:** `schemas/EventEnvelope.json` (the 13th schema type documented above) is a pre-existing schema in the repo referenced by the AsyncAPI patch. It is not a new file in this PR.
