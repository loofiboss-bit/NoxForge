from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads(
    (ROOT / "design/v7-session-contract.json").read_text(encoding="utf-8")
)
SDDM = (ROOT / "sddm/NoxForge/Main.qml").read_text(encoding="utf-8")
LOGOUT = (
    ROOT / "look-and-feel/io.github.loofiboss.noxforge.desktop/contents/logout/Logout.qml"
).read_text(encoding="utf-8")
TABBOX = (
    ROOT / "kwin/tabbox/io.github.loofiboss.noxforge.desktop/contents/ui/Switcher.qml"
).read_text(encoding="utf-8")
CMAKE = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8")


class V7PhaseFiveTests(unittest.TestCase):
    def test_sddm_preserves_authentication_boundary_and_uses_real_busy_indicator(self) -> None:
        for call in CONTRACT["authenticationBoundary"]["preservedCalls"]:
            self.assertIn(call, SDDM)
        self.assertIn("QQC2.BusyIndicator", SDDM)
        self.assertNotIn("↻", SDDM)
        self.assertNotRegex(SDDM, r"credential|password.*(?:write|store|save)")
        self.assertFalse(CONTRACT["authenticationBoundary"]["credentialStorageAdded"])
        self.assertFalse(CONTRACT["authenticationBoundary"]["hostConfigurationMutation"])

    def test_sddm_exposes_stable_feedback_caps_lock_layout_and_session(self) -> None:
        for fragment in (
            "KeyboardIndicator.KeyState",
            'qsTr("Caps Lock is on")',
            "Layout.minimumHeight: 40",
            "Layout.maximumHeight: 40",
            "Qt.callLater(root.focusFirstAction)",
            "keyboard.layouts[keyboard.currentLayout]",
            'qsTr("Choose session")',
            "onLoginFailed",
            "onLoginSucceeded",
        ):
            self.assertIn(fragment, SDDM)
        tokens = json.loads((ROOT / "design/tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["geometry"]["largeControlHeight"], 40)

    def test_logout_actions_have_distinct_owned_semantics(self) -> None:
        icon_names = CONTRACT["logout"]["distinctActionIcons"]
        self.assertEqual(len(icon_names), len(set(icon_names)))
        for icon_name in icon_names:
            self.assertIn(f'iconName: "{icon_name}"', LOGOUT)
            self.assertTrue(
                (ROOT / f"icons/NoxForge/scalable/actions/{icon_name}.svg").is_file()
            )

    def test_tabbox_covers_identity_fallback_states_and_keyboard_activation(self) -> None:
        for role in CONTRACT["tabbox"]["modelRoles"]:
            expected_type = "var" if role == "icon" else "bool" if role == "minimized" else "string"
            self.assertIn(f"required property {expected_type} {role}", TABBOX)
        self.assertIn(CONTRACT["tabbox"]["missingIconFallback"], TABBOX)
        self.assertIn("Keys.onReturnPressed", TABBOX)
        self.assertIn("Keys.onSpacePressed", TABBOX)
        self.assertIn("Accessible.role: Accessible.List", TABBOX)
        self.assertIn("Accessible.role: Accessible.ListItem", TABBOX)
        for scenario in ("empty", "many", "keyboard", "missing-icon"):
            self.assertRegex(CMAKE, rf"session-tabbox-{re.escape(scenario)}\b")

    def test_each_session_surface_has_the_full_offscreen_scale_matrix(self) -> None:
        self.assertEqual(CONTRACT["offscreenScaleMatrix"], [100, 125, 140, 150, 200])
        self.assertRegex(CMAKE, r"foreach\(scale IN ITEMS 1\.0 1\.25 1\.4 1\.5 2\.0\)")
        for surface in ("sddm", "splash", "logout", "tabbox"):
            self.assertIn(f"session-{surface}-scale-${{scale_id}}", CMAKE)
        self.assertEqual(CONTRACT["mixedDpi"]["status"], "pending-live")
        self.assertFalse(CONTRACT["liveQualification"]["qualifiesLiveSession"])

    def test_phase_five_sources_do_not_mutate_or_activate_host_configuration(self) -> None:
        combined = "\n".join((SDDM, LOGOUT, TABBOX))
        for forbidden in (
            "plasma-apply-lookandfeel",
            "kwriteconfig",
            "resetLayout",
            "systemctl",
        ):
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
