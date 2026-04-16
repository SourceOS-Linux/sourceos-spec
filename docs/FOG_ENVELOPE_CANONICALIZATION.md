# Fog Envelope Canonicalization and Signing Profile (v0)

This document defines the **recommended evidence profile** for FogVault and FogCompute envelopes until the rules are promoted into first-class schema constraints and ADRs.

## Goals

- deterministic hashing across heterogeneous nodes
- small, auditable signing surface
- stable content references independent of transport
- explicit separation between content hashing, envelope hashing, and settlement logic

## Canonicalization profile

### 1. Canonical JSON

For any JSON payload that is hashed or signed, implementations should:

1. serialize with **JCS** (JSON Canonicalization Scheme; RFC 8785)
2. encode as UTF-8 bytes
3. hash with **SHA-256**

This yields the canonical `payloadHash`.

### 2. Content hashing

Raw content referenced by `ContentRef` should be hashed over the raw bytes, not over JSON wrappers. The digest form should be:

```text
sha256:<lowercase-hex>
```

### 3. Signature algorithm

The default signature algorithm for Fog envelopes and receipts should be:

- **Ed25519** for detached signatures

Recommended signature field encoding:

```text
ed25519:<base64url-signature>
```

### 4. Domain separation

To avoid cross-object signature confusion, signers should sign a domain-separated preimage:

```text
SRCOS-FOG-V1\n
<object-type>\n
<object-id>\n
<payload-hash>
```

Where:
- `<object-type>` is `TopicEnvelope` or `UsageReceipt`
- `<object-id>` is the object URN
- `<payload-hash>` is the canonical SHA-256 digest string

### 5. Encryption metadata

When envelopes are encrypted, the authenticated additional data (AAD) should bind at least:

- `topicId`
- `entryId` or `receiptId`
- `keyEpoch`
- `payloadType`

Recommended default content cipher for topic payloads:

- **XChaCha20-Poly1305**

## Verification order

### TopicEnvelope

1. resolve and verify `ContentRef` digests if present
2. canonicalize `payload`
3. compute `payloadHash`
4. verify detached signature
5. only then evaluate topic semantics / policy

### UsageReceipt

1. canonicalize receipt body
2. compute `receiptHash`
3. verify detached signature
4. verify referenced `WorkOrder` / output refs / settlement mapping

## What this does not settle yet

This v0 profile does **not** yet fix:

- key distribution / rotation mechanics
- threshold or multisignature receipts
- CBOR/COSE variants
- transport-layer framing
- receipt notarization / timestamp authority integration

Those should land in follow-up ADRs and schema revisions.
