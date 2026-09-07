#!/usr/bin/env python3
"""Synthetic M0 client of the public Hermes stdio JSON-RPC gateway.

Development probe only, not the Rust product Orchestrator. Owns its child,
uses an isolated profile, and records protocol results without importing Hermes.
"""
import argparse
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import threading
import time
from urllib.parse import urlsplit


def local_endpoint(value):
    parsed = urlsplit(value)
    return (parsed.scheme == 'http' and parsed.hostname == '127.0.0.1'
            and parsed.username is None and parsed.password is None
            and parsed.port is not None and not parsed.query and not parsed.fragment)


def require_complete(event):
    params = event.get('params', {})
    if params.get('type') != 'message.complete' or params.get('payload', {}).get('status') != 'complete':
        raise RuntimeError('Gateway did not report a successful completed message')
    return event


def child_env(profile):
    # Do not inherit cloud credentials, proxy routing, active Hermes profiles,
    # provider defaults or arbitrary user Python startup settings.
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'LANG', 'TMPDIR') if k in os.environ}
    env.update(HERMES_HOME=str(profile), NO_PROXY='127.0.0.1,localhost',
               HF_HUB_DISABLE_TELEMETRY='1', PYTHONUNBUFFERED='1',
               HERMES_TUI_TOOLSETS='memory', HERMES_TUI_MAX_TURNS='4',
               HERMES_DISABLE_LAZY_INSTALLS='1',
               HERMES_SKIP_UPDATE_CHECK='1',
               MYAI_LOCAL_API_KEY='myai-local-spike', LCM_FRESH_TAIL_COUNT='4',
               LCM_FRESH_TAIL_MAX_TOKENS='2048')
    return env


def prepare(profile, lcm, endpoint, model, context_length=65536):
    if profile.exists():
        raise ValueError('Use a new probe profile; existing state is never overwritten.')
    profile.mkdir(parents=True, mode=0o700)
    (profile / 'plugins').mkdir()
    (profile / 'plugins/hermes-lcm').symlink_to(lcm.resolve(), target_is_directory=True)
    # JSON is a YAML subset. Values are from the inspected upstream config schema.
    config = {
        'providers': {'myai-local': {'base_url': endpoint, 'key_env': 'MYAI_LOCAL_API_KEY',
                                     'api_mode': 'chat_completions'}},
        'model': {'default': model, 'provider': 'custom:myai-local', 'base_url': endpoint,
                  'context_length': context_length},
        'max_tokens': 512,
        'plugins': {'enabled': ['hermes-lcm']},
        'context': {'engine': 'lcm'},
        'memory': {'provider': 'hindsight'},
        # Keep the context engine active, but do not expose retrieval tools in
        # this memory-transport smoke. Agent/tool quality is a separate gate.
        'platform_toolsets': {'cli': ['memory'], 'tui': ['memory']},
        'compression': {'enabled': True, 'threshold': 0.5},
        'auxiliary': {'compression': {'provider': 'custom:myai-local', 'base_url': endpoint,
                                     'model': model, 'timeout': 120},
                      'title_generation': {'provider': 'custom:myai-local', 'base_url': endpoint, 'model': model},
                      'background_review': {'enabled': False}},
    }
    (profile / 'config.yaml').write_text(json.dumps(config, indent=2))
    (profile / 'hindsight').mkdir()
    (profile / 'hindsight/config.json').write_text(json.dumps({
        'mode': 'local_external', 'api_url': 'http://127.0.0.1:19188',
        'bank_id': profile.name, 'auto_retain': True, 'auto_recall': True,
        'recall_sync': True, 'recall_types': 'world,experience,observation',
        'recall_max_tokens': 512, 'retain_async': False, 'memory_mode': 'context',
    }, indent=2))


