# M0 developer runbook

Reference layout:

```text
my_ai/
  my-ai/       this Git repository, derived from pinned Jan
  references/  separate source clones, pinned by upstreams.lock
  .m0/         local toolchains, models, runtimes and synthetic state; not Git
```

This is a reproducible invocation guide for the provisioned Spark developer
environment, **not a clean-machine installer**. Installing system dependencies,
redistributing binaries and launching the whole desktop still require M0/M8 work.
The immutable source locks do not replace a reviewed release manifest.

## Checks

```bash
python3 scripts/m0/test_contracts.py
python3 scripts/m0/age_probe.py --bin-dir ../.m0/downloads/age/age
bash scripts/m0/build-jan-worker.sh
corepack yarn vitest run extensions/download-extension/src/index.test.ts
```

Baseline web build executed successfully without changing Jan source:

```bash
corepack yarn build:tauri:plugin:api
corepack yarn build:core
corepack yarn build:extensions
corepack yarn build:web
```

## Real local chain

Run from the repository. Both ports must be free; the harness refuses to attach
to or stop existing services. Choose a new `--work` path for every attempt; it
will not overwrite evidence. The named pg0 instance `myai-m0-spike` contains only
synthetic M0 memory. It is retained for inspection, not deleted during cleanup.

```bash
python3 scripts/m0/chain.py \
  --work ../.m0/chain-new-run \
  --worker src-tauri/plugins/tauri-plugin-llamacpp/target/debug/jan-llama-worker \
  --model ../.m0/models/qwen3.5-0.8b/Qwen3.5-0.8B-Q8_0.gguf \
  --hermes-python ../.m0/runtimes/hermes-managed/bin/python \
  --hindsight ../.m0/runtimes/hindsight/bin/hindsight-local-mcp \
  --lcm ../references/hermes-lcm \
  --embeddings-snapshot /home/nvidia/.cache/huggingface/hub/models--intfloat--multilingual-e5-small/snapshots/614241f622f53c4eeff9890bdc4f31cfecc418b3
```

The harness verifies the test GGUF and ONNX hashes, starts the Jan worker with
its public preset/HTTP contract, starts local Hindsight with pinned local
embeddings, and drives Hermes' public stdio gateway. It tests a synthetic
preference across two sessions and saves `result.json` and raw synthetic protocol.
An error-bearing `message.complete` fails the run. Child stdin/termination is
owned and bounded; unrelated services are never scanned or killed.

Only synthetic data may be used. The loopback test credential is deliberately
non-secret, Hindsight has no auth in this developer profile, and process groups
are not an OS sandbox. This is not a production Owner Policy implementation.
The runtime disables lazy package installs and cloud-credential inheritance;
Hindsight's embedding loader is explicitly offline. This is not yet a
packet-capture proof that every upstream path is offline.

Managed Hermes environment was installed with frozen uv dependencies and the
`hindsight` extra; Hindsight uses frozen `hindsight-api-slim`, `embedded-db` and
`local-onnx` extras. Python 3.12.12's SQLite warning is unresolved for shipping:
see ADR 0005. Do not use developer smoke profiles as users' canonical data.
