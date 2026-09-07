"""M0 invariants: ownership isolation, atomic outbox and safe probe execution."""
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from gateway_probe import Gateway, local_endpoint, child_env, require_complete

SCHEMA = Path(__file__).resolve().parents[2] / 'vault-schema/v0.1/schema.sql'


class VaultContract(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.executescript(SCHEMA.read_text())
        self.db.execute("INSERT INTO owners VALUES ('owner', 'Owner')")
        for ai in ('alice', 'bob'):
            self.db.execute('INSERT INTO ais VALUES (?, ?, ?, ?, ?)',
                            (ai, 'owner', ai, '{}', '2026-09-07T00:00:00Z'))
        self.db.execute("INSERT INTO provenance VALUES ('alice','p1','owner','said','{}','now')")
        self.db.execute("INSERT INTO conversations VALUES ('alice','c1','Synthetic','now')")
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_cross_ai_source_is_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO records VALUES ('bob','r1','memory',1,'active','{}','p1','now','now')")

    def test_cross_ai_conversation_is_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO messages VALUES ('bob','m1','c1',0,'user','{}','p1','now')")

    def test_outbox_cannot_reference_missing_event(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO materialization_outbox VALUES ('alice','missing','hindsight','pending',0,NULL)")

    def test_message_and_outbox_roll_back_together(self):
        with self.assertRaises(RuntimeError):
            with self.db:
                self.db.execute("INSERT INTO messages VALUES ('alice','m1','c1',0,'user','{}','p1','now')")
                self.db.execute("INSERT INTO materialization_outbox VALUES ('alice','p1','hindsight','pending',0,NULL)")
                raise RuntimeError('simulated interruption before commit')
        self.assertEqual(self.db.execute('SELECT count(*) FROM messages').fetchone()[0], 0)
        self.assertEqual(self.db.execute('SELECT count(*) FROM materialization_outbox').fetchone()[0], 0)

    def test_duplicate_materialization_is_rejected(self):
        sql = "INSERT INTO materialization_outbox VALUES ('alice','p1','hindsight','pending',0,NULL)"
        self.db.execute(sql)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(sql)


class ProbeContract(unittest.TestCase):
    def test_completion_envelope_is_not_success(self):
        for status in ('error', 'cancelled', None):
            with self.assertRaises(RuntimeError):
                require_complete({'params': {'type': 'message.complete', 'payload': {'status': status}}})

    def test_explicit_success_is_accepted(self):
        event = {'params': {'type': 'message.complete', 'payload': {'status': 'complete', 'text': 'OK'}}}
        self.assertEqual(require_complete(event), event)

    def test_rpc_does_not_drop_early_events(self):
        import queue
        gateway = Gateway.__new__(Gateway)
        gateway.pending, gateway.transcript = [], []
        gateway.events = queue.Queue()
        early = {'params': {'type': 'message.complete', 'session_id': 'synthetic'}}
        reply = {'id': 1, 'result': {}}
        gateway.events.put(early)
        gateway.events.put(reply)
        self.assertEqual(gateway.wait(lambda e: e.get('id') == 1), reply)
        self.assertEqual(gateway.wait(lambda e: 'params' in e), early)
        self.assertEqual(gateway.transcript, [early, reply])

    def test_local_url_does_not_accept_userinfo_trick(self):
        self.assertTrue(local_endpoint('http://127.0.0.1:19137/v1'))
        for endpoint in ('https://example.com/v1', 'http://127.0.0.1:123@evil.example/v1',
                         'http://127.0.0.1.evil.example:80/v1'):
            self.assertFalse(local_endpoint(endpoint))

    def test_child_environment_does_not_inherit_credentials(self):
        from unittest.mock import patch
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'synthetic', 'OPENROUTER_API_KEY': 'synthetic',
                                     'HTTP_PROXY': 'http://example.com'}):
            env = child_env(Path('/tmp/myai-synthetic'))
        self.assertNotIn('ANTHROPIC_API_KEY', env)
        self.assertNotIn('OPENROUTER_API_KEY', env)
        self.assertNotIn('HTTP_PROXY', env)

    def test_virtualenv_executable_must_keep_its_symlink_path(self):
        import sys
        with tempfile.TemporaryDirectory(prefix='myai-venv-regression-') as tmp:
            subprocess.run([sys.executable, '-m', 'venv', '--without-pip', tmp], check=True)
            python = Path(tmp) / 'bin/python'
            prefix = subprocess.check_output([str(python.absolute()), '-c', 'import sys; print(sys.prefix)'], text=True).strip()
            self.assertEqual(prefix, tmp)


if __name__ == '__main__':
    unittest.main()
