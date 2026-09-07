# Security model — M0 candidate

Owner Policy is canonical and versioned separately from generated Hermes config.
The compiler maps file access, network, shell, cloud routing and approvals to
adapter capabilities. Unsupported enforcement fails closed or selects Assistant
mode. A prompt instruction is not an OS/network sandbox.

Explicit loopback endpoints and minimal child environments prevent inherited
cloud credentials from changing routing. Loopback listeners still require scoped
credentials in the product; never log tokens, include them in process arguments
or export them. OS Keychain holds secret values; Vault holds references only.

Jan's existing extension settings must not become My AI's credential storage.
Its download wrapper uses HF headers across a batch; source adapters must separate
origins and verify redirect auth behavior before authenticated multi-source use.

Agent mode requires a verified sandbox with explicit mounts and network policy.
Absent one, allow Chat/Memory and withhold shell/file tools. M0 uses synthetic
profiles and restricted toolsets; it does not certify production isolation.

No telemetry by default. Disable Hindsight LLM trace recording for the probe;
OpenTelemetry exporters remain disabled. Support bundles omit conversations,
memories, user files and secret values. Runtime logs stay private until reviewed.

Supply-chain gates: exact commits, upstream lockfiles, authenticated transport,
verified archive digests and clean staging. Licenses are inventoried from the
actual pinned source; transitive dependency/model audits remain release gates.
