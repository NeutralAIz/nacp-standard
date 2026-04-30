# NACP and A2A — Compatibility Note

**Status:** Informational
**Last reviewed:** 2026-04-30

This document describes how NACP composes with the [Agent2Agent (A2A) protocol](https://a2a-protocol.org/). It is informational — neither protocol depends on the other.

---

## Summary

- NACP **does not compete with A2A.**
- A2A **may be used as an execution or communication transport** for work governed by an NACP contract.
- NACP **may reference A2A** agent metadata, tasks, messages, artifacts, or extensions.
- NACP **may also be used without A2A.**

The two protocols solve different problems and cleanly compose:

| Protocol | What it covers |
|---|---|
| **A2A** | Communication and task exchange between agents. Defines agent cards, tasks, messages, artifacts, and parts. |
| **NACP** | Agreement and accountability. Defines the contract, lifecycle, evidence, audit events, and settlement metadata around delegated work. |

A2A handles *how the work is communicated*. NACP handles *what was agreed, by whom, under what terms, with what evidence, and how it was settled*.

---

## How NACP references A2A

A NACP contract can name A2A as its `execution_transport` and carry pointers to the relevant A2A entities:

```json
{
  "contract_id": "contract_123",
  "execution_transport": "a2a",
  "execution_refs": {
    "agent_card_url": "https://example.com/.well-known/agent-card.json",
    "task_id": "task_456",
    "message_ids": ["msg_1", "msg_2"],
    "artifact_ids": ["artifact_1"]
  }
}
```

Recommended fields under `execution_refs` when `execution_transport == "a2a"`:

| Field | Description |
|---|---|
| `agent_card_url` | URL to the provider's A2A agent card (typically `/.well-known/agent-card.json`). |
| `task_id` | A2A task identifier the contract maps to. |
| `message_ids` | Optional list of A2A message identifiers exchanged for this task. |
| `artifact_ids` | Optional list of A2A artifact identifiers produced for this task. |
| `extension_uris` | Optional list of A2A extension URIs in use on this exchange. |

Implementations MAY add further A2A-specific keys; these SHOULD be namespaced (e.g. `a2a.skill_id`).

---

## Mapping at a glance

| A2A concept | NACP concept |
|---|---|
| Agent card | Identity reference (`requester` / `provider`) |
| Task | A unit of work referenced by `execution_refs.task_id` |
| Message | Communication referenced by `execution_refs.message_ids` |
| Artifact | Evidence referenced by `evidence` or `execution_refs.artifact_ids` |
| Skills (on agent card) | May inform `task_category` selection |

NACP does not require any specific A2A version, transport, or extension.

---

## Lifecycle interaction

The A2A task lifecycle and the NACP contract lifecycle are independent but related. A typical mapping:

| NACP `lifecycle_status` | Typical A2A task state |
|---|---|
| `proposed` | (no A2A task yet, or `submitted`) |
| `accepted` | `working` (or A2A acceptance equivalent) |
| `in_progress` | `working` |
| `paused` | `input-required` / paused |
| `completed` | `completed` |
| `failed` | `failed` |
| `cancelled` | `canceled` |

The mapping is non-normative; implementations are free to derive their own as long as the contract's `lifecycle_status` remains accurate.

---

## NACP without A2A

NACP is also useful where A2A is not in use — e.g. internal enterprise workflows, queue-based job systems, file-exchange pipelines, or human-in-the-loop processes. In those cases `execution_transport` carries another value (`api`, `queue`, `file`, `human`, or an implementation-namespaced value), and `execution_refs` carries pointers appropriate to that transport. See [TRANSPORT_NEUTRALITY.md](TRANSPORT_NEUTRALITY.md).

---

## A2A without NACP

A2A is independently useful and does not require NACP. NACP is the layer to add when an organization needs an explicit, auditable record of *what was agreed, by whom, under what terms, with what evidence, and how it was settled* — independently of how the work was communicated.
