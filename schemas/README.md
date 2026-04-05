# Agent-Plane Schema Documentation

## Overview
This document provides comprehensive details about the Agent-Plane schemas, including usage examples, URN patterns, spec metadata explanation, and validation instructions.

## Usage Examples
### Example 1: Basic Usage
```json
{
  "exampleKey": "exampleValue"
}
```

### Example 2: Advanced Usage
```json
{
  "advancedKey": [{
    "nestedKey": "nestedValue"
  }]
}
```

## URN Patterns
The URN patterns for the agent-plane schemas follow the structure: `urn:example:<entity>:<id>`.
- **Example:** `urn:sourceos:agent:12345`

## Spec Metadata Explanation
- **version:** The version of the schema being used.
- **description:** A brief overview of the schema.

## Validation Instructions
To validate the agent-plane schema, use the following command:
```bash
jsonschema -i example.json schema.json
```
Make sure to replace `example.json` with your JSON data file and `schema.json` with your schema file.

## Conclusion
This documentation serves as a reference for working with Agent-Plane schemas. For further details, please refer to the additional resources provided in the repository.