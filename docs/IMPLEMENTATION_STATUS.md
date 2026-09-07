# Implementation status

Active milestone: M0. M1–M9 are not started.

Checkpoint: original ARM64 Jan worker runs; real Hermes/Hindsight memory transport
and a manual LCM compression/continuation have passing fixtures. Repeated model
and memory failures, the 64K floor and unfinished desktop/overflow gates prevent
M0 acceptance. No main-brain recommendation or product release is certified.

See [M0 report](M0_REPORT.md) for measured gates and [decisions](DECISIONS.md) for ADRs.
M0 scripts are disposable integration experiments; the product Control Plane
remains Rust. Upstream code is not moved to match an illustrative directory tree.

Local layout: this repository contains the Jan-derived worktree; sibling
`../references/` contains separately pinned upstream source checkouts; sibling
`../.m0/` contains development dependencies and synthetic test state. Neither
runtime state nor model weights belong in Git.
