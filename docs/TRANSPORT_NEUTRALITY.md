# Transport Neutrality

**Status:** Informational
**Last reviewed:** 2026-04-30

NACP contracts are transport-neutral. The detailed task payload may live outside the contract; the contract itself carries the metadata required to identify the parties, terms, lifecycle, evidence, references, and settlement state.

This document collects example contracts that reference different execution transports. Each example focuses on the relevant fields; full contracts include identity references, lifecycle, audit events, and (optionally) settlement metadata. See `examples/` for fuller, runnable examples.

---

## Why transport neutrality

A contract is a record of *what was agreed*. The work itself can be performed:

- through agent-to-agent messaging (A2A)
- through tool calls (MCP-enabled tools)
- through direct API calls
- through queues
- through encrypted peer-to-peer channels
- through file or artifact exchange
- through human-driven processes
- through a custom enterprise system
- through a future protocol that does not exist yet

NACP should be usable across all of these without privileging any one transport.

The contract layer keeps the **agreement**. The transport layer keeps the **execution**. The contract carries pointers — `execution_transport` plus `execution_refs` — that tie the two together.

---

## Example: Contract referencing an A2A task

```json
{
  "contract_id": "contract_a2a_001",
  "contract_type": "delegated_task",
  "protocol_version": "1.1",
  "requester": { "id": "did:example:requester", "id_type": "did" },
  "provider": { "id": "did:example:provider", "id_type": "did" },
  "task_category": "code_review",
  "task_summary": "Review PR #482 for security issues.",
  "execution_transport": "a2a",
  "execution_refs": {
    "agent_card_url": "https://example.com/.well-known/agent-card.json",
    "task_id": "task_456",
    "message_ids": ["msg_1", "msg_2"],
    "artifact_ids": ["artifact_1"]
  },
  "lifecycle_status": "in_progress"
}
```

See [A2A_COMPATIBILITY.md](A2A_COMPATIBILITY.md) for details.

---

## Example: Contract referencing MCP tool execution

```json
{
  "contract_id": "contract_mcp_001",
  "contract_type": "delegated_task",
  "protocol_version": "1.1",
  "requester": { "id": "did:example:llm_host", "id_type": "did" },
  "provider": { "id": "did:example:tool_provider", "id_type": "did" },
  "task_category": "data_extraction",
  "task_summary": "Extract product details from supplied URLs.",
  "execution_transport": "mcp",
  "execution_refs": {
    "server_uri": "stdio://example-mcp-server",
    "tool_name": "scrape_products",
    "tool_call_ids": ["call_abc", "call_def"]
  },
  "evidence_requirements": { "format": "json", "schema_uri": "https://example.com/schemas/products.json" },
  "lifecycle_status": "completed"
}
```

NACP does not replace MCP; it references MCP tool calls as execution metadata. See [MCP_INTEGRATION.md](MCP_INTEGRATION.md).

---

## Example: Contract referencing a direct API job

```json
{
  "contract_id": "contract_api_001",
  "contract_type": "delegated_task",
  "protocol_version": "1.1",
  "requester": { "id": "https://requester.example.com", "id_type": "url" },
  "provider": { "id": "https://provider.example.com", "id_type": "url" },
  "task_category": "transcription",
  "task_summary": "Transcribe attached audio file.",
  "execution_transport": "api",
  "execution_refs": {
    "endpoint": "https://provider.example.com/api/v1/jobs",
    "job_id": "job_789",
    "request_id": "req_012"
  },
  "deadline_at": "2026-05-01T12:00:00.000000Z",
  "lifecycle_status": "in_progress"
}
```

---

## Example: Contract referencing a file/artifact exchange

```json
{
  "contract_id": "contract_file_001",
  "contract_type": "delegated_task",
  "protocol_version": "1.1",
  "requester": { "id": "uuid:11111111-1111-1111-1111-111111111111", "id_type": "uuid" },
  "provider": { "id": "uuid:22222222-2222-2222-2222-222222222222", "id_type": "uuid" },
  "task_category": "image_classification",
  "task_summary": "Classify the supplied image set.",
  "execution_transport": "file",
  "execution_refs": {
    "input_uri": "s3://bucket/inputs/2026-04-30/job.json",
    "output_uri": "s3://bucket/outputs/2026-04-30/job.json",
    "content_hash": "sha256:abc..."
  },
  "evidence_requirements": {
    "kinds": ["artifact", "signed_receipt"]
  },
  "lifecycle_status": "completed"
}
```

---

## Example: Contract over a custom transport

```json
{
  "contract_id": "contract_custom_001",
  "contract_type": "delegated_task",
  "protocol_version": "1.1",
  "requester": { "id": "did:example:enterprise", "id_type": "did" },
  "provider": { "id": "did:example:internal_agent", "id_type": "did" },
  "task_category": "report_generation",
  "execution_transport": "acme.queue",
  "execution_refs": {
    "queue": "acme://reports/q1",
    "job_id": "j_01HK..."
  },
  "lifecycle_status": "accepted"
}
```

Implementation-specific transports SHOULD be namespaced (`acme.queue`, `acme.workflow`). The neutral set (`a2a`, `mcp`, `api`, `queue`, `p2p`, `file`, `human`) is reserved for the spec.

---

## What NACP does *not* do here

- It does not specify the wire protocol of the underlying transport.
- It does not require the underlying transport to be aware of NACP.
- It does not embed the full task payload — `task_payload_ref` carries a pointer instead.
- It does not move money — `settlement_reference` carries a pointer to whatever external system actually settled the contract.
