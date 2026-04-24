# NACP Security Model & Guidelines

## 1. Threat Model

NACP operates in a "Zero-Trust" environment where agents may be malicious or compromised. The security model assumes:
- The network (including Liaisons) may be intercepted.
- Agents may attempt to replay messages.
- Agents may attempt to inject malicious instructions into tasks.

---

## 2. Core Security Pillars

### 2.1 Cryptographic Identity (Ed25519)
All messages post-registration MUST be signed. Verification failure MUST result in immediate message rejection (`NACP-401`).

### 2.2 Replay Protection (Timestamp Windows)
Implementations MUST enforce a maximum clock skew (suggested: 300 seconds). 
- Messages with a timestamp outside this window MUST be rejected.
- Agents SHOULD track `msg_id` within the skew window to prevent exact replays.

### 2.3 Perfect Forward Secrecy (X25519)
For sensitive task data, agents SHOULD use the `HANDSHAKE` flow to establish an ephemeral encrypted channel. This ensures that even if an agent's long-term identity key is stolen, past traffic remains secure.

---

## 3. Implementation Security (Defense in Depth)

### 3.1 Input Sanitization
Agents receiving `TASK_ASSIGN` messages MUST NOT trust `input_data`. 
- **Command Injection**: Never pass input directly to a shell. Use `shell=False` in subprocesses and use allow-lists for executable paths.
- **Path Traversal**: Validate all file paths. Use `.resolve()` and ensure paths are within the designated workspace.

### 3.2 LLM Safety (Indirect Prompt Injection)
Agents using LLMs MUST treat the task `description` and `input_data` as untrusted content.
- Use distinct System/User/Assistant role separation.
- Implement "guardrail" checks on LLM output before returning `TASK_RESULT`.

### 3.3 Resource Limits (DoS Protection)
Liaisons MUST enforce:
- **Maximum Payload Size**: Suggested 10MB.
- **Rate Limiting**: Per-agent limits on `HEARTBEAT` and `TASK_ASSIGN`.
- **TTL Enforcement**: Messages MUST be purged after their TTL expires.

---

## 4. Vulnerability Reporting

If you find a security issue in the NACP specification or reference implementations, please report it to NeutralAIz Security at `security@neutralaiz.com`.
