# canon.os-build.v1

**Status:** Draft  
**Intended repository:** `SourceOS-Linux/sourceos-spec`  
**Suggested first release:** `v2.1.0`

## Context

SourceOS and SociOS need a normative contract boundary between immutable host-image identity, mutable install-time binding, and runtime cybernetic meaning. Existing platform discussions and downstream repos already distinguish build substrate, install/enrollment flow, and runtime policy/evidence lanes, but the typed contract canon does not yet expose first-class objects for these layers.

## Decision

This specification defines three first-class contract objects:

- `OSImage` — immutable substrate identity and host contract
- `NodeBinding` — mutable install-time and enrollment-time node assignment
- `CyberneticAssignment` — runtime identity, policy, telemetry, relations, and control semantics

The governing rule is:

- a field belongs in `OSImage` if it changes boot, measured identity, host ABI, update behavior, extension compatibility, or image provenance;
- a field belongs in `NodeBinding` if two nodes can boot the same image but must receive different install-time or enrollment-time values;
- a field belongs in `CyberneticAssignment` if it changes runtime service identity, deployment environment projection, policy, relations, objectives, or control-loop behavior.

## Naming rules

### Immutable short IDs

`OSImage.shortId` uses the pattern:

`so<epoch>-<host-profile>`

Examples:

- `so1-edge-appliance`
- `so1-workstation`
- `so1-vm-base`
- `so1-installer`

### Artifact projection

Rendered artifact names may append artifact and architecture:

`<shortId>-<artifact>-<arch>`

Examples:

- `so1-edge-appliance-oci-aarch64`
- `so1-vm-base-qcow2-x86_64`
- `so1-installer-iso-x86_64`

### Forbidden in immutable short IDs

Do not encode:

- environment (`dev`, `stage`, `prod`)
- topology (`na-use1`, `eu-de1`)
- customer or site names
- cybernetic role words (`sensor`, `planner`, `governor`)
- runtime service names

## Required object shape

### `OSImage`

Must contain:

- URN identity
- `shortId`
- `family`, `epoch`, `hostProfile`, `artifact`, `architecture`
- `osRelease` with at least `ID`, `VERSION_ID`, `IMAGE_ID`, `IMAGE_VERSION`
- OCI annotations
- substrate capability list
- provenance references

### `NodeBinding`

Must contain:

- URN identity
- `imageRef`
- `nodeProfile`
- topology
- fleet
- update ring

May contain:

- registry mirrors
- hostname template
- installer profile
- bootstrap trust roots
- install-time target image reference

### `CyberneticAssignment`

Must contain:

- URN identity
- `nodeRef`
- runtime service identity
- deployment environment name
- policy refs
- graph relations

May contain:

- principal reference
- control profile reference
- objective set

## Allowlist and denylist

### `OSImage` allowlist categories

- distro lineage and ABI epoch
- boot and update contract
- secure boot / TPM / measured boot posture
- generic hardware and virtualization enablement
- `os-release` identity
- OCI image metadata
- build provenance and attestations
- substrate agents tightly coupled to the host

### `OSImage` denylist categories

- runtime service identity
- deployment environment name
- runtime graph relations
- control objectives
- workload selection intent
- live enrollment tokens
- long-lived secrets

## Versioning

This addition is additive if introduced as new schema types and optional API/event surfaces. Recommended versioning policy:

- patch — clarifications, descriptions, examples
- minor — additive fields and additive schema types
- major — boundary changes or incompatible rename/removal

## Reference example

```json
{
  "id": "urn:srcos:osimage:so1-edge-appliance",
  "type": "OSImage",
  "specVersion": "2.1.0",
  "shortId": "so1-edge-appliance",
  "family": "sourceos",
  "epoch": 1,
  "hostProfile": "edge-appliance",
  "artifact": "oci",
  "architecture": "aarch64",
  "osRelease": {
    "ID": "sourceos",
    "ID_LIKE": ["fedora"],
    "VERSION_ID": "1",
    "IMAGE_ID": "so1-edge-appliance",
    "IMAGE_VERSION": "2026.04.14.1"
  },
  "ociAnnotations": {
    "org.opencontainers.image.version": "2026.04.14.1",
    "org.opencontainers.image.revision": "fcea8a4bf4cb4f06b63e090fd9cf89fcdb24194c",
    "org.opencontainers.image.source": "https://github.com/SourceOS-Linux/sourceos-spec",
    "com.socioprophet.os.channel": "stable"
  },
  "substrateCapabilities": ["bootc", "secureboot", "tpm2", "measured-boot"],
  "provenance": {
    "statementRef": "urn:srcos:attestation:osimage:so1-edge-appliance:2026.04.14.1",
    "slsaPredicateRef": "urn:srcos:slsa:osimage:so1-edge-appliance:2026.04.14.1"
  }
}
```
