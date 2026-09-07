# Adapter contract — M0 candidate

Production contracts are Rust traits; M0 Python scripts are protocol probes only.
Do not copy illustrative signatures from the implementation outline as upstream APIs.

Each component exposes detect, capabilities, install, configure, start, stop,
health, version, upgrade and rollback. State import/export is capability-gated;
unsupported operations return `Unsupported`, never a successful empty result.

Common request envelope: operation ID, AI ID, component pin, deadline,
cancellation token and policy revision. Result: status, observed version,
retryability, structured error class, evidence reference and owned handle.
Error classes: unavailable, timeout, incompatible, unauthorized, integrity,
resource exhaustion, invalid state and upstream failure. No secrets in errors.

| Plane | Public boundary verified in source | Capability probes still needed |
| --- | --- | --- |
| Hardware | llmfit `system --json`, `recommend --json` | normalized fit, live headroom |
| Download | Jan `download_files`, `pause_download_task`, `cancel_download_task` | auth separation, real pause/resume, source fallback |
| Inference | Jan `start_engine`, `get_engine_info`, load/unload commands; worker loopback API | real load, tokens, tool calling, shutdown |
| Agent | Hermes JSON-RPC `session.create`, `prompt.submit`, `session.history`, `session.interrupt` | completion, approvals, cancel, restart |
| Memory | Hindsight HTTP retain/recall, bank/document/operation endpoints | extraction, recall, rebuild, deletion |
| Continuity | Hermes `context.engine` user plugin slot | compaction, timeout, context shrink |

Capability graph resolution precedes start. A started process is not healthy
until protocol health passes; healthy is not ready until the tiny model smoke
passes. Stop uses handles created by My AI, never system-wide name matching.
Version changes invalidate compatibility evidence.

ModelSourceAdapter resolves repository revision and artifact metadata separately
from transport. Opaque auth references are attached per source origin; redirects
must not leak credentials. Content equivalence requires matching SHA-256/size,
not a matching repository name. Local GGUF import is a registered file reference
until the user elects managed copying.
