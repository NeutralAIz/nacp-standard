# NACP — Networked Agent Contract Protocol

**Version:** 1.1.1-draft  
**Status:** Draft (1.1.1 adds AUTH_ACTION header pattern, REST error envelope, expanded WebSocket protocol)  
**Last Reviewed:** 2026-04-30  
**Maintainers:** NeutralAIz Inc.

---

> **NACP is not a transport protocol and not a tool protocol. It is a contract protocol for autonomous agents.** It defines the semantic obligations agents agree to when they discover, trust, delegate to, evaluate, and communicate with each other.
>
> **APIs expose functions. MCP exposes tools and context. NACP coordinates autonomous agents.**

---

## 1. Purpose

NACP (Networked Agent **Contract** Protocol) is a standardized protocol for autonomous AI agents to discover, authenticate, negotiate capabilities, delegate tasks, and communicate — either directly peer-to-peer or through a liaison (relay) service.

Use NACP when:
- Multiple independent agents need to discover each other
- Agents are implemented in different frameworks or languages
- Agents need signed identity and auditable provenance
- Agents delegate work and expect progress/result messages
- Agents run behind NAT/firewalls and need relay support
- A benchmark/scoring/evolution system needs a common contract
- **Agents need to negotiate and verify payments for services**

---

## 2. Message Envelope

Every NACP message is a signed JSON envelope:

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

---

## 3. Message Types

NACP defines 25 message types across 7 categories:

### 3.1 Health (3 types)

| Type | Direction | Payload |
|------|-----------|---------|
| `PING` | Any → Any | `{latency_ns, metadata}` |
| `PONG` | Any → Any | `{latency_ns, metadata}` |
| `HEARTBEAT` | Agent → Liaison | `{status, active_tasks, load_percent, uptime_seconds}` |

### 3.2 Discovery (3 types)

| Type | Direction | Payload |
|------|-----------|---------|
| `DISCOVER` | Agent → Liaison | `{skill_name, protocols[], transport[], min_status, max_results}` |
| `SKILL_QUERY` | Agent → Agent | `{query}` (natural language) |
| `SKILL_RESPONSE` | Agent → Agent | `{skills[], protocols[], interfaces[]}` |

### 3.3 Task Lifecycle (11 types)

| Type | Direction | Payload |
|------|-----------|---------|
| `TASK_ASSIGN` | Initiator → Executor | `{task_id, skill, description, input_data, deadline, priority, payment}` |
| `TASK_ACCEPT` | Executor → Initiator | `{task_id, estimated_duration_ms, payment_ack}` |
| `TASK_REJECT` | Executor → Initiator | `{task_id, reason, message}` |
| `TASK_PROGRESS` | Executor → Initiator | `{task_id, progress_percent, status_message}` |
| `TASK_RESULT` | Executor → Initiator | `{task_id, status, result, execution_time_ms, tokens_used, payment_final}` |
| `TASK_CANCEL` | Initiator → Executor | `{task_id, reason}` |
| `TASK_CANCELLED` | Executor → Initiator | `{task_id, status_at_cancellation, partial_result}` |
| `TASK_STATUS_QUERY` | Any → Executor | `{task_id}` |
| `TASK_STATUS_RESPONSE` | Executor → Any | `{task_id, status, progress_percent}` |
| `TASK_PAUSE` | Initiator → Executor | `{task_id, reason}` |
| `TASK_RESUME` | Initiator → Executor | `{task_id}` |

### 3.4 Payment (New in 1.1)

NACP supports an "Economy of Agents" via structured payment placeholders.

| Field | Description |
|-------|-------------|
| `payment_method` | `crypto`, `escrow`, `credit`, `free` |
| `currency` | `USDC`, `ETH`, `SOL`, `CREDIT` |
| `amount` | String-encoded decimal (e.g., `"0.005"`) |
| `transaction_id` | Optional hash or reference to external settlement |

**Example TASK_ASSIGN with Payment:**
```json
{
  "payload": {
    "task_id": "...",
    "skill": "code_analysis",
    "payment": {
      "method": "crypto",
      "currency": "USDC",
      "amount": "0.10",
      "strategy": "post-pay"
    }
  }
}
```

### 3.5 P2P Signaling (New in 1.1)

Facilitates the WebRTC-style "handoff" from Liaison to direct P2P connection.

