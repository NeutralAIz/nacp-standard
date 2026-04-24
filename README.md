# NACP Standard — Networked Agent Contract Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Protocol Version](https://img.shields.io/badge/version-1.1.0--draft-orange.svg)](NACP_SPECIFICATION.md)
[![Schemas](https://img.shields.io/badge/schemas-21-blue.svg)](schemas/)

> **APIs expose functions. MCP exposes tools and context. NACP coordinates autonomous agents.**

NACP (Networked Agent **Contract** Protocol) is an open standard for networked autonomous agents. It defines the missing agent-to-agent layer: persistent identity, capability discovery, task lifecycle, payment negotiation, P2P signaling, and auditability.

**MCP connects an agent to tools and context. NACP connects agents to each other.**

---

## Key Features (v1.1.0)

- **Signed Identity** — Every message is signed with Ed25519 for non-repudiation
- **Task Lifecycle** — Full state machine for task delegation and tracking (11 message types)
- **Agent Economy** — Built-in payment negotiation supporting Crypto, Escrow, and Credits
- **P2P Signaling** — WebRTC-style signaling for direct agent-to-agent handoffs
- **Zero-Trust Security** — End-to-end encrypted P2P channels after initial discovery
- **21 JSON Schemas** — Formal message validation for every protocol message type

---

## When to Use NACP

Use NACP when:
- Multiple independent agents need to discover each other
- Agents need to negotiate and verify payments for services
- Agents need signed identity and auditable provenance
- Agents delegate work and expect progress/result messages
- Agents run behind NAT/firewalls and need relay/signaling support
- You need a common contract for benchmarking, scoring, or evolving agent systems

---

## Protocol at a Glance

| Aspect | Detail |
|--------|--------|
| **Name** | Networked Agent Contract Protocol (NACP) |
| **Version** | 1.1.0-draft |
| **Message format** | Signed JSON envelope (Ed25519) |
| **Message types** | 25 types across 7 categories |
| **Payment** | Crypto, Escrow, Credit, Free |
| **Signaling** | WebRTC-style ICE/SDP exchange |
| **Encryption** | X25519 + XSalsa20-Poly1305 (NaCl) |

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

---

## Repository Contents

```
nacp-standard/
├── NACP_SPECIFICATION.md      # Full protocol specification (v1.1.0-draft)
├── README.md                   # This file
├── SECURITY.md                 # Security model and guidelines
├── LICENSE                     # MIT License
├── schemas/                    # JSON Schema files (21 schemas)
│   ├── envelope.schema.json    # Base message envelope
│   ├── payment.schema.json     # Payment metadata
│   ├── signaling.schema.json   # P2P signaling
│   ├── skill.schema.json       # Skill definition
│   ├── task_assign.schema.json # Task assignment
│   ├── task_result.schema.json # Task result
│   └── ... (see schemas/ directory)
```

---

## Quick Start

### Read the Spec

The full protocol specification is in [`NACP_SPECIFICATION.md`](NACP_SPECIFICATION.md). It covers:

1. Message envelope format and field definitions
2. All 25 message types with payload schemas
3. Canonical JSON serialization for signature verification
4. Transport modes (REST, WebSocket, Relay)
5. Cryptographic handshake and key derivation
6. Payment negotiation fields
7. P2P signaling flow
8. Versioning policy

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
4. **Handle the task lifecycle**: TASK_ASSIGN → TASK_ACCEPT/TASK_REJECT → TASK_RESULT
5. **Respond to PING** with PONG for health monitoring

---

## Contributing

NACP is an open standard. Contributions, proposals, and feedback are welcome via GitHub Issues and Pull Requests.

---

## License

[MIT](LICENSE) — © 2026 NeutralAIz Inc.
