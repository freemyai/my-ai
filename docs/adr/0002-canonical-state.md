# ADR 0002: AI state is independent of runtime

Date: 2026-09-07. Status: accepted design.

The ownership root is Owner → AI → projects/history/preferences/policy. Persist
canonical records transactionally in SQLite, with content-addressed artifacts.
Hermes state and Hindsight/LCM databases are not authoritative personal state.

Commit conversation/provenance and a materialization outbox entry in the same
transaction. Index asynchronously with idempotency keys. Rebuild a new index from
Vault, verify it, then activate it. A backend outage leaves durable pending work.

Forgetting writes a tombstone and invalidates every derived replica. Until the
backend acknowledges deletion, deny retrieval of the tombstoned record and mark
health degraded. Rebuilding must replay current active state, never resurrect it.

Export canonical, runtime-neutral JSONL plus hashed artifacts and a versioned
manifest. OS credential references may survive; secret values never do. The
presence of provenance is not proof of factual correctness: retain confirmation
and validity separately.
