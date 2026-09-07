# Vault v0.1 — M0 schema candidate

`vault.sqlite` is transactional canonical state; `artifacts/sha256/` stores immutable
payloads. The AI is rooted under an owner and owns its projects. The SQL candidate
is in [vault-schema](../vault-schema/v0.1/schema.sql); it is not an M5 implementation.

Every canonical record carries an AI ID and immutable logical ID, revision,
creation/update time, current status and provenance. Memory adds validity interval,
confidence, origin, user confirmation and source references. Identity and owner
records must exist before projects, conversations, memories or policy.

Foreign keys are mandatory on every SQLite connection. Use WAL, full durability
for committed personal state, explicit migrations and SQLite backup API for live
snapshots. Never copy a live database file while ignoring its WAL.

In one transaction: store original conversation, provenance event and outbox item.
Materialization retries use `(AI, record, revision, engine)` identity. A failure
keeps the outbox pending; only a verified engine acknowledgement marks it applied.
Rebuild projects active canonical state into a fresh bank, validates it and switches
the runtime pointer. Do not parse Hindsight's internal PostgreSQL schema.

Record kinds cover person, preference, decision, goal, project, skill reference,
checkpoint and migration event in addition to identity, conversation and memory.
Runtime checkpoint fields are namespaced optional metadata; portable work state
also retains task intent, completed actions, unresolved approvals and artifact refs.

`.myai` is a versioned archive of manifest, schema, identity, owner, JSONL records,
policy, skills references, artifacts and checksums. Stable key ordering and record
ordering make content hashes deterministic; timestamps are explicit metadata.
Exports exclude tokens, caches, browser sessions and private runtime credentials.

Import checks schema, checksums, path traversal, duplicate paths, symlinks, size
limits and decompression ratio before staging. Apply migrations into staging;
run ownership checks; atomically activate. Failure leaves the previous AI active.
Use an existing archive library and mature age-compatible encryption; encryption
and cross-platform packaging remain explicit M0/M7 dependency gates.
