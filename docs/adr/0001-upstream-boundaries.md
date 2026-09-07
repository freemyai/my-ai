# ADR 0001: Preserve upstream boundaries

Date: 2026-09-07. Status: accepted for M0.

My AI retains Jan's Git ancestry and directory layout. `upstream` is janhq/jan;
`origin` is freemyai/my-ai. No UI changes in M0. Hermes, Hindsight, llmfit and LCM
remain independent checkouts and versioned managed components, without forks.

Current Jan main supersedes the discussed router with `jan-llama-worker`; its
public API and its exact llama.cpp pin are authoritative. Adapter contracts carry
capabilities rather than hard-coding a process topology. A worker failure cannot
become a reason to implement an inference engine.

For Spark, attempt the unchanged upstream build first. Missing development
packages are an environment issue, not evidence that ARM64 is unsupported.
Official Jan v0.8.4 release assets list amd64 Linux packages, not ARM64 packages;
consumer redistribution therefore needs a separately validated ARM64 build.

The reference discussion names crc-org/llama.cpp, but the actual Jan build fetches
ggml-org/llama.cpp. Follow the verified Jan pin, not that historical reference.
