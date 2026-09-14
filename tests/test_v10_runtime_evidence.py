import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate_runtime_evidence import validate


class RuntimeEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        evidence = self.root / 'docs/evidence/v11'
        evidence.mkdir(parents=True)
        (evidence / 'qualification.json').write_text(json.dumps({'candidate': {'runtimeSourceHashes': 'hashes.json'}}))
        hashes = {}
        for name in ('VERSION', 'CMakeLists.txt'):
            (self.root / name).write_text('fixture')
            hashes[name] = hashlib.sha256(b'fixture').hexdigest()
        (evidence / 'hashes.json').write_text(json.dumps(hashes))

    def test_current(self):
        self.assertEqual(validate(self.root), [])

    def test_changed_source(self):
        (self.root / 'VERSION').write_text('changed')
        self.assertIn('Stale runtime evidence', ' '.join(validate(self.root)))

    def test_unrecorded_source(self):
        (self.root / 'src').mkdir()
        (self.root / 'src/new.cpp').write_text('new runtime source')
        self.assertIn('coverage differs', ' '.join(validate(self.root)))
