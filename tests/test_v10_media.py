"""Regression coverage for the media manifest gate."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

SPEC = importlib.util.spec_from_file_location("validate_media", Path(__file__).resolve().parents[1] / "scripts/validate_media.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MediaValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "media").mkdir()
        self.image = self.root / "media/example.png"
        def chunk(kind, payload):
            return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))
        self.image.write_bytes(MODULE.PNG_SIGNATURE + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"\0\0\0\0")) + chunk(b"IEND", b""))
        self.data = {"provenancePolicy": {"live": "Isolated Plasma session", "generated": "Deterministic generator"}, "captures": [{"id": "desktop", "path": "media/example.png", "provenance": "live-isolated-container", "sourceDimensions": "1x1"}], "derivatives": {}}

    def validate(self):
        (self.root / "media/manifest.json").write_text(json.dumps(self.data))
        return MODULE.validate_manifest(self.root)

    def test_valid(self):
        self.assertEqual(self.validate(), [])

    def test_truncated_stream(self):
        self.image.write_bytes(self.image.read_bytes()[:33])
        self.assertIn("requires image data", " ".join(self.validate()))

    def test_bad_crc(self):
        data = bytearray(self.image.read_bytes())
        data[29] ^= 1
        self.image.write_bytes(data)
        self.assertIn("CRC", " ".join(self.validate()))

    def test_trailing_data(self):
        self.image.write_bytes(self.image.read_bytes() + b"junk")
        self.assertIn("invalid PNG end", " ".join(self.validate()))

    def test_missing_file(self):
        self.image.unlink()
        self.assertIn("cannot read", " ".join(self.validate()))

    def test_dimensions(self):
        self.data["captures"][0]["sourceDimensions"] = "2x1"
        self.assertIn("differ from declared", " ".join(self.validate()))

    def test_escape(self):
        self.data["captures"][0]["path"] = "../outside.png"
        self.assertIn("escapes repository", " ".join(self.validate()))

    def test_symlink_escape(self):
        self.image.unlink()
        self.image.symlink_to(self.root.parent / "outside.png")
        self.assertIn("escapes repository", " ".join(self.validate()))

    def test_invalid_provenance(self):
        for value in ("", "invented", "live ", None):
            self.data["captures"][0]["provenance"] = value
            self.assertIn("provenance", " ".join(self.validate()))

    def test_undocumented_provenance(self):
        self.data["provenancePolicy"] = {}
        self.assertIn("undocumented", " ".join(self.validate()))

    def test_derivative_dimensions(self):
        self.data["captures"] = []
        self.data["derivatives"] = {"icon": {"path": "media/example.png", "provenance": "generated", "dimensions": "2x2"}}
        self.assertIn("differ from declared", " ".join(self.validate()))

    def test_duplicates(self):
        self.data["captures"] *= 2
        errors = " ".join(self.validate())
        self.assertIn("duplicate id", errors)
        self.assertIn("duplicate path", errors)

    def test_invalid_png(self):
        self.image.write_bytes(b"not a PNG")
        self.assertIn("invalid PNG", " ".join(self.validate()))


if __name__ == "__main__":
    unittest.main()
