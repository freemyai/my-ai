# Model source integration findings — M0

These are inspected APIs, not a completed M2 download adapter.

- Hugging Face: official CLI `hf download REPO FILE --revision COMMIT --local-dir DIR`
  was used for two GGUF artifacts. Revision, byte length and SHA-256 are recorded
  in the M0 report. A moving branch is not a compatibility lock.
- Current `modelscope/modelscope-hub` is the lightweight `modelscope_hub` package,
  not the historical heavyweight `modelscope` package. Inspected public
  `HubApi.list_repo_files(repo_id, repo_type, revision=..., recursive=True)` and
  `HubApi.download_file(repo_id, repo_type, file_path, revision=...,
  expected_sha256=..., local_dir=..., local_files_only=...)`.
  The legacy compatibility `model_file_download` wrapper delegates to this API.
  Endpoint auto-resolution exists, but is not equivalent to measured speed-based
  source selection. No ModelScope cross-source GGUF equivalence has been certified.
- Jan's generic download Tauri command can take resolved artifact URLs and hashes.
  Its extension wrapper currently adds one HF credential header to a download
  batch. A source adapter must bind credentials to the intended origin, including
  redirects, and avoid forwarding platform credentials to another source.

Source selection requires a catalog's explicit equivalent-artifact mapping:
same expected content hash, model revision, quantization and license. Neither a
matching filename nor a faster metadata response is proof of equivalence.
Bandwidth, resumability, offline cache, integrity failures and China-network
fallback remain separate tests. This Spark machine is not a China-network testbed;
do not invent regional latency claims from it.

Ollama is cloned and license-pinned for a future runtime/source adapter. Its
presence in the inventory does not establish that an Ollama daemon was exercised.
