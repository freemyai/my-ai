# ADR 0003: Managed sidecars with explicit local configuration

Date: 2026-09-07. Status: provisional.

Hermes is installed from its exact checkout and upstream `uv.lock` into an
application-owned virtual environment. The first probe used system Python 3.12;
this does not prove installation on a computer without Python. A bundled uv plus
managed Python distribution remains a separate packaging gate.

Use Hindsight's public HTTP interface and its official `embedded-db` package.
Run it as a separate process with a unique pg0 instance, explicit loopback bind,
local LLM and local embeddings. Avoid the all-extras ML stack when ONNX suffices.
Do not rely on the Hermes memory plugin's cloud defaults or implicit daemon.

Hermes receives a dedicated HERMES_HOME. Enable LCM by the upstream plugin loader.
M0 clients use the public gateway protocol and never import AIAgent/private modules.
Only owned processes are stopped; never invoke Hermes's broad `serve --stop` scan.

M0 uses synthetic conversations. Product secrets need OS credential storage and
minimal child environments. Inherited provider credentials must not permit an
accidental cloud fallback.
