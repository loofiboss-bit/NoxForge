from __future__ import annotations

import configparser
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PhaseEightAssetsTests(unittest.TestCase):
    def test_icon_manifest_matches_physical_files(self) -> None:
        root = ROOT / "icons/NoxForge"
        coverage = json.loads((root / "coverage.json").read_text(encoding="utf-8"))
        icons = sorted(path.relative_to(root / "scalable").as_posix() for path in (root / "scalable").glob("*/*.svg"))
        self.assertEqual(coverage["icons"], icons)
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(root / "index.theme", encoding="utf-8")
        self.assertEqual(parser["Icon Theme"]["Inherits"], "hicolor")

    def test_cursors_are_physical_multisize_xcursor_files(self) -> None:
        root = ROOT / "cursors/NoxForge-Cursors"
        cursors = list((root / "cursors").iterdir())
        self.assertGreaterEqual(len(cursors), 90)
        self.assertFalse(any(path.is_symlink() for path in cursors))
        for path in cursors:
            magic, header, version, count = struct.unpack("<4I", path.read_bytes()[:16])
            self.assertEqual((magic, header, version), (0x72756358, 16, 0x00010000))
            self.assertEqual(count, 3)

    def test_sound_events_are_original_encoded_assets(self) -> None:
        root = ROOT / "sounds/NoxForge"
        coverage = json.loads((root / "coverage.json").read_text(encoding="utf-8"))
        events = {path.stem for path in (root / "stereo").glob("*.oga")}
        self.assertEqual(events, set(coverage["events"]))
        self.assertTrue(all(path.read_bytes().startswith(b"OggS") for path in (root / "stereo").glob("*.oga")))
        self.assertGreaterEqual(len(list((root / "source").glob("*.wav"))), 10)


if __name__ == "__main__":
    unittest.main()
