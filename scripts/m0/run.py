#!/usr/bin/env python3
"""Bounded build/probe log capture; shell-free, with exit-status evidence."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a command is required')
    args.log.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    with args.log.open('w') as log:
        proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = proc.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
            code = 124
    result = {'command': command, 'exit_code': code, 'duration_seconds': round(time.monotonic()-start, 2)}
    args.log.with_suffix('.result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    if code:
        print('\n'.join(args.log.read_text(errors='replace').splitlines()[-12:]))
    raise SystemExit(code)


if __name__ == '__main__':
    main()
