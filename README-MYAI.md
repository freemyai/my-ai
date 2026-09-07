# My AI · Freemy AI

Local sovereign personal AI. The owner names their AI; projects belong to that
AI, not the other way around. Personal state belongs in an engine-neutral Vault.

**Development status: M0 architecture spike. Not a finished application.**
The current worktree preserves Jan's upstream history and layout. No UI redesign
has started; M1 is locked until the M0 gates are satisfied.

- [Measured M0 results and blockers](docs/M0_REPORT.md)
- [Architecture](docs/ARCHITECTURE.md) · [Decisions](docs/DECISIONS.md)
- [Adapter contract](docs/ADAPTER_SPEC.md) · [Vault contract](docs/VAULT_SPEC.md)
- [Continuity](docs/CONTINUITY_CONTRACT.md) · [Security](docs/SECURITY_MODEL.md)
- [M0 developer runbook](docs/M0_RUNBOOK.md)

Jan, Hermes, Hindsight, llmfit and hermes-lcm are composed through their public
interfaces. My AI owns the integration, policy and portability contracts, not
replacement implementations of those engines. See [upstream licenses](THIRD_PARTY_NOTICES.md).
