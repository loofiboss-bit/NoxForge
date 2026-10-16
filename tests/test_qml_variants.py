from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QML_CONFIG = ROOT / "design/qml-variants.json"


class QmlVariantsContractTests(unittest.TestCase):
    def test_qml_variants_schema_and_mapping(self) -> None:
        self.assertTrue(QML_CONFIG.is_file(), "qml-variants.json must exist")
        data = json.loads(QML_CONFIG.read_text(encoding="utf-8"))
        self.assertIn(data.get("schemaVersion"), (1, 2))
        targets = data.get("targets", [])
        self.assertGreaterEqual(len(targets), 3)

        for target in targets:
            source = target.get("source")
            self.assertTrue(source, "source path must be defined")
            source_path = ROOT / source
            self.assertTrue(source_path.is_file(), f"canonical source must exist: {source}")

            outputs = target.get("outputs", [])
            self.assertGreaterEqual(len(outputs), 2, f"target {source} must map to at least 2 variants")
            source_body = source_path.read_text(encoding="utf-8")
            expected_header = f"// GENERATED from {source} — do not edit directly\n"

            for out_rel in outputs:
                out_path = ROOT / out_rel
                self.assertTrue(out_path.is_file(), f"output must exist: {out_rel}")
                out_content = out_path.read_text(encoding="utf-8")
                self.assertTrue(
                    out_content.startswith(expected_header),
                    f"{out_rel} must have the GENERATED header from {source}",
                )
                self.assertEqual(
                    out_content[len(expected_header):],
                    source_body,
                    f"{out_rel} body must match canonical source {source} exactly",
                )


if __name__ == "__main__":
    unittest.main()
