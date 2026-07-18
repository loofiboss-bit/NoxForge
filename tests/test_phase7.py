from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PhaseSevenNativeStyleTests(unittest.TestCase):
    def test_plugin_has_stable_public_key(self) -> None:
        metadata = json.loads((ROOT / "src/style/noxforgestyleplugin.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["Keys"], ["NoxForge"])

    def test_style_uses_qcommonstyle_without_theme_engine_proxy(self) -> None:
        sources = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "src/style").glob("*"))
            if path.suffix in {".h", ".cpp"}
        )
        self.assertIn("QCommonStyle", sources)
        self.assertNotIn("QProxyStyle", sources)
        self.assertNotIn("Breeze", sources)
        self.assertNotIn("Kvantum", sources)

    def test_style_covers_core_control_families(self) -> None:
        source = (ROOT / "src/style/noxforgestyle.cpp").read_text(encoding="utf-8")
        for control in (
            "PE_PanelButtonCommand",
            "PE_PanelLineEdit",
            "PE_PanelItemViewItem",
            "PE_IndicatorCheckBox",
            "CE_MenuItem",
            "CE_MenuBarItem",
            "CE_ProgressBarContents",
            "CC_ComboBox",
            "CC_SpinBox",
            "CC_GroupBox",
            "CC_Slider",
            "CC_ScrollBar",
        ):
            self.assertIn(control, source)


if __name__ == "__main__":
    unittest.main()
