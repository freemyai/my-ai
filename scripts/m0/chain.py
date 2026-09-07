#!/usr/bin/env python3
"""M0 synthetic integration harness, not the production Orchestrator.

Owns only its child process groups. Requires already provisioned, pinned inputs.
Never downloads implicitly on behalf of a user or attaches to an existing service.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time
from urllib.request import Request, build_opener, ProxyHandler

from gateway_probe import Gateway, child_env, prepare, require_complete

HTTP = build_opener(ProxyHandler({}))


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def request(url, body=None, key=None, timeout=120):
    headers = {'Content-Type': 'application/json'}
    if key:
        headers['Authorization'] = 'Bearer ' + key
    data = None if body is None else json.dumps(body).encode()
    with HTTP.open(Request(url, data=data, headers=headers), timeout=timeout) as response:
        return json.load(response)


def wait_healthy(process, url, key=None, timeout=300):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f'Child exited with {process.returncode}: {url}')
        try:
            return request(url, key=key, timeout=2)
        except (OSError, ValueError):
            time.sleep(1)
    raise TimeoutError(f'Health deadline: {url}')


def message(gateway, sid, text):
    gateway.rpc('prompt.submit', {'session_id': sid, 'text': text})
    event = gateway.wait(lambda e: e.get('params', {}).get('session_id') == sid
                         and e.get('params', {}).get('type') in
                         ('message.complete', 'agent.error', 'session.error'), timeout=300)
    return require_complete(event)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--worker', type=Path, required=True)
    p.add_argument('--model', type=Path, required=True)
    p.add_argument('--hermes-python', type=Path, required=True)
    p.add_argument('--hindsight', type=Path, required=True)
    p.add_argument('--lcm', type=Path, required=True)
    p.add_argument('--embeddings-snapshot', type=Path, required=True)
    p.add_argument('--compression-spike', action='store_true')
    args = p.parse_args()
    if digest(args.model) != '0ad885ffd4bb022fc4f0d33a3308fa108ef8613159d3b3a67e23abca056b7a6c':
        p.error('This synthetic profile requires the pinned Qwen3.5-0.8B Q8_0 artifact')
    embeddings = args.embeddings_snapshot.resolve()
    if digest(embeddings / 'onnx/model.onnx') != 'ca456c06b3a9505ddfd9131408916dd79290368331e7d76bb621f1cba6bc8665':
        p.error('Embedding artifact checksum mismatch')
    for port in (19137, 19188):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', port))  # Fail closed; do not stop other services.
    work = args.work.absolute()
    work.mkdir(parents=True, mode=0o700, exist_ok=False)
    profile = work / ('myai-' + work.name)
    prepare(profile, args.lcm, 'http://127.0.0.1:19137/v1', 'myai-m0')
    preset = work / 'preset.ini'
    preset.write_text('[*]\nparallel = 1\nthreads = 6\nctx-size = 65536\n'
                      'n-gpu-layers = 0\njinja = true\nreasoning = off\n\n'
                      f'[myai-m0]\nmodel = {args.model.resolve()}\n')
    children, logs = [], []
    gateway = None
    result = {'status': 'FAIL', 'scope': 'synthetic M0 CPU smoke, not continuity certification'}

    def start(name, command, env):
        log = (work / (name + '.log')).open('w')
        logs.append(log)
        proc = subprocess.Popen(command, env=env, stdin=subprocess.PIPE,
                                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        children.append(proc)
        return proc

    try:
        env = child_env(profile)
        env['JAN_LLAMA_API_KEY'] = 'myai-local-spike'  # Synthetic loopback credential only.
        worker = start('jan', [str(args.worker.absolute()), '--preset', str(preset),
                                '--port', '19137', '--models-max', '1'], env)
        result['jan_models'] = wait_healthy(worker, 'http://127.0.0.1:19137/v1/models', 'myai-local-spike')
        result['inference'] = request('http://127.0.0.1:19137/v1/chat/completions', {
            'model': 'myai-m0', 'messages': [{'role': 'user', 'content': 'Reply exactly MYAI_JAN_OK'}],
            'max_tokens': 32, 'temperature': 0}, 'myai-local-spike')
        if result['inference'].get('choices', [{}])[0].get('message', {}).get('content', '').strip() != 'MYAI_JAN_OK':
            raise RuntimeError('Jan smoke answer mismatch')
        print('Jan real inference complete', flush=True)
        env = child_env(profile)
        env.update(HINDSIGHT_API_LLM_PROVIDER='openai', HINDSIGHT_API_LLM_MODEL='myai-m0',
                   HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                   HINDSIGHT_API_LLM_BASE_URL='http://127.0.0.1:19137/v1',
                   HINDSIGHT_API_LLM_API_KEY='myai-local-spike',
                   HINDSIGHT_API_DATABASE_URL='pg0://myai-m0-spike',
                   HINDSIGHT_API_EMBEDDINGS_PROVIDER='onnx', HINDSIGHT_API_RERANKER_PROVIDER='rrf',
                   HINDSIGHT_API_EMBEDDINGS_ONNX_MODEL_PATH=str(embeddings / 'onnx/model.onnx'),
                   HINDSIGHT_API_EMBEDDINGS_ONNX_TOKENIZER_NAME_OR_PATH=str(embeddings),
                   HINDSIGHT_API_RETAIN_MAX_COMPLETION_TOKENS='4096',
                   HINDSIGHT_API_LLM_TRACE_ENABLED='false', HINDSIGHT_API_OTEL_TRACES_ENABLED='false')
        memory = start('hindsight', [str(args.hindsight.absolute()), '--host', '127.0.0.1',
                                    '--port', '19188', '--log-level', 'warning'], env)
        result['hindsight_health'] = wait_healthy(memory, 'http://127.0.0.1:19188/health')
        if result['hindsight_health'].get('status') != 'healthy':
            raise RuntimeError('Hindsight health response is not healthy')
        print('Hindsight healthy', flush=True)
        gateway = Gateway(args.hermes_python.absolute(), profile, args.compression_spike)
        gateway.wait(lambda e: e.get('params', {}).get('type') == 'gateway.ready')
        first_session = gateway.rpc('session.create', {'cwd': str(profile)})
        sid = first_session['session_id']
        result['first_message'] = message(gateway, sid,
            'This is synthetic test data: my name is Mira and my favorite flower is blue iris. '
            'Remember this preference. Reply briefly without using tools.')
        print('Hermes first message complete', flush=True)
        recall_url = f'http://127.0.0.1:19188/v1/default/banks/{profile.name}/memories/recall'
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            recalled = request(recall_url, {'query': 'What flower does Mira prefer?',
                                          'types': ['world', 'experience', 'observation'],
                                          'budget': 'low', 'max_tokens': 512})
            if any('iris' in r.get('text', '').lower()
                   and 'mira' in r.get('text', '').lower()
                   and r.get('document_id') == first_session['stored_session_id']
                   for r in recalled.get('results', [])):
                result['retained_recall'] = recalled
                break
            time.sleep(2)
        else:
            raise TimeoutError('Hermes turn did not become recall-visible')
        sid2 = gateway.rpc('session.create', {'cwd': str(profile)})['session_id']
        result['second_message'] = message(gateway, sid2,
            'Which flower does Mira prefer? Read the supplied persistent Hindsight context. '
            'Answer with the flower name only. Do not call tools or guess.')
        result['cross_session_answer_pass'] = result['second_message']['params']['payload']['text'].strip().lower() == 'blue iris'
        if not result['cross_session_answer_pass'] and not args.compression_spike:
            raise RuntimeError('Cross-session response did not contain the retained preference')
        if args.compression_spike:
            result['compression_scope'] = 'manual short-backlog test, leaf_chunk_tokens=512; not overflow certification'
            for turn in range(3):
                text = '\n'.join(f'Synthetic batch {turn}, entry {i}: checksum verified; no personal facts.'
                                 for i in range(35))
                message(gateway, sid2, 'Read this synthetic execution log and reply OK only.\n' + text)
                print(f'Compression fixture turn {turn + 1}/3 complete', flush=True)
            result['compression'] = gateway.rpc('session.compress', {'session_id': sid2})
            if result['compression'].get('removed', 0) <= 0:
                raise RuntimeError('Manual compression did not remove any active messages')
            result['after_compression'] = message(gateway, sid2, 'Reply exactly CONTINUED_OK')
            if result['after_compression']['params']['payload']['text'].strip() != 'CONTINUED_OK':
                raise RuntimeError('Post-compression continuation answer mismatch')
        if not result['cross_session_answer_pass']:
            raise RuntimeError('Cross-session response failed even though remaining probes were exercised')
        result['status'] = 'PASS'
    except Exception as exc:
        result['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        if gateway:
            gateway.close()
            result['gateway_exit_code'] = gateway.proc.returncode
            (profile / 'protocol.json').write_text(json.dumps(gateway.transcript, indent=2))
        result['child_exit_codes'] = []
        for child in reversed(children):
            if child.poll() is None:
                child.stdin.close()
                if child is not children[0]:
                    os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=5)
            result['child_exit_codes'].append(child.returncode)
        for log in logs:
            log.close()
        (work / 'result.json').write_text(json.dumps(result, indent=2))
        print(json.dumps({'status': result['status'], 'evidence': str(work / 'result.json')}), flush=True)


if __name__ == '__main__':
    main()
