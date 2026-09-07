# M0 Architecture Spike

Status: **IN PROGRESS — M1 locked**. Reference machine: Linux aarch64, NVIDIA GB10.

This report distinguishes source inspection, successful execution, and unverified
claims. A dependency installation or mocked test does not certify an integration.
The parent directory's `My_AI_v0.1_工程实施大纲.md` is the implementation authority.

## Evidence so far (2026-09-07 UTC)

| Spike | Evidence | Status |
| --- | --- | --- |
| Jan baseline | Pristine main `659147f4a75494a82d038edb766cab37c54e26a5`; upstream structure retained | Checked out |
| Jan dependencies | Yarn 4.5.3 immutable install succeeded; upstream peer warnings retained | PASS |
| Jan frontend | API/core/extensions/web builds succeed; original download extension 17 tests pass | PASS; no UI edits |
| Jan ARM64 worker | Original source builds using project-local GCC14 + explicit libgcc helpers; real Qwen3.5 response via authenticated HTTP | PASS CPU; ADR 0004 |
| Jan full desktop ARM64 | Native worker is not the complete Tauri app/installer | Not yet built/launched |
| llmfit | Official 1.1.14 GNU aarch64 release archive verified against upstream SHA-256; CLI executes | PASS |
| Hardware JSON | GB10 / CUDA / 20 cores / 121.69 GiB unified memory; only 22.56 GiB available at probe | PASS |
| Hermes packaging | Frozen uv install, 73 packages, project-local managed Python 3.12.12; not system Python | Runs; SQLite version needs replacement |
| Hermes public gateway | Actual `python -m tui_gateway.entry` JSON-RPC; message → Jan → final text | PASS transport; not tool capability |
| Hindsight lifecycle | Local slim + pg0/PostgreSQL + ONNX; healthy; real retain and recall | PASS synthetic data |
| Hermes → Hindsight | Automatic retain contains source session/turn metadata; API recall and new-session recall indicator observed | PASS memory transport |
| Cross-session answer | Run 005 correctly answers `Blue iris` from injected memory with an explicit extraction prompt; run 004's ordinary wording fails | PASS narrow fixture; quality not certified |
| LCM | Plugin storage binds and tools execute; live compression config warns about missing `_coerce_threshold_tokens_cap` | PARTIAL; not continuity PASS |
| age | Official ARM64 CLI encrypt/decrypt exact round-trip and rejects modified ciphertext | PASS CLI only; not `.myai` restore |
| Vault draft | 11 local contracts pass: AI-scoped FKs, atomic outbox, probe isolation/protocol regression | PASS schema/probe tests; not M5 |
| Licenses | 11 source pins with license hashes; model/embedding hashes; transitive release SBOM not complete | Source inventory; not release clearance |
| Freedom Lab | Not found in inspected local locations; existing vLLM services belong to other work | Location requested |

## Integration facts that change the proposed implementation

1. Current Jan main builds `jan-llama-worker` from pinned ggml-org/llama.cpp
   b10621 (`c1d0e7a004015f23bc0233470b747b596f29b264`). It replaces the older
   downloaded router. Use current public Tauri commands and loopback HTTP surface.
2. The Jan download extension accepts generic URLs, SHA-256 and sizes, but its
   public wrapper adds one HF bearer header to the whole batch. Source-specific
   credentials require a thin adapter and scrutiny of redirect handling before
   enabling authenticated ModelScope. Never reuse HF auth for another source.
3. Hermes has separate JSON-RPC and OpenAI-compatible HTTP gateways. `hermes serve`
   is the headless desktop JSON-RPC/WebSocket gateway, not `/v1/chat/completions`.
4. Hindsight's Hermes plugin defaults to cloud and observation-only recall. My AI
   must explicitly configure `local_external`, per-AI bank, and local workers.
5. Unified memory must not be counted twice. Total hardware fit is not permission
   to load a model larger than currently available memory.
6. Hermes currently rejects custom-provider contexts below 64000. The requested
   4K continuity case is blocked; never fake a model's context metadata (ADR 0005).
