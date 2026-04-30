# NACP and MCP — Optional Integration Note

**Status:** Informational, optional
**Last reviewed:** 2026-04-30

This document describes how an NACP implementation MAY bridge to the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). It is non-normative — MCP support is optional and is not required for NACP conformance.

---

## Summary

- NACP **does not replace MCP.**
- NACP **does not require MCP.**
- An NACP contract **MAY reference MCP tool calls or tool outputs** as execution or evidence references.
- An MCP server **MAY expose** an NACP implementation's read-only resources and state-changing actions as MCP resources and tools, allowing MCP-compatible LLM hosts to drive NACP-aware agents.

NACP and MCP solve adjacent problems:

| Protocol | What it covers |
|---|---|
| **MCP** | Exposes tools, resources, and context to LLM applications. |
| **NACP** | Defines the contract, lifecycle, evidence, audit, and settlement metadata around delegated agent work. |

The two compose: an LLM host can drive an NACP-aware agent through an MCP bridge, and an NACP contract can reference MCP tool calls as the execution mechanism for the work.

---

## When to bridge

Bridge NACP to MCP when:

- An LLM host (or any MCP client) needs to drive an NACP-aware agent and you want to expose the agent's behavior through MCP tools.
- An NACP contract should record MCP tool calls or tool outputs as evidence that work was performed.

Do **not** bridge when:

- The MCP host can talk to the underlying transport directly without needing NACP semantics.
- You only need NACP for the contract layer; the work itself is performed through a non-MCP transport (A2A, direct API, queue, file exchange). In that case, NACP records pointers to that transport in `execution_refs`.

---

## Architectural pattern

```
┌───────────────────────────────┐
│  MCP-compatible host          │  (LLM application)
└────────────────┬─────────────┘
                 │ JSON-RPC 2.0 (stdio or SSE)
                 ▼
┌───────────────────────────────┐
│  NACP ↔ MCP bridge            │  optional
│  - holds the agent's          │  one process per
│    signing key                │  NACP agent identity
│  - exposes the NACP           │
│    surface as MCP tools       │
│    and resources              │
└────────────────┬─────────────┘
                 │ NACP REST / WS / direct
                 ▼
┌───────────────────────────────┐
│  NACP-conformant system       │
└───────────────────────────────┘
```

**One bridge process = one NACP identity.** Hosts that need to drive multiple NACP agents SHOULD run multiple bridge processes.

---

## Tool naming convention

If you build an NACP ↔ MCP bridge, prefix MCP tool names with `nacp_` to avoid collisions with non-NACP tools registered in the same host. Sub-prefixes by subsystem are RECOMMENDED for catalogs larger than ~25 tools (e.g. `nacp_task_*`, `nacp_contract_*`).

The set of tools a bridge exposes is **implementation-defined**. The neutral surface area NACP itself defines is the contract layer; tool names follow the implementation's REST or RPC surface. A bridge is conformant to *this appendix* if it follows the prefixing convention and the resource/identity/error mapping below — not if it ships any specific catalog.

---

## Resource URI scheme

Read-only data exposed as MCP resources SHOULD use the `nacp://` URI scheme, with paths mirroring the implementation's read-only endpoints, e.g.:

```
nacp://contracts/{contract_id}
nacp://contracts/{contract_id}/audit
nacp://agents
nacp://agents/{id}
```

LLMs read these via `resources/read` instead of calling a tool — significantly more token-efficient for browsing.

---

## Identity model

A bridge MUST persist its NACP identity across restarts. Recommended:

1. Long-term signing key (e.g. Ed25519) in a file pointed to by an environment variable.
2. Implementation-assigned identifier cached locally, keyed by implementation URL + key fingerprint.
3. Auto-register on first connect; on conflict (e.g. same name, different key), exit loudly rather than silently registering a parallel agent.

A bridge MUST refuse to operate when a cached identifier does not match the loaded key — this prevents silently using a stale identifier for the wrong key.

---

## Authentication

If the underlying NACP implementation uses the optional REST binding (§8.2 of the spec), state-changing tool calls from the bridge SHOULD use the `X-NACP-Auth` action-envelope pattern. The bridge holds the signing key; the LLM never sees it. The bridge MAY look up actions at `.well-known/nacp.auth.action_registry` to avoid hard-coding implementation-specific action names.

---

## Error mapping (HTTP / NACP → JSON-RPC)

Recommended mapping when the underlying NACP implementation returns the unified REST error envelope (§8.2.c):

| HTTP | JSON-RPC | Application code | Notes |
|------|----------|------------------|-------|
| 400 | `-32602` | `invalid_params` | Surface `error_detail.errors`. |
| 401 | application | `-32001` `unauthorized` | Hint to re-auth. |
| 402 | application | `-32002` `settlement_required` | Surface external-settlement detail. |
| 403 | application | `-32003` `forbidden` | Surface action mismatch. |
| 404 | application | `-32004` `not_found` | |
| 409 | application | `-32005` `conflict` | Include `valid_next_states` for lifecycle conflicts. |
| 413 | `-32602` | `payload_too_large` | Advertise `max_payload_bytes`. |
| 422 | `-32602` | `validation` | |
| 429 | application | `-32006` `rate_limited` | Honour `Retry-After`. |
| 5xx | `-32603` | `internal` | |

Bridges SHOULD forward `request_id` from the NACP error envelope to the JSON-RPC error payload so users can correlate with implementation logs.

---

## Recording MCP execution in an NACP contract

When an NACP contract is fulfilled through MCP tool calls, the contract SHOULD reference them through `execution_refs`:

```json
{
  "execution_transport": "mcp",
  "execution_refs": {
    "server_uri": "stdio://example-mcp-server",
    "tool_name": "scrape_products",
    "tool_call_ids": ["call_abc", "call_def"]
  }
}
```

Tool outputs MAY also appear as `evidence` entries:

```json
{
  "evidence": [
    {
      "kind": "tool_call_log",
      "transport": "mcp",
      "call_ids": ["call_abc", "call_def"],
      "uri": "https://example.com/logs/r_001"
    }
  ]
}
```

---

## Out of scope

- WebSocket relay → MCP notifications: not yet specified.
- MCP prompts: an MCP-side concern, not an NACP concern.
- Multi-identity multiplexing within a single bridge process.
- Encrypted key stores (file permissions, OS keychain, KMS): implementation concerns.

---

## Independence

This appendix is informational. NACP does not require any MCP bridge, and an MCP bridge does not need to follow this appendix to be useful. The conventions above exist so that multiple independent NACP↔MCP bridges remain interoperable.
