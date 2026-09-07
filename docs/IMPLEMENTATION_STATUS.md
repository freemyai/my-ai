# Implementation status

Active milestone: M0. M1–M9 are not started.

See [M0 report](M0_REPORT.md) for measured gates and [decisions](DECISIONS.md) for ADRs.
M0 scripts are disposable integration experiments; the product Control Plane
remains Rust. Upstream code is not moved to match an illustrative directory tree.

Local layout: this repository contains the Jan-derived worktree; sibling
`../references/` contains separately pinned upstream source checkouts; sibling
`../.m0/` contains development dependencies and synthetic test state. Neither
runtime state nor model weights belong in Git.
