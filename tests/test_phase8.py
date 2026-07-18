from __future__ import annotations

import configparser
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PhaseEightAssetsTests(unittest.TestCase):
    def test_plasma_panel_icon_names_have_physical_icons(self) -> None:
        root = ROOT / "icons/NoxForge/scalable/applets"
        expected = {
            "audio-volume-high-symbolic.svg",
            "battery-full-symbolic.svg",
            "brightness-high-symbolic.svg",
            "camera-on-symbolic.svg",
            "device-notifier.svg",
            "kdeconnect-tray-symbolic.svg",
            "klipper.svg",
            "plasmavault.svg",
            "preferences-desktop-display-randr.svg",
            "preferences-desktop-notification-bell.svg",
        }
        self.assertTrue(expected.issubset({path.name for path in root.glob("*.svg")}))

    def test_common_desktop_mime_names_have_physical_icons(self) -> None:
        root = ROOT / "icons/NoxForge/scalable/mimetypes"
        expected = {
            "application-octet-stream.svg",
            "application-vnd.tcpdump.pcap.svg",
            "application-x-desktop.svg",
            "audio-flac.svg",
            "text-markdown.svg",
            "text-plain.svg",
            "unknown.svg",
            "x-office-document.svg",
        }
        self.assertTrue(expected.issubset({path.name for path in root.glob("*.svg")}))

    def test_icon_manifest_matches_physical_files(self) -> None:
        root = ROOT / "icons/NoxForge"
        coverage = json.loads((root / "coverage.json").read_text(encoding="utf-8"))
        icons = sorted(path.relative_to(root / "scalable").as_posix() for path in (root / "scalable").glob("*/*.svg"))
        self.assertEqual(coverage["icons"], icons)
        self.assertEqual(coverage["schemaVersion"], 2)
        self.assertEqual(coverage["opticalSizes"], [16, 22])
        self.assertEqual(len(coverage["aliases"]), 12)
        self.assertEqual(len(coverage["duplicateAllowlist"]), 10)
        optical = [path for size in (16, 22) for path in (root / f"{size}x{size}").glob("*/*.svg")]
        self.assertEqual(len(optical), coverage["opticalCount"])
        self.assertFalse(any(path.is_symlink() for path in optical))
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(root / "index.theme", encoding="utf-8")
        self.assertEqual(parser["Icon Theme"]["Inherits"], "hicolor")
        valid_contexts = {
            "Actions",
            "Animations",
            "Applications",
            "Categories",
            "Devices",
            "Emblems",
            "Emotes",
            "International",
            "MimeTypes",
            "Places",
            "Status",
        }
        for directory in parser["Icon Theme"]["Directories"].split(","):
            self.assertIn(parser[directory]["Context"], valid_contexts)

    def test_cursors_are_physical_multisize_xcursor_files(self) -> None:
        root = ROOT / "cursors/NoxForge-Cursors"
        cursors = list((root / "cursors").iterdir())
        self.assertGreaterEqual(len(cursors), 90)
        self.assertFalse(any(path.is_symlink() for path in cursors))
        for path in cursors:
            magic, header, version, count = struct.unpack("<4I", path.read_bytes()[:16])
            self.assertEqual((magic, header, version), (0x72756358, 16, 0x00010000))
            expected = 36 if path.name in {"wait", "progress", "watch", "half-busy", "left_ptr_watch"} else 3
            self.assertEqual(count, expected)

    def test_semantic_icons_and_cursors_are_not_aliases(self) -> None:
        icons = ROOT / "icons/NoxForge/scalable"
        for first, second in (
            ("status/audio-volume-high.svg", "status/audio-volume-muted.svg"),
            ("status/battery-good.svg", "status/battery-charging.svg"),
            ("status/network-wireless.svg", "status/network-wireless-disconnected.svg"),
            ("actions/go-next.svg", "actions/go-previous.svg"),
        ):
            self.assertNotEqual((icons / first).read_bytes(), (icons / second).read_bytes())
        cursors = ROOT / "cursors/NoxForge-Cursors/cursors"
        for first, second in (("zoom-in", "zoom-out"), ("up-arrow", "down-arrow"), ("grab", "grabbing")):
            self.assertNotEqual((cursors / first).read_bytes(), (cursors / second).read_bytes())

    def test_wait_and_progress_are_twelve_frame_animations(self) -> None:
        root = ROOT / "cursors/NoxForge-Cursors/cursors"
        for name in ("wait", "progress"):
            data = (root / name).read_bytes()
            count = struct.unpack("<4I", data[:16])[3]
            self.assertEqual(count, 36)
            for offset in range(count):
                position = struct.unpack("<3I", data[16 + offset * 12 : 28 + offset * 12])[2]
                self.assertEqual(struct.unpack("<9I", data[position : position + 36])[8], 80)

    def test_sound_events_are_original_encoded_assets(self) -> None:
        root = ROOT / "sounds/NoxForge"
        coverage = json.loads((root / "coverage.json").read_text(encoding="utf-8"))
        events = {path.stem for path in (root / "stereo").glob("*.oga")}
        self.assertEqual(events, set(coverage["events"]))
        self.assertTrue(all(path.read_bytes().startswith(b"OggS") for path in (root / "stereo").glob("*.oga")))
        self.assertGreaterEqual(len(list((root / "source").glob("*.wav"))), 10)


if __name__ == "__main__":
    unittest.main()
