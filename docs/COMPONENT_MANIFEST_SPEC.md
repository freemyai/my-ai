# Component manifest — M0 candidate

`upstreams.lock` records inspected source commits and license hashes. It is not a
certified binary manifest. Release manifests additionally require:

| Field | Required meaning |
| --- | --- |
| component_id / version / commit | Immutable identity |
| platform / arch / ABI / backend | Explicit supported target |
| URL / SHA-256 / byte size | Verified downloadable executable artifact |
| provides / requires | Capabilities with protocol version ranges |
| runtime / dependencies | Python, native libraries, driver constraints |
| config_schema / state_schema | Migrations and rollback compatibility |
| license / notices | Complete redistribution metadata |
| probes / evidence / certification | Test versions and observed outcomes |

Stage new versions beside the working installation. Verify checksum before
execution, and publish by atomic rename on the same filesystem. Retain the prior
version until health, capability and ownership checks commit the update.
Database migrations need snapshots and compatibility checks before switching.

Do not trust a mutable tag, moving download URL or component self-reported version
alone. A release digest does not imply model quality or security certification.
Stable-channel publication is a deliberate compatibility decision.