7. llmfit `recommend --json --runtime llamacpp --capability tool_use` still emitted
   MLX/bnb artifacts without GGUF sources and used total unified memory, not live
   available RAM. Catalog artifact/headroom checks are essential.
8. Hindsight's actual no-neural-reranker option is `rrf`, not `none`. Cold embedding
   download exceeded its startup deadline; local snapshot paths plus offline
   loading solve the provisioned-runtime start. Cold install still needs orchestration.
9. Hermes now host-gates generic OpenAI keys. Use a named custom provider and
   `key_env`, not ambient cloud credentials. Its startup also performs model
   catalog/update checks; disabling lazy installs alone is not offline certification.

## Gate evidence required before M1

- [ ] Original Jan native build and start, or measured ARM64 failure with approved fallback ADR.
- [x] Real local model message through Hermes public protocol.
- [ ] Reliable cross-session answer: retain/injection pass, but the one passing answer in run 005 is not repeatable with this model.
- [ ] Context engine loaded, with raw history persistence and real compaction evidence.
- [ ] 2–3× context-window continuity exercise.
- [x] Provisioned inference/memory/gateway lifecycle managed by M0 harness; owned Jan/Hindsight exit 0 on failed test.
- [ ] Versions, license hashes, commands and results recorded.
- [ ] Adapter/Vault/Policy/Continuity specs and remaining risks reviewed.

The Jan → Hermes → Hindsight → new-session answer smoke passes in run 005.
This is NOT the complete hardware/download/continuity/Vault M0 Gate. No UI
branding or subsequent product milestone has begun.

## Reproduction and evidence

See [runbook](M0_RUNBOOK.md), [source lock](../upstreams.lock),
[hardware JSON](evidence/m0/hardware.json), and
[raw llmfit recommendations](evidence/m0/recommendations.json).
Raw synthetic runs are retained outside Git at `../.m0/chain-001` through
`chain-005`, including failed attempts. Run 001 was interrupted during an implicit
remote embedding check; 002 exposed provider authentication configuration; 003
exposed tiny-model retrieval loops; 004 proved automatic retain and injection but
failed the answer assertion. Do not erase failed runs when adding a passing case.
Run 005 asks which flower Mira prefers using supplied persistent context (without
naming the flower) and answers `Blue iris`, one API call, no tool call in that
turn. Both managed Jan and Hindsight children exit 0. Sanitized summaries:
[failed ordinary question](evidence/m0/chain-004.json) and
[passing extraction fixture](evidence/m0/chain-005.json).
The first turn in run 005 used its four-call budget and produced awkward wording;
the passing transport assertion does not certify the tiny model's instruction
following. Retrieval tools are disabled, but Hermes' built-in memory tool remains
in the `memory` toolset. No general-purpose shell/file tools are enabled.

Run 006 repeats the extraction wording with short-compaction settings and fails
the answer assertion before reaching compression. A one-off passing answer is
not a reliability result. The script now permits the independent compaction
probe to run despite answer failure, while keeping the overall result FAIL.

No pre-existing vLLM or user service was changed. Temporary test servers are
loopback-only and stopped after each harness run. Downloaded models/toolchains
and the explicitly named synthetic pg0 database remain for reproducibility.

## Remaining M0 work, in order

1. Locate the already validated Freedom Lab stack and compare exact component and
   model pins; avoid treating today's unrelated upstream heads as a certified set.
2. Certify a capable model on Spark (including GPU, tools and Chinese), resolve
   Hermes/LCM compatibility, replace unsafe bundled SQLite, and rerun memory QA.
3. Execute real compaction, timeout/output-limit recovery and 2–3× window tests;
   settle the smaller-context restriction before architecture freeze.
4. Finish original desktop build/start, download pause/resume/corruption checks,
   authenticated source/redirect review, regional source tests and release SBOM.
5. Review all adapter and Vault contracts, then evaluate M0 Gate. Do not enter M1
   solely because an individual smoke passes.
