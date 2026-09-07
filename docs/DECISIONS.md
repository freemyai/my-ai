# Architecture decisions

| ADR | Decision | Status |
| --- | --- | --- |
| [0001](adr/0001-upstream-boundaries.md) | Preserve Jan ancestry; consume other upstreams through public interfaces | Accepted for M0 |
| [0002](adr/0002-canonical-state.md) | SQLite Vault owns personal state; engines own disposable indexes | Accepted design; implementation M5 |
| [0003](adr/0003-managed-runtime.md) | Isolated uv runtimes and per-AI profiles; explicit local endpoints | Provisional pending end-to-end test |
| [0004](adr/0004-arm64-worker-toolchain.md) | Build unchanged Jan worker with project-local GCC 14 and link flags | CPU spike passed; packaging pending |
| [0005](adr/0005-hermes-context-floor.md) | Respect Hermes 64K floor; do not fake small-context compatibility | Constraint confirmed; resolution open |

Architecture is not frozen until M0 gates pass. A source-level interface discovery
does not establish reliability, packaging portability, or a certified stack.
