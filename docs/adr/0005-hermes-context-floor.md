# ADR 0005 — Respect the current Hermes context floor; keep continuity gated

Status: measured compatibility constraint; product resolution open.

Pinned Hermes 0.21.0 enforces `MINIMUM_CONTEXT_LENGTH = 64000` for custom
providers (`agent/model_metadata.py` and `agent/agent_init.py`). A real 8192-token
gateway profile starts its protocol but rejects agent creation with
`agent_init_failed`. A `message.complete` envelope can contain an error and MUST
NOT count as success. The M0 client now checks this payload.

Do not fake the runtime's context length or mislabel Jan as LM Studio to bypass
this guard. Qwen3.5-0.8B has a native 262144-token window, so a 65536-token Jan
profile is valid for an integration smoke. Its size is chosen for CPU testing,
not certified agent capability, Chinese quality or user recommendation.

The requested 4K/smaller-model Continuity Contract is therefore not established
on the pinned stack. Low-threshold/manual compaction tests may prove LCM hooks,
but cannot substitute for a real 2–3× window exercise or model-switch recovery.
M1 remains locked until the gate is met or the owner explicitly accepts a
revised compatibility baseline. Do not fork Hermes merely to suppress the guard.

Further packaging issue: the managed Python 3.12.12 build includes SQLite 3.50.4.
Hermes warns about its WAL-reset bug and selects DELETE journaling for its own
stores. Audit LCM and select a patched managed runtime before production; the
Vault's WAL specification is not certification of every bundled SQLite build.

The real LCM-loaded gateway also emits `Could not apply live compression config:
'LCMEngine' object has no attribute '_coerce_threshold_tokens_cap'`. The caller
is Hermes `tui_gateway/session_compression.py:146`. LCM storage binding and tools
execute, but plugin registration is not sufficient compatibility evidence.
Do not patch in a guessed private method; validate an upstream-compatible pair
before freezing the component manifest. Tool-enabled Qwen3.5-0.8B also loops
through inappropriate retrieval calls in this fixture. The transport-only
smoke therefore disables retrieval tools via Hermes' public toolset control,
while leaving LCM as the active context engine. Tool quality remains uncertified.
