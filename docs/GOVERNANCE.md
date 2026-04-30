# Governance and Open-Standard Note

**Status:** Informational
**Last reviewed:** 2026-04-30

NACP is intended to remain implementation-neutral.

Core compliance MUST NOT depend on any specific vendor, runtime, marketplace, benchmark, registry, payment processor, or orchestration platform. Any such dependency is a defect in the specification, not a feature.

Product-specific or domain-specific behavior MUST be represented through optional, namespaced extensions:

```json
{
  "extension_fields": {
    "<namespace>.<feature>": { ... }
  }
}
```

Examples:

- `acme.scoring` — a vendor's proprietary scoring metadata
- `example.org.tournament` — a tournament-style evaluation system
- `internal.audit` — an enterprise's internal audit metadata

Bare (un-namespaced) keys in `extension_fields` are reserved for the spec.

---

## What this means in practice

- Reference implementations are welcome, but no implementation defines the protocol.
- Implementation-specific endpoints, tool names, registries, scoring systems, benchmark suites, or tournament systems MUST NOT appear in the normative core specification.
- Wire formats, identity schemes, and transports that are reasonable defaults are presented as **optional bindings** — adopt them where they fit.
- New core features SHOULD only be added when they are useful across multiple independent implementations and transports.
- Vendor-specific or domain-specific behavior SHOULD ship as a namespaced extension first; promotion to core requires multiple independent implementations.

---

## Conformance distinctions

A conformant implementation distinguishes:

- **Core conformance** — the implementation can produce and consume contracts following the neutral fields defined in `schemas/contract.schema.json` and the lifecycle defined in the spec.
- **Optional binding conformance** — the implementation supports one or more optional bindings (signed-message envelope, REST, WebSocket, cryptographic handshake, A2A bridge, MCP bridge, etc.).
- **Extension conformance** — the implementation correctly preserves unknown extension namespaces and follows the conventions for any extension namespaces it produces or consumes.

Implementations are encouraged to publish a short conformance statement listing which of the above they support and which extensions they produce.

---

## Contributions

Proposed changes to the core specification SHOULD:

- be transport-neutral
- be implementation-neutral
- not encode product-specific assumptions
- be implementable by at least two independent implementations before promotion to normative status

Vendor- or domain-specific work is welcome as namespaced extensions and as informational appendices, but does not become normative until the above is met.
