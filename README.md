# NACP Standard — Networked Agent Contract Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Protocol Version](https://img.shields.io/badge/version-1.1.1--draft-orange.svg)](NACP_SPECIFICATION.md)
[![Status](https://img.shields.io/badge/status-open_protocol-green.svg)](docs/GOVERNANCE.md)

> **NACP is a transport-neutral contract protocol for autonomous agent work.** It defines the agreement and accountability envelope around delegated tasks: identity, terms, lifecycle, execution references, evidence, auditability, and settlement metadata.

NACP (Networked Agent **Contract** Protocol) is an open, vendor-neutral standard for expressing structured contracts between autonomous agents, agent-capable services, and any system that delegates or performs delegated work. It is implementation-neutral and transport-neutral: it does not require any specific runtime, registry, marketplace, broker, payment processor, benchmark suite, or framework.

---

## What NACP Is

NACP is an open protocol for expressing structured contracts between autonomous agents, agent-capable services, and systems that delegate or perform work.

An NACP contract can define:

- who is requesting work
- who accepts responsibility for the work
- what category or type of work is requested
- where the detailed task payload lives
- which execution transport or tool system is being used
- when the work is due
- what output or evidence is required
- how lifecycle updates are reported
- how cost, payment intent, credits, receipts, or settlement references are represented
- how results, failures, disputes, and audit events are recorded

NACP defines the *contract and accountability envelope* around the work. The work itself can be performed through any transport — A2A, MCP-enabled tools, direct APIs, queues, peer-to-peer channels, file exchange, or future protocols.

---

## What NACP Is Not

NACP is not:

- a replacement for A2A
- a replacement for MCP
- a payment processor or payment rail
- a marketplace
- a scoring platform
- a benchmark suite
- a tournament system
- a proprietary platform protocol
- a requirement to use any specific vendor, registry, broker, runtime, transport, or agent framework

NACP may be implemented by any agent runtime, enterprise workflow, broker, registry, direct peer-to-peer network, orchestration system, marketplace, evaluation system, or custom agent platform. Product-specific behavior belongs in optional, namespaced extension fields — see [docs/GOVERNANCE.md](docs/GOVERNANCE.md).

---

## How NACP Relates to Other Layers

| Layer | Purpose | Relationship to NACP |
|---|---|---|
| **API** | Exposes application functions | NACP may reference API requests or results as execution details |
| **MCP** | Exposes tools and context to agents or LLM applications | NACP may reference MCP tool use but does not replace MCP |
| **A2A** | Enables agent-to-agent communication and task exchange | NACP may wrap or reference A2A tasks, messages, artifacts, or agent metadata |
| **Payment systems** | Authorize, process, or settle payments | NACP may store cost, payment intent, receipts, escrow references, or external settlement references |
| **NACP** | Contract and accountability layer | Defines task terms, lifecycle, evidence, auditability, and settlement metadata |

The short version:

- **A2A** may help agents communicate.
- **MCP** may help agents use tools.
- **Payment systems** may help agents transact.
- **NACP** defines what was agreed, by whom, under what terms, with what lifecycle, what evidence, what audit trail, and what settlement references.

---

## Architecture: Transport-Neutral by Design

NACP is transport-neutral. Detailed task execution may happen through:

- A2A (Agent2Agent) tasks, messages, and artifacts
- MCP-enabled tools
- Direct APIs
- Message queues
- Encrypted peer-to-peer channels
- File exchange
- Shared artifacts
- Human-readable documents
- Custom enterprise systems
- Future protocols

NACP does **not** prescribe how work must be performed. It defines how work is **agreed, tracked, evidenced, audited, and settled**. The detailed task payload may live outside the contract; the contract carries the metadata required to identify the parties, terms, lifecycle, evidence, references, and settlement state.

See [docs/TRANSPORT_NEUTRALITY.md](docs/TRANSPORT_NEUTRALITY.md) for examples of contracts referencing each transport, and [docs/A2A_COMPATIBILITY.md](docs/A2A_COMPATIBILITY.md) for how NACP and A2A compose.

---

## Core Features

- **Persistent agent identity** — Stable, cryptographically verifiable identifiers for parties to a contract
- **Contract envelopes** — Structured agreement records with terms, parties, and lifecycle
- **Task lifecycle** — A neutral state model from request through completion or dispute
- **Execution references** — Pointers into the transport that actually performs the work
- **Evidence references** — Pointers to outputs, artifacts, logs, or other evidence of work performed
- **Audit events** — An append-only record of state changes and notable events
- **Settlement metadata** — References to external payment, escrow, credit, receipt, or settlement systems (NACP does not move money itself)
- **Optional tool/protocol bridges** — Optional integrations with A2A, MCP, and other transports
- **Signed messages** — Optional Ed25519 signing for non-repudiation and audit
- **Dispute state** — Explicit state for failed, contested, or refunded contracts
- **Extension namespaces** — Optional, namespaced extension fields so vendors and domains can extend the protocol without forking it
- **JSON Schemas** — Formal validation of contracts, envelopes, and message payloads

---

## When to Use NACP

Use NACP when you need a common, accountable representation for delegated work — across teams, vendors, runtimes, or transports — and you need to keep an auditable record of what was agreed and what happened. Typical signals:

- You delegate work to autonomous agents and need a record of the agreement
- Multiple parties need a shared lifecycle and audit trail
- You need to attach evidence, settlement references, or dispute state to work
- You want a transport-agnostic agreement layer that can sit above A2A, MCP, direct APIs, or your own runtime
- You need to compose work across runtimes without coupling to any single platform

---

## Repository Contents

```
nacp-standard/
├── NACP_SPECIFICATION.md       # Full protocol specification
├── README.md                    # This file
├── SECURITY.md                  # Security model and guidelines
├── LICENSE                      # MIT License
├── docs/
│   ├── A2A_COMPATIBILITY.md     # How NACP composes with A2A
│   ├── TRANSPORT_NEUTRALITY.md  # Examples across transports
│   ├── MCP_INTEGRATION.md       # Optional MCP bridge guidance
│   └── GOVERNANCE.md            # Open-standard / implementation-neutral note
├── schemas/                     # JSON Schemas
│   ├── contract.schema.json     # Core neutral contract envelope
│   ├── envelope.schema.json     # Signed message envelope (optional binding)
│   ├── audit_event.schema.json  # Audit event record
│   ├── settlement.schema.json   # Settlement metadata
│   └── ... (additional schemas)
└── examples/                    # Neutral, vendor-free examples
    ├── contract_over_a2a.json
    ├── contract_over_mcp.json
    ├── contract_over_direct_api.json
    ├── contract_with_artifact_evidence.json
    ├── contract_completed_audit.json
    ├── contract_failed_dispute.json
    └── contract_settlement_external.json
```

> The earlier `MCP_INTEGRATION.md` appendix has moved to `docs/MCP_INTEGRATION.md` and been re-scoped as optional, non-normative bridge guidance.

---

## Quick Start

### Read the specification

The full protocol specification is in [`NACP_SPECIFICATION.md`](NACP_SPECIFICATION.md). It covers:

1. The neutral contract envelope (core)
2. Contract lifecycle and audit events
3. Execution references and evidence references
4. Settlement metadata (references to external systems; NACP does not process payments)
5. Optional signed-message binding (Ed25519 envelopes for inter-agent messaging)
6. Optional REST and WebSocket bindings
7. Extension namespaces and versioning

### Validate contracts and messages

JSON Schemas in `schemas/` can be used to validate any NACP contract or message:

```python
import json
from jsonschema import validate

with open("schemas/contract.schema.json") as f:
    contract_schema = json.load(f)

validate(instance=contract, schema=contract_schema)
```

### Implement NACP

A minimal NACP-compatible implementation:

1. **Represents contracts** using the neutral fields defined in `schemas/contract.schema.json`
2. **Records lifecycle transitions** as audit events
3. **References execution** through `execution_transport` and `execution_refs` rather than embedding all task data
4. **References evidence** by pointer (URL, content ID, artifact ID) rather than inlining large payloads
5. **References settlement** by pointer to external payment, escrow, or receipt systems
6. **Uses extension namespaces** for product-specific or domain-specific fields

Optional additions — adopt the pieces that fit your environment:

- Sign messages with Ed25519 for non-repudiation (see optional message-binding section in the spec)
- Expose contracts and audit events over REST or WebSocket transports
- Bridge to A2A, MCP, or another transport for execution

### Implementation independence

NACP is intentionally **not** tied to any specific implementation. Any conformant implementation — open source, commercial, in-house, or experimental — is welcome. Implementations should clearly distinguish **core** behavior (the neutral contract layer) from **optional extensions** (namespaced extension fields, transport-specific bindings, product-specific features). See [docs/GOVERNANCE.md](docs/GOVERNANCE.md).

---

## Contributing

NACP is an open standard. Contributions, proposals, and feedback are welcome via GitHub Issues and Pull Requests. Vendor-specific or product-specific behavior should be proposed as namespaced extensions rather than as changes to the core.

---

## License

[MIT](LICENSE) — see `LICENSE` for the full text.
