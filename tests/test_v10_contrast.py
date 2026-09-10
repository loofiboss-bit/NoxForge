from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from scripts.check_rendered_contrast import blend, check

ROOT = Path(__file__).resolve().parents[1]


class CompositedContrastTests(unittest.TestCase):
    def setUp(self):
        self.tokens = json.loads((ROOT / 'design/tokens.json').read_text())

    def test_all_state_parent_combinations_meet_contrast(self):
        report = check(self.tokens)
        self.assertEqual(len(report['cases']), 40)

    def test_group_dimming_of_disabled_text_is_rejected(self):
        tokens = copy.deepcopy(self.tokens)
        tokens['states']['hierarchy']['disabled']['opacity'] = 'disabled'
        with self.assertRaisesRegex(ValueError, 'disabled'):
            check(tokens)

    def test_overlay_is_composited_before_contrast(self):
        tokens = copy.deepcopy(self.tokens)
        tokens['overlay']['hover'].update(color='textPrimary', opacity=1.0)
        with self.assertRaisesRegex(ValueError, 'hover'):
            check(tokens)
        self.assertEqual(blend('#FFFFFF', '#000000', 0.5), '#808080')
