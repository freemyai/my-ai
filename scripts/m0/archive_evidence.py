#!/usr/bin/env python3
"""Publish a small allowlisted summary of a synthetic chain run, not raw profiles."""
import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    source = json.loads((args.run / 'result.json').read_text())
    result = {key: source[key] for key in ('status', 'scope', 'error', 'child_exit_codes', 'gateway_exit_code', 'compression_scope') if key in source}
    if 'compression' in source:
        result['compression'] = {k: source['compression'][k] for k in
            ('status', 'removed', 'before_messages', 'after_messages', 'before_tokens', 'after_tokens', 'summary')
            if k in source['compression']}
    result['run_name'] = args.run.name
    inference = source.get('inference', {})
    result['inference'] = {key: inference[key] for key in ('choices', 'system_fingerprint', 'usage') if key in inference}
    result['hindsight_health'] = source.get('hindsight_health')
    for key in ('first_message', 'second_message'):
        payload = source.get(key, {}).get('params', {}).get('payload', {})
        result[key] = {k: payload[k] for k in ('text', 'status', 'usage', 'error') if k in payload}
    result['retained_facts'] = [
        {key: row[key] for key in ('text', 'type', 'metadata') if key in row}
        for row in source.get('retained_recall', {}).get('results', [])]
    protocol = args.run / ('myai-' + args.run.name) / 'protocol.json'
    events = json.loads(protocol.read_text()) if protocol.exists() else []
    result['recall_indicators'] = [e['params']['payload']['text'] for e in events
        if 'Hindsight' in str(e.get('params', {}).get('payload', {}).get('text', ''))
        and 'recalled' in str(e.get('params', {}).get('payload', {}).get('text', ''))]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as output:
        output.write(json.dumps(result, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
