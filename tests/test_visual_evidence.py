from __future__ import annotations

import hashlib
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence"


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


class VisualEvidenceTests(unittest.TestCase):
    def test_ltr_rtl_scale_matrix_has_expected_dimensions_and_unique_data(self) -> None:
        expected = {"100": (960, 760), "125": (1200, 950), "140": (1344, 1064), "200": (1920, 1520)}
        captures: list[Path] = []
        for direction in ("ltr", "rtl"):
            for percent, dimensions in expected.items():
                path = EVIDENCE / f"gallery_{direction}_{percent}pct.png"
                self.assertEqual(png_dimensions(path), dimensions)
                self.assertGreater(path.stat().st_size, 20_000)
                captures.append(path)
        hashes = {hashlib.sha256(path.read_bytes()).digest() for path in captures}
        self.assertEqual(len(hashes), len(captures))

    def test_authentic_sddm_and_contact_sheet_evidence_is_nonempty(self) -> None:
        self.assertEqual(png_dimensions(EVIDENCE / "sddm_login_100pct.png"), (960, 540))
        self.assertEqual(png_dimensions(EVIDENCE / "icons_16_22_24_32_48px.png"), (400, 480))


if __name__ == "__main__":
    unittest.main()
