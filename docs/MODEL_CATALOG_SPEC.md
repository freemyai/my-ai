# Model catalog — M0 candidate

Separate model family, exact artifact, runtime plan and compatibility evidence.
An artifact is a repository revision + file + format + quantization + size + hash
+ license/gating metadata. Different weights never share an artifact ID merely
because their model names look similar.

Recommendations combine hardware headroom, user uses/languages, measured agent
reliability, context stability, speed evidence and license/access requirements.
Missing evidence is unknown, not a perfect score. Filter out missing/incompatible
artifacts before scoring. Deduplicate variants by underlying model where useful.

M0 llmfit emitted MLX/bnb source entries with `runtime: llama.cpp` and no GGUF
sources. It also reports total unified memory as fit memory. My AI must validate
actual artifacts and reserve live memory for the OS, KV cache and workers. This
is why raw llmfit results cannot be the final recommendation list.

Display Best Overall, Faster, More Powerful when enough supported candidates
exist; fewer truthful choices are better than invented certifications. Preserve
Browse All and manual selection of compatible artifacts. Distinguish predicted
speed from locally measured speed. Never invent Chinese/tool-calling scores.

Source Auto probes availability/latency without uploading personal data. Switch
HF↔ModelScope only after matching artifact hash/size. Download telemetry remains
local. Unauthenticated small artifact probes precede gated downloads.
