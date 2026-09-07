# Jan upstream maintenance

Upstream: https://github.com/janhq/jan.git. Target: https://github.com/freemyai/my-ai.
The repository preserves Jan's original ancestry and layout. The initial checkout
is shallow; unshallow before long-range rebases or complete historical audits.

M0 baseline: `659147f4a75494a82d038edb766cab37c54e26a5`. No Jan core patches.
My AI additions live in docs, scripts/m0 and vault-schema. Branding remains Jan
until M1, so the original build can be evaluated without product changes.

Use `bash scripts/sync-jan-upstream.sh` to fetch and inspect divergence. The helper
does not merge, move branches or overwrite a working tree. Integration occurs on
a review branch with source pins, licenses and compatibility gates revalidated.
Any future core patch requires an ADR and entry in a patch manifest.
