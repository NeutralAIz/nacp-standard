# NACP Standard — Networked Agent Contract Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Protocol Version](https://img.shields.io/badge/version-1.1.1--draft-orange.svg)](NACP_SPECIFICATION.md)
[![Schemas](https://img.shields.io/badge/schemas-24-blue.svg)](schemas/)
[![MCP Bridge](https://img.shields.io/badge/MCP-bridge_appendix-purple.svg)](MCP_INTEGRATION.md)

> **APIs expose functions. MCP exposes tools and context. NACP coordinates autonomous agents.**

NACP (Networked Agent **Contract** Protocol) is an open standard for networked autonomous agents. It defines the missing agent-to-agent layer: persistent identity, capability discovery, task lifecycle, payment negotiation, P2P signaling, and auditability.

**MCP connects an agent to tools and context. NACP connects agents to each other.**

---

## What's new in 1.1.1-draft

- **§5.1 split** — `5.1.a` keeps the envelope-in-body / `X-NACP-Signature` pattern. `5.1.b` (new) defines the `X-NACP-Auth` action-envelope pattern for state-changing REST calls (GET/DELETE/PUT) where the body has nowhere to carry a signature. Implementations advertise their action set at `.well-known/nacp.auth.action_registry`.
- **§5.2 expanded** — formalises the WebSocket relay protocol: auth frame, response frames (`AUTH_OK`, `RELAY`), and explicit close codes (4400 / 4401 / 4403).
- **§5.4 new — REST error envelope** — `{error_code, error_message, error_detail, request_id}` mandatory on every non-2xx response. Distinct from the inter-agent ERROR envelope of §3.7.
- **Error codes added** — `NACP-402` (payment required) and `NACP-422` (REST body validation).
- **3 new schemas** — `auth_action.schema.json`, `rest_error.schema.json`, `ws_relay_frame.schema.json`.
- **MCP integration appendix** — informational appendix `MCP_INTEGRATION.md` standardising the canonical NACP↔MCP bridge mapping (tool naming `nacp_*`, resource scheme `nacp://`, error mapping). Becomes normative in 1.2 once a second implementation lands.

---

## Key Features (v1.1.1)

- **Signed Identity** — Every message is signed with Ed25519 for non-repudiation
- **REST Action Envelopes** — `X-NACP-Auth` pattern for authenticating state-changing REST calls without a body to sign
- **Task Lifecycle** — Full state machine for task delegation and tracking (11 message types)
- **Agent Economy** — Built-in payment negotiation supporting Crypto, Escrow, and Credits
- **P2P Signaling** — WebRTC-style signaling for direct agent-to-agent handoffs
- **WebSocket Relay** — Sub-100ms push delivery with documented frame schemas + close codes
- **Zero-Trust Security** — End-to-end encrypted P2P channels after initial discovery
- **Unified REST Errors** — One envelope shape across every non-2xx response
- **MCP Bridge** — Canonical mapping for LLM-host integration (Claude Desktop, Cursor, Windsurf, Continue, Cody, custom apps)
- **24 JSON Schemas** — Formal validation for every protocol message type + auth + error + WS frames

---

## When to Use NACP

Use NACP when:
- Multiple independent agents need to discover each other
- Agents need to negotiate and verify payments for services
- Agents need signed identity and auditable provenance
- Agents delegate work and expect progress/result messages
- Agents run behind NAT/firewalls and need relay/signaling support
- You need a common contract for benchmarking, scoring, or evolving agent systems
- You want LLM hosts (Claude Desktop, Cursor, …) to drive autonomous agents through the [MCP bridge](MCP_INTEGRATION.md)

---

## Protocol at a Glance

| Aspect | Detail |
|--------|--------|
| **Name** | Networked Agent Contract Protocol (NACP) |
| **Version** | 1.1.1-draft |
| **Message format** | Signed JSON envelope (Ed25519) |
| **Message types** | 25 types across 7 categories |
| **REST authentication** | Envelope-in-body (§5.1.a) + `X-NACP-Auth` action envelopes (§5.1.b) |
| **REST error envelope** | `{error_code, error_message, error_detail, request_id}` (§5.4) |
| **Payment** | Crypto, Escrow, Credit, Free |
| **Signaling** | WebRTC-style ICE/SDP exchange |
| **WebSocket relay** | `AUTH_OK` / `RELAY` frames + 4400 / 4401 / 4403 close codes (§5.2.b) |
| **Encryption** | X25519 + XSalsa20-Poly1305 (NaCl) |
| **LLM integration** | [MCP bridge appendix](MCP_INTEGRATION.md) (informational; → normative in 1.2) |

### Message Categories

| Category | Types | Purpose |
|----------|-------|---------|
| Health | PING, PONG, HEARTBEAT | Liveness and monitoring |
| Discovery | DISCOVER, SKILL_QUERY, SKILL_RESPONSE | Capability discovery |
| Task Lifecycle | TASK_ASSIGN, TASK_ACCEPT, TASK_REJECT, TASK_PROGRESS, TASK_RESULT, TASK_CANCEL, TASK_CANCELLED, TASK_STATUS_QUERY, TASK_STATUS_RESPONSE, TASK_PAUSE, TASK_RESUME | Task delegation |
| Payment | Integrated in Task messages | Negotiation and verification |
| P2P Signaling | SIGNALING_ICE, SIGNALING_SDP, SIGNALING_PEER | WebRTC-style handoff |
| Crypto | HANDSHAKE_INIT, HANDSHAKE_ACK, CHANNEL_OPEN, CHANNEL_CLOSE | Encrypted channels |
| Control | ERROR | Error reporting |

Plus the auxiliary `AUTH_ACTION` envelope (§5.1.b) used in the
`X-NACP-Auth` header — not a wire message type, but defined by the
spec and shipped as `schemas/auth_action.schema.json`.

---

## Repository Contents

```
nacp-standard/
├── NACP_SPECIFICATION.md      # Full protocol specification (v1.1.1-draft)
├── MCP_INTEGRATION.md          # Informational appendix — NACP ↔ MCP bridge mapping
├── README.md                   # This file
├── SECURITY.md                 # Security model and guidelines
├── LICENSE                     # MIT License
├── schemas/                    # JSON Schema files (24 schemas)
│   ├── envelope.schema.json     # Base message envelope
│   ├── auth_action.schema.json  # X-NACP-Auth header envelope (§5.1.b)
│   ├── rest_error.schema.json   # REST API error envelope (§5.4)
│   ├── ws_relay_frame.schema.json  # WebSocket relay frames (§5.2.b)
│   ├── error.schema.json        # Inter-agent ERROR payload (§3.7)
│   ├── payment.schema.json      # Payment metadata
│   ├── signaling.schema.json    # P2P signaling
│   ├── skill.schema.json        # Skill definition
│   ├── task_assign.schema.json  # Task assignment
│   ├── task_result.schema.json  # Task result
│   └── ... (see schemas/ directory)
```

---

## Quick Start

### Read the Spec

The full protocol specification is in [`NACP_SPECIFICATION.md`](NACP_SPECIFICATION.md). It covers:

1. Message envelope format and field definitions
2. All 25 message types with payload schemas
3. Canonical JSON serialization for signature verification
4. Transport modes (REST §5.1.a/§5.1.b, WebSocket §5.2.a/§5.2.b, Relay §5.3)
5. REST error envelope (§5.4)
6. Cryptographic handshake and key derivation
7. Payment negotiation fields
8. P2P signaling flow
9. Versioning policy

For LLM-host integration, see [`MCP_INTEGRATION.md`](MCP_INTEGRATION.md) — the canonical mapping for NACP↔MCP bridges (tool naming, resource scheme, identity model, error mapping).

### Validate Messages

JSON Schema files in `schemas/` can be used to validate any NACP message:

```python
import json
from jsonschema import validate

with open("schemas/envelope.schema.json") as f:
    envelope_schema = json.load(f)

with open("schemas/task_assign.schema.json") as f:
    task_assign_schema = json.load(f)

# Validate a message envelope
validate(instance=message, schema=envelope_schema)
```

### Implement an Agent

At minimum, an NACP-compatible agent must:

1. **Generate an Ed25519 keypair** for persistent identity
2. **Register** with a liaison service (or directly with another agent)
3. **Sign all outgoing messages** using canonical JSON serialization
4. **Authenticate state-changing REST calls** via `X-NACP-Auth` action envelopes (§5.1.b)
5. **Handle the task lifecycle**: TASK_ASSIGN → TASK_ACCEPT/TASK_REJECT → TASK_RESULT
6. **Respond to PING** with PONG for health monitoring
7. **Honour the REST error envelope** (§5.4) on all non-2xx responses

### Reference Implementation

[NeutralAiz Hub v1.6.0](https://github.com/NeutralAIz/neutralaizhub) is a reference NACP-conformant liaison + scoring + tournament platform. It ships:

- All 1.1.1 features (action envelopes, REST error envelope, WS frames)
- An MCP bridge (`nacp/mcp_server.py`) implementing the `MCP_INTEGRATION.md` appendix
- 182 passing tests covering identity, error envelopes, cursor pagination, and more

---

## Contributing

NACP is an open standard. Contributions, proposals, and feedback are welcome via GitHub Issues and Pull Requests.

---

## License

[MIT](LICENSE) — © 2026 NeutralAIz Inc.
