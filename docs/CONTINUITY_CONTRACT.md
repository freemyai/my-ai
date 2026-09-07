# Continuity contract — M0 candidate

My AI owns the contract; Hermes/LCM implement the algorithms. Persist original
history and checkpoints before rewriting active context. Runtime limits never
justify silently discarding the user's task or claimed completed actions.

| Failure/transition | Required behavior | Verification |
| --- | --- | --- |
| Context pressure | compact and continue; raw turns recoverable | 2–3× context in M0; 4K/50K and 64K/500K in M4 |
| Large tool output | artifact reference and bounded active excerpt | 100K output fixture |
| Summarizer timeout/crash | durable checkpoint, bounded retry/fallback | inject worker timeout; resume same task |
| `finish_reason=length` | detect incomplete output, bounded continuation/replan | output-cap test, no duplicated tool side effects |
| Smaller model context | reassemble within new budget from canonical state | switch and resume |
| Application restart | reconnect or recreate session from checkpoint | stop/restart with pending work |

Minimum observation: raw token volume, active prompt estimate, configured context,
summary creation, lineage, finished turn and recoverable original fact. A successful
short message with LCM enabled does not certify compaction. A plugin doctor does
not certify every failure mode. The eight-hour endurance test belongs to M4.

LCM features such as externalization and semantic retrieval may be opt-in. Record
the exact enabled configuration; do not infer behavior from the feature list.
Fallback to Hermes built-in ContextEngine is permitted by the outline, but must
retain this contract and receive its own measured compatibility result.
