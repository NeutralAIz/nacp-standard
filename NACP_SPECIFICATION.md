# NACP — Networked Agent Contract Protocol

**Version:** 1.1.0-draft  
**Status:** Draft (Updated with Payment & Signaling)  
**Last Reviewed:** 2026-04-24  
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
| `NACP-403` | Unauthorized agent |
| `NACP-404` | Agent/task/skill not found |
| `NACP-408` | Timeout |
| `NACP-409` | Conflict (duplicate registration, etc.) |
| `NACP-413` | Payload too large |
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

### 5.1 REST (HTTP/2)

```
POST /nacp/inbox
X-NACP-Signature: base64-signature
Content-Type: application/json

<envelope>
```

### 5.2 WebSocket

```
ws://host:port/nacp/ws?agent_id=<id>&session_id=<optional>
```

### 5.3 Relay (via Liaison)

Agents behind NAT/firewalls communicate through a liaison (relay) service:

```
POST  /api/v1/relay          # Send relay message
GET   /api/v1/relay/{id}     # Poll pending messages
WS    /api/v1/relay/{id}/ws  # WebSocket relay stream
```

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