class Gateway:
    def __init__(self, python, profile, compression_spike=False):
        self.events = queue.Queue()
        self.stderr = (profile / 'gateway.stderr.log').open('w')
        env = child_env(profile)
        if compression_spike:
            # Public LCM knobs: exercise compaction on a short synthetic backlog.
            # This is NOT a 2–3x native-context overflow test.
            env.update(LCM_LEAF_CHUNK_TOKENS='512', LCM_DYNAMIC_LEAF_CHUNK_ENABLED='false',
                       LCM_FRESH_TAIL_COUNT='2', LCM_CONTEXT_THRESHOLD='0.95')
        self.proc = subprocess.Popen([str(python), '-m', 'tui_gateway.entry'],
                                     env=env, cwd=profile,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=self.stderr, text=True, start_new_session=True)
        self.counter = 0
        self.transcript = []
        self.pending = []
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.proc.stdout:
            try:
                self.events.put(json.loads(line))
            except json.JSONDecodeError:
                # Human stdout is not protocol evidence, and could contain secrets.
                pass
        self.events.put(None)

    def wait(self, predicate, timeout=180):
        for index, event in enumerate(self.pending):
            if predicate(event):
                return self.pending.pop(index)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                event = self.events.get(timeout=max(0.01, deadline-time.monotonic()))
            except queue.Empty as exc:
                raise TimeoutError('Gateway response deadline exceeded') from exc
            if event is None:
                raise RuntimeError(f'Gateway exited: {self.proc.poll()}')
            self.transcript.append(event)
            if predicate(event):
                return event
            self.pending.append(event)
        raise TimeoutError('Gateway response deadline exceeded')

    def rpc(self, method, params):
        self.counter += 1
        rid = self.counter
        self.proc.stdin.write(json.dumps({'jsonrpc': '2.0', 'id': rid,
                                         'method': method, 'params': params}) + '\n')
        self.proc.stdin.flush()
        event = self.wait(lambda e: e.get('id') == rid)
        if 'error' in event:
            raise RuntimeError(json.dumps(event['error']))
        return event['result']

    def close(self):
        if self.proc.poll() is None:
            # Public stdio EOF lets Hermes drain providers and close its stores.
            self.proc.stdin.close()
            try:
                self.proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGTERM)
                try:
                    self.proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(self.proc.pid, signal.SIGKILL)
                    self.proc.wait(timeout=5)
        self.stderr.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--python', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--lcm', type=Path, required=True)
    parser.add_argument('--endpoint', default='http://127.0.0.1:19137/v1')
    parser.add_argument('--model', default='myai-m0')
    parser.add_argument('--context-length', type=int, default=65536)
    parser.add_argument('--message', help='Omit for protocol/lifecycle-only probe')
    args = parser.parse_args()
    if not local_endpoint(args.endpoint):
        parser.error('M0 probe only permits explicit loopback inference')
    profile = args.profile.resolve()
    prepare(profile, args.lcm, args.endpoint, args.model, args.context_length)
    # Keep the virtualenv executable path: resolving its symlink selects system
    # Python and loses the managed environment's installed packages.
    gateway = Gateway(args.python.absolute(), profile)
    try:
        ready = gateway.wait(lambda e: e.get('params', {}).get('type') == 'gateway.ready')
        print('gateway.ready received', flush=True)
        created = gateway.rpc('session.create', {'cwd': str(profile)})
        print(json.dumps({'session': created}), flush=True)
        sid = created['session_id']
        if args.message:
            print(json.dumps(gateway.rpc('prompt.submit', {'session_id': sid, 'text': args.message})), flush=True)
            complete = gateway.wait(lambda e: e.get('params', {}).get('session_id') == sid
                                    and e.get('params', {}).get('type') in
                                    ('message.complete', 'agent.error', 'session.error'), timeout=240)
            print(json.dumps(complete, ensure_ascii=False), flush=True)
            require_complete(complete)
        print(json.dumps(gateway.rpc('session.status', {'session_id': sid})), flush=True)
    finally:
        gateway.close()
        # Only synthetic test profiles may be used with this development probe.
        (profile / 'protocol.json').write_text(json.dumps(gateway.transcript, indent=2))


if __name__ == '__main__':
    main()