| Type | Direction | Payload |
|------|-----------|---------|
| `SIGNALING_ICE` | A ↔ B | `{candidate, sdp_mid, sdp_mindex}` |
| `SIGNALING_SDP` | A ↔ B | `{type: "offer"\|"answer", sdp}` |
| `SIGNALING_PEER` | Liaison → Agent | `{peer_id, direct_endpoint, transport_hint}` |

### 3.6 Crypto (4 types)

| Type | Direction | Payload |
|------|-----------|---------|
| `HANDSHAKE_INIT` | A → B | `{ed25519_public_key, x25519_ephemeral_public}` |
| `HANDSHAKE_ACK` | B → A | `{ed25519_public_key, x25519_ephemeral_public}` |
| `CHANNEL_OPEN` | A → B | `{session_id, cipher}` |
| `CHANNEL_CLOSE` | Either | `{session_id, reason}` |

### 3.7 Control (1 type)

| Type | Direction | Payload |
|------|-----------|---------|
| `ERROR` | Any → Any | `{error_code, message, details}` |

**Error codes:**

| Code | Meaning |
|------|---------|
| `NACP-400` | Malformed message |
| `NACP-401` | Invalid or missing signature |
| `NACP-402` | Payment required (insufficient credits / escrow refused) |
| `NACP-403` | Unauthorized agent |
| `NACP-404` | Agent/task/skill not found |
| `NACP-408` | Timeout |
| `NACP-409` | Conflict (duplicate registration, illegal state transition, etc.) |
| `NACP-413` | Payload too large |
| `NACP-422` | Request body validation failed (REST APIs) |
| `NACP-429` | Rate limited |
| `NACP-500` | Internal server error |
| `NACP-503` | Service unavailable |

---

## 4. Canonical JSON Serialization

Signature verification depends on deterministic serialization. All implementations MUST use this canonical form:

1. **Encoding:** UTF-8
2. **Serialization:** `json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`
3. **Signature field exclusion:** The `signature` field is REMOVED from the envelope dict before computing the canonical form. The signature is computed over `{"version":"1.0","msg_id":"...","timestamp":"...","type":"...","from":"...","to":"...","payload":{...}}` (no `signature` key present).
4. **Optional fields:** Missing optional fields are OMITTED entirely, NOT set to `null`.
5. **Timestamps:** ISO-8601 with microseconds, UTC, using `Z` suffix: `"2026-04-24T12:00:00.000000Z"`
6. **Base64:** Standard base64 encoding (RFC 4648 §4) for Ed25519 signatures — NOT base64url.
7. **Numbers:** No trailing zeros. Use integers when no decimal part (e.g., `5` not `5.0`).
8. **Field order:** `sort_keys=True` ensures alphabetical key ordering.

**Example:**
```python
import json

def canonical_json(envelope: dict) -> str:
    """Compute canonical JSON for signature verification."""
    canonical = {k: v for k, v in envelope.items() if k != "signature"}
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

---

## 5. Transport Modes

NACP supports two REST authentication patterns and a WebSocket fast path.
Both REST patterns coexist; implementations choose per-endpoint based on
whether the request body itself carries an envelope.

### 5.1.a REST — Envelope-in-body (`X-NACP-Signature` optional)

When the request body **is** a NACP envelope (e.g. an inbound message
delivered via `POST /nacp/inbox` or `POST /api/v1/relay`), the signature
travels inside the envelope's `signature` field. Implementations MAY
additionally echo the signature in an `X-NACP-Signature` header for
intermediaries that need to verify without parsing the body.

```
POST /nacp/inbox
X-NACP-Signature: base64-signature   (optional convenience)
Content-Type: application/json

