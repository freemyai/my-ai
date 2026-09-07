-- M0 executable schema candidate. Not a production migration.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;

CREATE TABLE owners (
    id TEXT PRIMARY KEY NOT NULL,
    display_name TEXT NOT NULL
) STRICT;
CREATE TABLE ais (
    id TEXT PRIMARY KEY NOT NULL,
    owner_id TEXT NOT NULL REFERENCES owners(id),
    name TEXT NOT NULL,
    identity_json TEXT NOT NULL CHECK(json_valid(identity_json)),
    created_at TEXT NOT NULL
) STRICT;
CREATE TABLE provenance (
    ai_id TEXT NOT NULL REFERENCES ais(id),
    id TEXT NOT NULL,
    actor TEXT NOT NULL,
    event_type TEXT NOT NULL,
    source_json TEXT NOT NULL CHECK(json_valid(source_json)),
    occurred_at TEXT NOT NULL,
    PRIMARY KEY (ai_id, id)
) STRICT;
CREATE TABLE records (
    ai_id TEXT NOT NULL REFERENCES ais(id),
    id TEXT NOT NULL,
    kind TEXT NOT NULL CHECK(kind IN
      ('memory','person','preference','decision','goal','project','skill',
       'policy','checkpoint','migration','knowledge')),
    revision INTEGER NOT NULL CHECK(revision > 0),
    status TEXT NOT NULL CHECK(status IN ('active','superseded','forgotten')),
    body_json TEXT NOT NULL CHECK(json_valid(body_json)),
    provenance_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY(ai_id, id),
    FOREIGN KEY(ai_id, provenance_id) REFERENCES provenance(ai_id, id)
) STRICT;
CREATE TABLE conversations (
    ai_id TEXT NOT NULL REFERENCES ais(id),
    id TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY(ai_id, id)
) STRICT;
CREATE TABLE messages (
    ai_id TEXT NOT NULL,
    id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    ordinal INTEGER NOT NULL CHECK(ordinal >= 0),
    role TEXT NOT NULL CHECK(role IN ('user','assistant','tool','system')),
    content_json TEXT NOT NULL CHECK(json_valid(content_json)),
    provenance_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY(ai_id, id),
    UNIQUE(ai_id, conversation_id, ordinal),
    FOREIGN KEY(ai_id, conversation_id) REFERENCES conversations(ai_id, id),
    FOREIGN KEY(ai_id, provenance_id) REFERENCES provenance(ai_id, id)
) STRICT;
CREATE TABLE artifacts (
    ai_id TEXT NOT NULL REFERENCES ais(id),
    sha256 TEXT NOT NULL CHECK(length(sha256)=64 AND sha256 NOT GLOB '*[^0-9a-f]*'),
    size_bytes INTEGER NOT NULL CHECK(size_bytes >= 0),
    media_type TEXT NOT NULL,
    provenance_id TEXT NOT NULL,
    PRIMARY KEY(ai_id, sha256),
    FOREIGN KEY(ai_id, provenance_id) REFERENCES provenance(ai_id, id)
) STRICT;
CREATE TABLE materialization_outbox (
    ai_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    engine_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('pending','applied','failed')),
    attempts INTEGER NOT NULL DEFAULT 0 CHECK(attempts >= 0),
    last_error_class TEXT,
    PRIMARY KEY(ai_id, event_id, engine_id),
    FOREIGN KEY(ai_id, event_id) REFERENCES provenance(ai_id, id)
) STRICT;
CREATE INDEX records_by_kind ON records(ai_id, kind, status);
CREATE INDEX outbox_pending ON materialization_outbox(state, ai_id);
