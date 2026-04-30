# NACP — Networked Agent Contract Protocol

**Version:** 1.1.1-draft
**Status:** Draft (open protocol; see [docs/GOVERNANCE.md](docs/GOVERNANCE.md))
**Last Reviewed:** 2026-04-30

---

> **NACP is a transport-neutral contract protocol for autonomous agent work.** It defines the agreement and accountability envelope around delegated tasks: identity, terms, lifecycle, execution references, evidence, auditability, and settlement metadata.
>
> NACP does **not** replace A2A, MCP, payment rails, marketplaces, or any agent runtime. It defines the contract that wraps work performed through any of those.

---

## 1. Purpose and Scope

NACP defines:

- the structure of a **contract** between a requester and a provider of delegated work
- the **lifecycle** that contract moves through
- the **references** that connect the contract to where work actually happens (execution transports, tool calls, files, artifacts)
- the **evidence** that work was performed
- the **audit events** that record state changes and notable events
- the **settlement metadata** that references external payment, escrow, credit, receipt, or settlement systems

NACP does **not** define:

- a specific transport for performing the work
- a specific payment rail or currency
- a specific registry, broker, marketplace, or runtime
- a scoring system, benchmark suite, or tournament system
- product-specific behavior of any kind

Product-specific or domain-specific behavior MUST be expressed through namespaced extension fields. See [§9](#9-extensions-and-versioning) and [docs/GOVERNANCE.md](docs/GOVERNANCE.md).

### 1.1 Conformance language

The keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY in this document are to be interpreted as described in RFC 2119/RFC 8174.

### 1.2 Core vs. optional

This specification distinguishes:

- **Core** (§2 – §4, §9): the neutral contract layer. Conformant implementations MUST be able to produce and consume contracts as defined here.
- **Optional bindings** (§5 – §8): signed-message envelopes, REST and WebSocket transports, cryptographic handshakes, and tooling bridges. These are non-exclusive and not required for core conformance.

A conformant implementation MAY support any subset of the optional bindings.

---

## 2. The Contract

A NACP **contract** is a structured record of delegated work. Implementations MUST be able to represent at least the following fields. Schema: [`schemas/contract.schema.json`](schemas/contract.schema.json).

### 2.1 Core contract fields

| Field | Type | Required | Description |
|---|---|---|---|
| `contract_id` | string | yes | Implementation-assigned, globally unique identifier for the contract. |
| `contract_type` | string | yes | Neutral category, e.g. `delegated_task`, `subscription`, `evaluation`. Implementation-defined values SHOULD be namespaced. |
| `protocol_version` | string | yes | NACP protocol version (e.g. `"1.1"`). |
| `requester` | object | yes | Identity reference for the party requesting work. See §2.2. |
| `provider` | object | yes | Identity reference for the party accepting responsibility for the work. See §2.2. |
| `created_at` | string | yes | ISO-8601 UTC timestamp the contract was created. |
| `accepted_at` | string | no | ISO-8601 UTC timestamp the provider accepted the contract. |
| `expires_at` | string | no | ISO-8601 UTC timestamp after which an unaccepted contract is void. |
| `deadline_at` | string | no | ISO-8601 UTC timestamp by which the work must be complete. |
| `task_category` | string | no | Neutral category for the work itself, e.g. `code_review`, `summarization`, `data_extraction`. |
| `task_summary` | string | no | Short human-readable summary of the work. |
| `task_payload_ref` | object | no | Pointer to the detailed task payload. See §3. |
| `execution_transport` | string | yes | Identifier for the transport on which the work will be performed: `a2a`, `mcp`, `api`, `queue`, `p2p`, `file`, `human`, or an implementation-namespaced value. |
| `execution_refs` | object | no | Transport-specific references. See §3. |
| `output_requirements` | object | no | What output is expected (format, schema, fields). |
| `evidence_requirements` | object | no | What evidence is expected (artifacts, signed receipts, logs). |
| `lifecycle_status` | string | yes | Current lifecycle state. See §4. |
| `audit_events` | array | no | Append-only list of audit event records. See §4.3. |
| `evaluation_reference` | object | no | Optional pointer to a separate evaluation, scoring, or QA process. NACP does not define what that process is. |
| `settlement_mode` | string | no | One of `none`, `prepaid`, `postpaid`, `escrow`, `external_reference`, or an implementation-namespaced value. |
| `settlement_reference` | object | no | Pointer to an external payment, escrow, credit, receipt, or settlement system. NACP does not move money. See §6. |
| `dispute_status` | string | no | One of `none`, `open`, `resolved`, `withdrawn`, or implementation-namespaced. |
| `extension_fields` | object | no | Namespaced extension data. See §9. |

### 2.2 Identity references

`requester` and `provider` are identity references with the following minimum shape:

```json
{
  "id": "<implementation-defined identifier>",
  "id_type": "did | url | uuid | fingerprint | other",
  "display_name": "<optional human-readable label>",
  "public_key": "<optional public key for signature verification>",
  "public_key_alg": "<optional, e.g. ed25519>"
}
```

NACP does not mandate a specific identity scheme. Implementations MAY use DIDs, URLs, UUIDs, public-key fingerprints, or any other stable identifier. When non-repudiation matters, identities SHOULD include a public key (or a way to resolve one).

---

## 3. Execution References

NACP contracts are **transport-neutral**. The detailed task payload may live outside the contract. The contract carries enough metadata to identify the parties, terms, lifecycle, evidence, and settlement state — and a reference to wherever the work actually happens.

`execution_transport` names the transport. `execution_refs` carries the transport-specific pointers. The values below are **reserved identifiers** the spec uses for common transports — not a closed set. Implementations MAY define additional values; those SHOULD be namespaced (e.g. `acme.queue`). NACP imposes no requirements on the listed transports themselves and does not depend on any of them.

### 3.1 Over A2A

```json
{
  "execution_transport": "a2a",
  "execution_refs": {
    "agent_card_url": "https://example.com/.well-known/agent-card.json",
    "task_id": "task_456",
    "message_ids": ["msg_1", "msg_2"],
    "artifact_ids": ["artifact_1"]
  }
}
```

### 3.2 Over MCP-enabled tools

```json
{
  "execution_transport": "mcp",
  "execution_refs": {
    "server_uri": "stdio://example-mcp-server",
    "tool_name": "search_documents",
    "tool_call_ids": ["call_abc"]
  }
}
```

### 3.3 Over a direct API

```json
{
  "execution_transport": "api",
  "execution_refs": {
    "endpoint": "https://example.com/api/v1/jobs",
    "job_id": "job_789",
    "request_id": "req_012"
  }
}
```

### 3.4 Over file or artifact exchange

```json
{
  "execution_transport": "file",
  "execution_refs": {
    "input_uri": "s3://bucket/inputs/2026-04-30/job.json",
    "output_uri": "s3://bucket/outputs/2026-04-30/job.json",
    "content_hash": "sha256:..."
  }
}
```

Implementations MAY define additional `execution_transport` values; these SHOULD be namespaced (e.g. `acme.queue`).

`task_payload_ref` follows the same idea but specifically points to the detailed task description, which may differ from where execution happens (e.g. a payload on object storage, executed via A2A).

See [docs/TRANSPORT_NEUTRALITY.md](docs/TRANSPORT_NEUTRALITY.md) for worked examples.

---

## 4. Lifecycle and Audit

### 4.1 Lifecycle states

NACP defines a neutral lifecycle. Implementations MUST support these core states:

| State | Meaning |
|---|---|
| `proposed` | Contract has been created and offered to a provider. |
| `accepted` | Provider has accepted responsibility for the work. |
| `rejected` | Provider has declined the contract. |
| `in_progress` | Work has begun. |
| `paused` | Work has been paused at the request of either party. |
| `completed` | Work has been delivered and meets `output_requirements` / `evidence_requirements`. |
| `failed` | Work could not be completed. |
| `cancelled` | Either party cancelled before completion. |
| `disputed` | A party has raised a dispute. |
| `settled` | Settlement metadata has been recorded; this state is independent of `completed` and may follow it. |

Implementations MAY add additional namespaced lifecycle states as `extension_fields.lifecycle_state_extensions` but MUST NOT redefine the meanings of the core states above.

### 4.2 Permitted transitions

Implementations SHOULD enforce the following transitions:

```
proposed   → accepted | rejected | cancelled
accepted   → in_progress | cancelled
in_progress → paused | completed | failed | cancelled | disputed
paused     → in_progress | cancelled | disputed
completed  → settled | disputed
failed     → disputed | settled
disputed   → in_progress | completed | failed | cancelled | settled
```

Any attempt to transition outside these is non-conformant.

### 4.3 Audit events

`audit_events` is an append-only list of records describing state changes and notable events. Each record SHOULD have:

```json
{
  "event_id": "evt_...",
  "timestamp": "2026-04-30T12:00:00.000000Z",
  "actor": { "id": "...", "id_type": "..." },
  "event_type": "lifecycle_transition | evidence_added | settlement_recorded | message_sent | dispute_raised | ...",
  "details": { },
  "signature": "<optional base64 signature>"
}
```

Implementations SHOULD make the audit log tamper-evident (e.g. by chaining records or signing them). NACP does not mandate a specific scheme.

Schema: [`schemas/audit_event.schema.json`](schemas/audit_event.schema.json).

---

## 5. Evidence

`evidence_requirements` declares what must be produced; evidence itself is recorded by reference. Evidence references SHOULD use the same shape as `execution_refs`:

```json
{
  "evidence": [
    {
      "kind": "artifact",
      "uri": "https://example.com/artifacts/result.json",
      "content_hash": "sha256:..."
    },
    {
      "kind": "tool_call_log",
      "transport": "mcp",
      "call_ids": ["call_abc"]
    },
    {
      "kind": "signed_receipt",
      "uri": "https://example.com/receipts/r_001"
    }
  ]
}
```

Evidence MAY also live as additions to `audit_events` of type `evidence_added`.

---

## 6. Settlement Metadata

NACP **does not move money** and is **not a payment rail**. It records *references* to external payment, escrow, credit, receipt, or settlement systems so a contract carries the metadata required to reconcile or audit it.

`settlement_mode` describes the model:

| Value | Meaning |
|---|---|
| `none` | No settlement. |
| `prepaid` | Requester has prepaid through an external system. |
| `postpaid` | Requester will pay after delivery through an external system. |
| `escrow` | Funds are held in an external escrow. |
| `external_reference` | Settlement is handled entirely outside NACP; a reference is recorded. |

`settlement_reference` carries the pointer:

```json
{
  "settlement_mode": "external_reference",
  "settlement_reference": {
    "system": "stripe",
    "reference_id": "pi_...",
    "amount_quoted": "0.10",
    "currency": "USD",
    "receipt_uri": "https://example.com/receipts/r_001"
  }
}
```

`system`, `reference_id`, and `currency` are opaque to NACP. Implementations MAY use any payment system, ledger, credit system, or none.

Schema: [`schemas/settlement.schema.json`](schemas/settlement.schema.json).

---

## 7. Disputes

`dispute_status` indicates the dispute state of a contract. The detailed dispute payload SHOULD be captured in `audit_events` of type `dispute_raised`, `dispute_evidence`, and `dispute_resolved`. NACP does not define how disputes are resolved; that is implementation- or platform-specific.

---

## 8. Optional Bindings

The remainder of this document defines **optional bindings** that an implementation MAY adopt. These are non-exclusive: a conformant NACP implementation MAY use any subset, all, or none of them. Core conformance (§2 – §4, §9) does not require any optional binding.

### 8.1 Signed-message envelope (optional)

Implementations that want non-repudiation for inter-agent messaging MAY use a signed JSON envelope. Each envelope is signed with Ed25519:

```json
{
  "version": "1.1",
  "msg_id": "uuid-v4",
  "timestamp": "2026-04-24T12:00:00.000000Z",
  "type": "TASK_ASSIGN",
  "from": "agent-id-or-did",
  "to": "agent-id-or-broadcast",
  "reply_to": "optional-correlation-msg-id",
  "priority": 5,
  "ttl": 300,
  "payload": { },
  "signature": "base64-ed25519-signature",
  "session_id": "optional-encrypted-session-id"
}
```

Schema: [`schemas/envelope.schema.json`](schemas/envelope.schema.json).

#### 8.1.1 Default message types

A reference catalog of message types is provided for implementations that want a ready-made wire protocol. None of these are required for core conformance; implementations are free to express the same semantics over A2A, REST, queues, or any other transport.

| Category | Types |
|---|---|
| Health | `PING`, `PONG`, `HEARTBEAT` |
| Discovery | `DISCOVER`, `SKILL_QUERY`, `SKILL_RESPONSE` |
| Task lifecycle | `TASK_ASSIGN`, `TASK_ACCEPT`, `TASK_REJECT`, `TASK_PROGRESS`, `TASK_RESULT`, `TASK_CANCEL`, `TASK_CANCELLED`, `TASK_STATUS_QUERY`, `TASK_STATUS_RESPONSE`, `TASK_PAUSE`, `TASK_RESUME` |
| P2P signaling | `SIGNALING_ICE`, `SIGNALING_SDP`, `SIGNALING_PEER` |
| Cryptographic handshake | `HANDSHAKE_INIT`, `HANDSHAKE_ACK`, `CHANNEL_OPEN`, `CHANNEL_CLOSE` |
| Control | `ERROR` |

When this binding is used, task lifecycle messages SHOULD reference a NACP `contract_id` so contract state and message state stay aligned.

#### 8.1.2 Canonical JSON for signing

Signature verification depends on deterministic serialization. All implementations using this binding MUST use this canonical form:

1. **Encoding:** UTF-8.
2. **Serialization:** `json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`.
3. **Signature exclusion:** the `signature` field is REMOVED from the envelope before computing the canonical form.
4. **Optional fields:** missing optional fields are OMITTED entirely, NOT set to `null`.
5. **Timestamps:** ISO-8601 with microseconds, UTC, using `Z` suffix: `"2026-04-24T12:00:00.000000Z"`.
6. **Base64:** RFC 4648 §4 (not base64url).
7. **Numbers:** no trailing zeros; integers when there is no decimal part.
8. **Field order:** `sort_keys=True` for alphabetical key ordering.

```python
import json

def canonical_json(envelope: dict) -> str:
    canonical = {k: v for k, v in envelope.items() if k != "signature"}
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

#### 8.1.3 Error codes (envelope ERROR type)

| Code | Meaning |
|---|---|
| `NACP-400` | Malformed message |
| `NACP-401` | Invalid or missing signature |
| `NACP-402` | Settlement / payment required |
| `NACP-403` | Unauthorized |
| `NACP-404` | Not found |
| `NACP-408` | Timeout |
| `NACP-409` | Conflict |
| `NACP-413` | Payload too large |
| `NACP-422` | Body validation failed (REST) |
| `NACP-429` | Rate limited |
| `NACP-500` | Internal error |
| `NACP-503` | Service unavailable |

### 8.2 REST binding (optional)

NACP-conformant REST APIs MAY adopt one or both of these authentication patterns and the unified error envelope.

#### 8.2.a Envelope-in-body (`X-NACP-Signature` optional)

When the request body **is** an NACP envelope (e.g. an inbound message delivered via `POST /nacp/inbox`), the signature travels inside the envelope's `signature` field. Implementations MAY additionally echo it in `X-NACP-Signature` for intermediaries.

```
POST /nacp/inbox
X-NACP-Signature: base64-signature   (optional)
Content-Type: application/json

{ "version": "1.1", ..., "signature": "base64-ed25519-signature" }
```

#### 8.2.b Action-envelope header (`X-NACP-Auth`)

For state-changing endpoints with no envelope to put a signature in (e.g. `DELETE /api/v1/agents/{id}`), the caller wraps a fresh signed envelope of type `AUTH_ACTION` and sends it base64-encoded in `X-NACP-Auth`:

```
DELETE /api/v1/agents/{id}
X-NACP-Auth: base64( {
  "version": "1.1",
  "msg_id": "<uuid4>",
  "timestamp": "<ISO-8601 UTC>",
  "type": "AUTH_ACTION",
  "from": "<caller-agent-id>",
  "to": "<implementation-system-id>",
  "payload": {
    "action": "<action>",
    "agent_id": "<target-agent-id>"
  },
  "signature": "<base64 Ed25519>"
} )
```

The receiver:

1. Base64-decodes the header, parses the JSON envelope.
2. Asserts `type == "AUTH_ACTION"`.
3. Asserts `payload.action` is one of the recognised actions for the endpoint.
4. Asserts `payload.agent_id` matches the path-level resource.
5. Verifies the Ed25519 signature against the canonical-JSON form of the envelope (signature stripped) and the registered public key of `from`.
6. Records `msg_id` for replay protection within the time-skew window.

Implementations using this binding SHOULD advertise their action set at their own `.well-known/nacp.auth.action_registry`. This is a **per-implementation, locally-served** discovery document — there is no global registry, and NACP does not mandate one. Action names are implementation-namespaced (e.g. `acme.heartbeat`); bare names are reserved for the spec.

Schema: [`schemas/auth_action.schema.json`](schemas/auth_action.schema.json).

#### 8.2.c Unified REST error envelope

NACP-conformant REST APIs SHOULD return non-2xx responses in this shape:

```json
{
  "error_code": "NACP-404",
  "error_message": "Not found",
  "error_detail": null,
  "request_id": "<X-Request-Id>"
}
```

Schema: [`schemas/rest_error.schema.json`](schemas/rest_error.schema.json). `error_code` extends §8.1.3.

### 8.3 WebSocket binding (optional)

Two patterns are defined.

#### 8.3.a Direct agent-to-agent

```
ws://host:port/nacp/ws?agent_id=<id>&session_id=<optional>
```

Used for direct connections; out of scope for this version.

#### 8.3.b Mediated relay push

A mediator-delivered fast path:

```
WS /api/v1/relay/{agent_id}
```

**Auth frame** (first frame, client → server): a single TEXT frame containing an `AUTH_ACTION` envelope (§8.2.b) with `payload.action == "ws_relay"`. Server has 10 seconds to receive it before closing with code 4401.

**Server-sent frames** — see [`schemas/ws_relay_frame.schema.json`](schemas/ws_relay_frame.schema.json):

- `AUTH_OK`: acknowledgement
- `RELAY`: inbound envelope

**Close codes:**

| Code | Meaning |
|---|---|
| `4400` | Bad JSON in auth frame |
| `4401` | Auth timeout or signature failure |
| `4403` | Identity / path mismatch |

#### 8.3.c Mediated relay (HTTP)

Agents behind NAT MAY use a mediator (relay) service:

```
POST  /api/v1/relay          # Send (envelope-in-body, §8.2.a)
GET   /api/v1/relay/{id}     # Poll (X-NACP-Auth, action="relay_poll")
WS    /api/v1/relay/{id}     # Push (§8.3.b)
```

Mediators SHOULD cap relay payload size (e.g. 64 KB) so agents exchange pointers (presigned URLs, content IDs) rather than raw bytes.

### 8.4 Cryptographic handshake (optional)

Implementations needing forward-secret sensitive data MAY use the handshake messages in §8.1.1:

```
Agent A                    Mediator                  Agent B
  |--- HANDSHAKE_INIT ------>|--- HANDSHAKE_INIT ------>|
  |<-- HANDSHAKE_ACK --------|<-- HANDSHAKE_ACK --------|
  |<-------- Encrypted Channel (XSalsa20-Poly1305) ---->|
```

**Key derivation:**

1. Both agents generate X25519 ephemeral keypairs.
2. Diffie-Hellman shared secret computed.
3. BLAKE2b derivation with salt `nacp-v1-key` produces a 32-byte symmetric key.
4. Encryption via NaCl SecretBox (XSalsa20-Poly1305).

**Key rotation:** keys rotate every 24 hours or on `CHANNEL_CLOSE` with `rotate_key: true`; a new handshake is required after rotation.

### 8.5 Tool/protocol bridges (optional)

NACP MAY be bridged to:

- A2A — see [docs/A2A_COMPATIBILITY.md](docs/A2A_COMPATIBILITY.md)
- MCP — see [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md)

Bridges are non-exclusive. Neither A2A nor MCP is required for core conformance.

---

## 9. Extensions and Versioning

### 9.1 Extension namespaces

All product-specific or domain-specific behavior MUST live in `extension_fields` under a namespace owned by the extension author:

```json
{
  "extension_fields": {
    "acme.scoring": {
      "rubric_id": "rubric_v3",
      "score": 0.87
    },
    "acme.tournament": {
      "round_id": "round_5"
    }
  }
}
```

Bare (un-namespaced) keys in `extension_fields` are reserved for the spec.

Implementations MUST NOT reject contracts because of unknown extension namespaces; unknown extensions are passed through unchanged.

### 9.2 Versioning

- **Major** version bump: breaking changes (field removal, type changes).
- **Minor** version bump: backward-compatible additions (new fields, new lifecycle states with namespaced extensions).
- **Patch** version bump: clarifications and documentation fixes.

`protocol_version` on a contract identifies the version it was authored against. Implementations SHOULD accept any minor version within the same major version.

### 9.3 Implementation independence

Core conformance MUST NOT depend on any specific vendor, runtime, marketplace, benchmark, registry, payment processor, or orchestration platform. See [docs/GOVERNANCE.md](docs/GOVERNANCE.md).

---

## 10. Security Considerations

See [SECURITY.md](SECURITY.md). At minimum, implementations using the optional signed-message binding SHOULD:

- enforce a maximum clock skew (suggested 300 seconds)
- track `msg_id` within the skew window to prevent exact replays
- treat task `description` and `input_data` as untrusted content (LLM and shell injection)
- enforce per-party rate limits and payload size limits
- protect long-term signing keys (file permissions, OS keychain, KMS)

---

*This specification is published under the [MIT license](LICENSE). It is intended to remain implementation-neutral.*