{
  "version": "1.1",
  "msg_id": "...",
  ...
  "signature": "base64-ed25519-signature"
}
```

### 5.1.b REST — Action Envelope (`X-NACP-Auth`, new in 1.1.1)

State-changing endpoints often have **no envelope to put a signature in**
— a `DELETE /api/v1/agents/{id}` has no body; a `PUT
/api/v1/agents/{id}/status` carries a small status string, not a NACP
message; a `GET /api/v1/relay/{id}` is a poll. To authenticate these
calls, the caller wraps a fresh signed envelope of type `AUTH_ACTION`
and sends it in the `X-NACP-Auth` header, base64-encoded.

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
3. Asserts `payload.action` is one of the recognised actions for the
   endpoint.
4. Asserts `payload.agent_id` matches the path-level resource.
5. Verifies the Ed25519 signature against the canonical-JSON form of
   the envelope (signature stripped) and the registered public key of
   `from`.
6. Records `msg_id` for replay protection within the time-skew window.

Implementations **MUST** advertise their full action set at
`.well-known/nacp.auth.action_registry` so agents can discover which
strings to sign. Action names are implementation-namespaced (e.g.
`hub.heartbeat`, `hub.task_create`) — bare names are reserved for the
spec.

Schema: [`schemas/auth_action.schema.json`](schemas/auth_action.schema.json).

### 5.2 WebSocket

NACP defines two WebSocket usage patterns:

#### 5.2.a Inter-agent direct (legacy)

```
ws://host:port/nacp/ws?agent_id=<id>&session_id=<optional>
```

Reserved for direct agent-to-agent connections. Out of scope for 1.1.1.

#### 5.2.b Relay push (new in 1.1.1)

A liaison-mediated WebSocket fast path that delivers inbound envelopes
to an agent in <100ms. Replaces the polling fallback when the agent can
hold an outbound socket open.

```
WS /api/v1/relay/{agent_id}
```

**Authentication frame** (first frame, client → server): a single TEXT
frame containing the JSON of an `AUTH_ACTION` envelope (§5.1.b) with
`payload.action == "ws_relay"`. The server has 10 seconds to receive it
before closing with code 4401.

**Server-sent frames** — see
[`schemas/ws_relay_frame.schema.json`](schemas/ws_relay_frame.schema.json):

- `AUTH_OK`: acknowledgement (`{type: "AUTH_OK", agent_id: "..."}`)
- `RELAY`: inbound envelope (`{type: "RELAY", message: {id, envelope, ...}}`)
  — `message.envelope` is a JSON-encoded string; receivers parse it
  before verifying the signature.

**Close codes:**

| Code | Meaning |
|------|---------|
| `4400` | Bad JSON in auth frame |
| `4401` | Auth timeout (no first frame within 10s) **or** signature verification failed |
| `4403` | `auth.from` or `auth.payload.agent_id` does not match the path `{agent_id}` |

### 5.3 Relay (via Liaison)

Agents behind NAT/firewalls communicate through a liaison (relay) service:

```
POST  /api/v1/relay          # Send relay message (envelope in body, §5.1.a)
GET   /api/v1/relay/{id}     # Poll pending messages (X-NACP-Auth, §5.1.b, action="relay_poll")
WS    /api/v1/relay/{id}     # WebSocket fast path (§5.2.b)
```

> **Scope note.** NACP-conformant liaisons MAY cap relay payload size
> aggressively (e.g. 64 KB) to discourage shuttling agent data through
> the relay. Agents should exchange pointers (presigned URLs, content
> IDs) rather than raw bytes.

### 5.4 REST error envelope (new in 1.1.1)

NACP-conformant REST APIs return non-2xx responses in a unified shape —
distinct from the inter-agent ERROR envelope of §3.7:

```json
{
  "error_code": "NACP-404",
  "error_message": "Agent not found",
  "error_detail": null,
  "request_id": "<X-Request-Id>"
}
```

Schema: [`schemas/rest_error.schema.json`](schemas/rest_error.schema.json).

`error_code` enum extends §3.7 with `NACP-402` (payment required) and
`NACP-422` (body validation). `error_detail` MAY be an object, array,
or null; implementations should put state-machine state, validation
failures, and recovery hints there. `request_id` echoes the
`X-Request-Id` response header for log correlation.

---

## 6. Cryptographic Handshake

### 6.1 Handshake Flow

```
Agent A                    Liaison                    Agent B
  |                          |                          |
  |--- HANDSHAKE_INIT ------>|--- HANDSHAKE_INIT ------>|
  |                          |                          |
  |<-- HANDSHAKE_ACK --------|<-- HANDSHAKE_ACK --------|
  |                          |                          |
  |<-------- Encrypted Channel (XSalsa20-Poly1305) ---->|
```

### 6.2 Key Derivation

1. Both agents generate X25519 ephemeral keypairs
2. Diffie-Hellman shared secret computed
3. BLAKE2b derivation with salt `nacp-v1-key` produces 32-byte symmetric key
4. Encryption via NaCl SecretBox (XSalsa20-Poly1305)

### 6.3 Key Rotation

- Keys rotate every 24 hours or on CHANNEL_CLOSE with `rotate_key: true`
- New handshake required after rotation

---

## 7. Versioning

- **Major:** Breaking changes (field removal, type changes)
- **Minor:** Backward-compatible additions (new message types, new fields)
- **Patch:** Clarifications, documentation fixes

---

*© 2026 NeutralAIz Inc. — MIT License*
