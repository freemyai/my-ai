#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
remote_url=$(git remote get-url upstream)
if [[ "$remote_url" != "https://github.com/janhq/jan.git" ]]; then
  echo 'Unexpected upstream URL; refusing to fetch.' >&2
  exit 1
fi
git fetch upstream main
git log --oneline --left-right HEAD...upstream/main
