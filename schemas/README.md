# Agent Plane Schema Documentation

## Overview
This document provides comprehensive documentation on the Agent Plane schemas, including URN patterns, specification metadata explanation, and usage examples for key entities such as ExecutionDecision, AgentSession, and SessionReceipt.

## Schema Families Table
| Schema Family         | Description                               |
|-----------------------|-------------------------------------------|
| ExecutionDecision     | Represents the decision made by the agent. |
| AgentSession          | Represents a session of an agent.         |
| SessionReceipt        | Represents a receipt for a session.       |

## URN Patterns
### ExecutionDecision URN
- **Pattern**: `urn:sourceos:execution:decision:<decision_id>`

### AgentSession URN
- **Pattern**: `urn:sourceos:agent:session:<session_id>`

### SessionReceipt URN
- **Pattern**: `urn:sourceos:receipt:<receipt_id>`

## Schema Metadata Explanation
Each schema includes metadata that describes its purpose, version, and last updated information.

- **Version**: Indicates the version of the schema.
- **Last Updated**: Date when the schema was last modified.

## Usage Examples
### ExecutionDecision Example
```json
{
  "id": "urn:sourceos:execution:decision:12345",
  "metadata": {
    "version": "1.0",
    "lastUpdated": "2026-04-05"
  },
  "decision": "approve"
}
```

### AgentSession Example
```json
{
  "id": "urn:sourceos:agent:session:12345",
  "metadata": {
    "version": "1.0",
    "lastUpdated": "2026-04-05"
  },
  "status": "active"
}
```

### SessionReceipt Example
```json
{
  "id": "urn:sourceos:receipt:12345",
  "metadata": {
    "version": "1.0",
    "lastUpdated": "2026-04-05"
  },
  "result": "success"
}
```

## Validation Instructions
Schema validation must be performed against the JSON Schema specification outlined in the [official documentation](https://json-schema.org/).

## Versioning Discipline
Follow semantic versioning for all schema updates:
- Major version when incompatible API changes are made,
- Minor version when functionality is added in a backward-compatible manner,
- Patch version when backward-compatible bug fixes are introduced.

## Current Status
All schemas are currently under active development. All feedback is welcomed.

## References
- [JSON Schema Official Website](https://json-schema.org/)
- SourceOS Documentation
- API Reference links