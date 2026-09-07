#!/usr/bin/env python3
"""Capture pinned source/license evidence. No installs, model calls or secrets."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def command(args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, text=True, timeout=60).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--references', type=Path, required=True)
    parser.add_argument('--llmfit', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    refs = args.references.resolve()
    components = [('jan', root, 'Apache-2.0')]
    components += [(name, refs / name, license_id) for name, license_id in [
        ('hermes-agent', 'MIT'), ('hindsight', 'MIT'), ('llmfit', 'MIT'),
        ('hermes-lcm', 'MIT'), ('huggingface-hub', 'Apache-2.0'),
        ('modelscope-hub', 'Apache-2.0'), ('ollama', 'MIT'),
        ('age', 'BSD-3-Clause'), ('restic', 'BSD-2-Clause')]]
    llama = root / 'src-tauri/plugins/tauri-plugin-llamacpp/vendor/llama.cpp'
    if llama.exists():
        components.append(('llama.cpp', llama, 'MIT'))
    records = []
    for name, path, license_id in components:
        candidates = [path / n for n in ('LICENSE', 'LICENSE.txt', 'LICENSE.md')]
        license_file = next(p for p in candidates if p.is_file())
        remote = 'upstream' if name == 'jan' else 'origin'
        records.append({
            'name': name,
            'repository': command(['git', 'remote', 'get-url', remote], path),
            'commit': command(['git', 'rev-parse',
                               'refs/remotes/upstream/main' if name == 'jan' else 'HEAD'], path),
            'license': license_id,
            'license_file': license_file.name,
            'license_sha256': hashlib.sha256(license_file.read_bytes()).hexdigest(),
            'usage': 'source integration spike; not certified for redistribution',
        })
    lock = {'schema_version': 1, 'certified': False, 'components': records}
    (root / 'upstreams.lock').write_text(json.dumps(lock, indent=2) + '\n')
    evidence = root / 'docs/evidence/m0'
    evidence.mkdir(parents=True, exist_ok=True)
    for name, argv in [
        ('hardware', ['system', '--json']),
        ('recommendations', ['recommend', '--json', '--limit', '3',
                             '--runtime', 'llamacpp', '--capability', 'tool_use']),
    ]:
        result = json.loads(command([str(args.llmfit.resolve()), *argv]))
        (evidence / f'{name}.json').write_text(json.dumps({
            'captured_at': datetime.now(timezone.utc).isoformat(),
            'command': ['llmfit', *argv], 'result': result,
            'scope': 'upstream raw result; not My AI certification or a measured speed',
        }, indent=2) + '\n')
    print(f'Recorded {len(records)} source pins and llmfit evidence.')


if __name__ == '__main__':
    main()
