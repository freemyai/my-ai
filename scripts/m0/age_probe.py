#!/usr/bin/env python3
"""Test upstream age round-trip and tamper rejection with disposable keys."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bin-dir', type=Path, required=True)
    args = parser.parse_args()
    age = str(args.bin_dir.absolute() / 'age')
    keygen = str(args.bin_dir.absolute() / 'age-keygen')
    with tempfile.TemporaryDirectory(prefix='myai-age-synthetic-') as tmp:
        key = str(Path(tmp) / 'identity.txt')
        subprocess.run([keygen, '-o', key], check=True, capture_output=True)
        recipient = subprocess.check_output([keygen, '-y', key], text=True).strip()
        plaintext = b'My AI synthetic portable identity test\n'
        encrypted = subprocess.run([age, '-r', recipient], input=plaintext,
                                   check=True, capture_output=True).stdout
        recovered = subprocess.run([age, '-d', '-i', key], input=encrypted,
                                   check=True, capture_output=True).stdout
        if recovered != plaintext:
            raise RuntimeError('Round-trip mismatch')
        corrupted = encrypted[:-1] + bytes([encrypted[-1] ^ 1])
        tampered = subprocess.run([age, '-d', '-i', key], input=corrupted, capture_output=True)
        if tampered.returncode == 0:
            raise RuntimeError('Tampered ciphertext was accepted')
        print(json.dumps({'status': 'PASS', 'round_trip': True, 'tamper_rejected': True,
                          'scope': 'upstream crypto CLI only; not My AI export/restore'}))


if __name__ == '__main__':
    main()
