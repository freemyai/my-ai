# Third-party inventory — M0, not a release clearance

Exact repository, commit and license file SHA-256 are recorded in
[upstreams.lock](upstreams.lock). Read the full license at the pinned revision.

| Component | Inspected root license | Use / redistribution note |
| --- | --- | --- |
| Jan | Apache-2.0 | Preserve copyright/license and applicable notices; identify modifications; no trademark grant |
| Hermes Agent | MIT | Preserve copyright and permission notice |
| Hindsight | MIT | Preserve copyright and permission notice; supersedes the old discussion's Apache claim |
| llmfit | MIT | Official ARM64 binary tested; preserve release license |
| hermes-lcm | MIT | User plugin source; preserve copyright and permission notice |
| llama.cpp | MIT | Jan-pinned source; preserve notice and bundled dependencies' notices |
| huggingface_hub | Apache-2.0 | Inspected source; installed client version separately locked by Hindsight |
| modelscope_hub | Apache-2.0 | Source resolution/transport reference; not shipped yet |
| Ollama | MIT | Fallback reference; no installed runtime discovered |
| age | BSD-3-Clause | Encryption candidate; preserve notice, no endorsement |
| restic | BSD-2-Clause | Future backup reference; preserve source/binary notices |

Jan's Rust crate metadata says MIT while the repository root LICENSE is
Apache-2.0. Preserve the actual files; do not flatten component-specific notices
into one inferred license. This inventory is a technical source audit, not legal
clearance or an exhaustive transitive SBOM.

Development tooling includes uv, python-build-standalone, Rust, Ubuntu native
libraries, pg0/PostgreSQL, ONNX Runtime and all Python/Node/Cargo dependencies.
Their exact shipped artifact licenses and source obligations must be inventoried
before any installer is distributed. Package installation alone is not clearance.

M0 model: Qwen/Qwen3-1.7B-GGUF, revision
`90862c4b9d2787eaed51d12237eafdfe7c5f6077`, Apache-2.0 per upstream metadata.
`Qwen3-1.7B-Q8_0.gguf`: 1,834,426,016 bytes, SHA-256
`061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a`.
This is a small synthetic smoke model, not a recommended or certified main brain.

64K-window transport smoke: `unsloth/Qwen3.5-0.8B-GGUF`, revision
`6ab461498e2023f6e3c1baea90a8f0fe38ab64d0`, Apache-2.0 per repository metadata.
`Qwen3.5-0.8B-Q8_0.gguf`: 811,843,840 bytes, SHA-256
`0ad885ffd4bb022fc4f0d33a3308fa108ef8613159d3b3a67e23abca056b7a6c`.
The official Qwen model config declares 262144 native positions. The converted
GGUF is third-party, hash-pinned; it is not a certified main brain.

Local embedding: `intfloat/multilingual-e5-small`, MIT per repository metadata,
snapshot `614241f622f53c4eeff9890bdc4f31cfecc418b3`.
`onnx/model.onnx`: 470,268,510 bytes, SHA-256
`ca456c06b3a9505ddfd9131408916dd79290368331e7d76bb621f1cba6bc8665`.
Tokenizer and full artifact notices remain part of the release SBOM gate.
