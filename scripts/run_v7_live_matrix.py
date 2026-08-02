#!/usr/bin/env python3
"""Run the input-capable v7 matrix in disposable KWin Wayland sessions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
THEME_ID = "io.github.loofiboss.noxforge.desktop"
QML_LAUNCHER = shutil.which("qml") or "/usr/lib64/qt6/bin/qml"
SINGLE_SCALES = (1.0, 1.25, 1.4, 1.5, 1.75, 2.0)
MIXED_SCALES = ((1.0, 1.4), (1.0, 2.0))
META = 125
SHIFT = 42
ALT = 56
TAB = 15
UP = 103
DOWN = 108
LEFT = 105
RIGHT = 106
ESC = 1
F = 33
F11 = 87


def run(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    check: bool = True,
    capture: bool = True,
    timeout: int = 60,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        timeout=timeout,
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_size(path: Path) -> list[int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"invalid PNG evidence: {path}")
    return list(struct.unpack(">II", header[16:24]))


def verify_maximized_capture(path: Path, desktop: Path) -> None:
    with Image.open(path) as source:
        image = source.convert("RGB")
    with Image.open(desktop) as source:
        background = source.convert("RGB")
    if image.size != background.size:
        raise RuntimeError(f"capture size changed relative to desktop baseline: {path}")
    width, height = image.size
    bounds = ImageChops.difference(image, background).getbbox()
    # Aurorae's maximized outer shadow leaves a symmetric five-pixel capture
    # margin and Plasma reserves its panel. The changed application surface
    # must otherwise span the complete output in both axes.
    if (
        bounds is None
        or bounds[0] > 8
        or bounds[1] > 8
        or bounds[2] < width - 8
        or bounds[3] < height - 100
    ):
        raise RuntimeError(f"capture is not maximized across the output: {path}")


def scale_label(scale: float) -> str:
    return str(round(scale * 100))


def isolated_environment(root: Path) -> dict[str, str]:
    directories = {
        "HOME": root / "home",
        "XDG_CONFIG_HOME": root / "config",
        "XDG_DATA_HOME": root / "data",
        "XDG_CACHE_HOME": root / "cache",
        "XDG_RUNTIME_DIR": root / "runtime",
    }
    for key, directory in directories.items():
        directory.mkdir(parents=True, exist_ok=True)
        directory.chmod(0o700 if key == "XDG_RUNTIME_DIR" else 0o755)
    env = os.environ.copy()
    env.update({key: str(value) for key, value in directories.items()})
    env.update(
        {
            "DESKTOP_SESSION": "plasma",
            "KDE_FULL_SESSION": "true",
            "KDE_SESSION_VERSION": "6",
            "QT_QPA_PLATFORM": "wayland",
            "XCURSOR_THEME": "NoxForge-Cursors",
            "XDG_CURRENT_DESKTOP": "KDE",
            "XDG_SESSION_TYPE": "wayland",
        }
    )
    (directories["XDG_CONFIG_HOME"] / "plasma-welcomerc").write_text(
        "[General]\nLastSeenVersion=6.7.3\n", encoding="utf-8", newline="\n"
    )
    return env


def require_tools(injector: Path) -> None:
    required = (
        "dbus-run-session",
        "dolphin",
        "firefox",
        "kdialog",
        "konsole",
        "kscreen-doctor",
        "kwin_wayland",
        "plasma-apply-lookandfeel",
        "plasmashell",
        "pipewire",
        "qdbus-qt6",
        "spectacle",
        "systemsettings",
        "wireplumber",
    )
    missing = [tool for tool in required if shutil.which(tool) is None]
    if not Path(QML_LAUNCHER).is_file():
        missing.append("qml")
    if not os.environ.get("DISPLAY") and shutil.which("Xvfb") is None:
        missing.append("Xvfb")
    if missing:
        raise RuntimeError("missing live qualification tools: " + ", ".join(missing))
    if not injector.is_file() or not os.access(injector, os.X_OK):
        raise RuntimeError(f"input helper is not executable: {injector}")


def install_theme(env: dict[str, str]) -> None:
    result = run([str(ROOT / "scripts/install.sh"), "--user"], env=env)
    if "No KDE settings were changed" not in result.stdout:
        raise RuntimeError("isolated user installation did not confirm its non-applying boundary")


def stage_system_lookandfeel(env: dict[str, str]) -> None:
    source = Path("/usr/share/plasma/look-and-feel") / THEME_ID
    destination = Path(env["XDG_DATA_HOME"]) / "plasma/look-and-feel" / THEME_ID
    if not source.is_dir():
        raise RuntimeError(f"verified system look-and-feel payload is missing: {source}")
    shutil.copytree(source, destination)
    source_files = {
        path.relative_to(source).as_posix(): sha256(path)
        for path in source.rglob("*")
        if path.is_file()
    }
    destination_files = {
        path.relative_to(destination).as_posix(): sha256(path)
        for path in destination.rglob("*")
        if path.is_file()
    }
    if source_files != destination_files:
        raise RuntimeError("isolated look-and-feel staging changed the verified RPM payload")


def stage_prestart_defaults(env: dict[str, str], defaults: Path) -> None:
    text = defaults.read_text(encoding="utf-8")
    required = (
        "widgetStyle=NoxForge",
        "ColorScheme=NoxForgeDark",
        "Theme=NoxForge",
        "cursorTheme=NoxForge-Cursors",
        "library=org.kde.kwin.aurorae",
        f"theme=__aurorae__svg__{THEME_ID}",
        f"LayoutName={THEME_ID}",
    )
    missing = [entry for entry in required if entry not in text]
    if missing:
        raise RuntimeError("look-and-feel defaults are incomplete: " + ", ".join(missing))
    config = Path(env["XDG_CONFIG_HOME"])
    payloads = {
        "kdeglobals": (
            f"[KDE]\nLookAndFeelPackage={THEME_ID}\nwidgetStyle=NoxForge\n\n"
            "[General]\nColorScheme=NoxForgeDark\n\n"
            "[Icons]\nTheme=NoxForge\n\n[Sounds]\nTheme=NoxForge\n"
        ),
        "plasmarc": f"[Theme]\nname={THEME_ID}\n",
        "kcminputrc": "[Mouse]\ncursorTheme=NoxForge-Cursors\n",
        "kwinrc": (
            "[org.kde.kdecoration2]\nlibrary=org.kde.kwin.aurorae\n"
            f"theme=__aurorae__svg__{THEME_ID}\n\n[TabBox]\nLayoutName={THEME_ID}\n"
        ),
        "ksplashrc": f"[KSplash]\nTheme={THEME_ID}\n",
    }
    for name, payload in payloads.items():
        (config / name).write_text(payload, encoding="utf-8", newline="\n")
    env["NOXFORGE_LIVE_PRESTAGED"] = "verified look-and-feel defaults"


def verify_system_package() -> dict[str, object]:
    nevra = run(["rpm", "-q", "noxforge"]).stdout.strip()
    verification = run(["rpm", "-V", "noxforge"], check=False)
    if verification.returncode != 0 or verification.stdout.strip():
        raise RuntimeError("installed NoxForge RPM failed verification: " + verification.stdout)
    doctor = json.loads(run([str(ROOT / "tools/noxforge-doctor"), "--json"]).stdout)
    if doctor.get("status") != "ok" or doctor.get("missing"):
        raise RuntimeError("installed NoxForge package failed doctor readback")
    return {
        "nevra": nevra,
        "rpmVerify": "passed",
        "doctorStatus": doctor["status"],
        "expectedVersion": doctor.get("expectedVersion"),
        "packageVersion": doctor.get("packageVersion"),
        "mixedVersions": doctor.get("mixedVersions"),
    }


def wait_for_service(service: str, path: str, timeout_seconds: int = 30) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        result = run(["qdbus-qt6", service, path], check=False, timeout=5)
        if result.returncode == 0:
            return
        time.sleep(0.25)
    raise RuntimeError(f"timed out waiting for {service}{path}")


class LiveSession:
    def __init__(self, args: argparse.Namespace, evidence: Path) -> None:
        self.args = args
        self.evidence = evidence
        self.socket = args.socket
        self.processes: list[subprocess.Popen[str]] = []
        self.kwin: subprocess.Popen[str] | None = None
        self.desktop_capture: Path | None = None
        self.script_counter = 0
        self.log = evidence / "session.log"
        self.log_handle = self.log.open("w", encoding="utf-8")

    def start(self) -> None:
        self.kwin = subprocess.Popen(
            [
                "kwin_wayland",
                "--virtual",
                "--width",
                "1920",
                "--height",
                "1080",
                "--scale",
                "1",
                "--output-count",
                str(self.args.outputs),
                "--socket",
                self.socket,
                "--no-lockscreen",
                "--exit-with-session",
                "/usr/bin/plasmashell",
            ],
            cwd=ROOT,
            text=True,
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
        )
        wait_for_service("org.kde.KWin", "/KWin")
        os.environ["WAYLAND_DISPLAY"] = self.socket
        if not os.environ.get("DISPLAY"):
            xvfb = self.launch(
                ["Xvfb", ":99", "-screen", "0", "1280x720x24", "-nolisten", "tcp"],
                wait_seconds=0.5,
            )
            if xvfb.poll() is not None:
                raise RuntimeError("qualification Xvfb bridge exited early")
            os.environ["DISPLAY"] = ":99"
        if not (Path(os.environ["XDG_RUNTIME_DIR"]) / "pipewire-0").exists():
            self.launch(["pipewire"], wait_seconds=1)
            self.launch(["wireplumber"], wait_seconds=1)
        current_package = run(
            ["kreadconfig6", "--file", "kdeglobals", "--group", "KDE", "--key", "LookAndFeelPackage"]
        ).stdout.strip()
        if not current_package:
            run(
                [
                    "kwriteconfig6",
                    "--file",
                    "kdeglobals",
                    "--group",
                    "KDE",
                    "--key",
                    "LookAndFeelPackage",
                    "org.kde.breeze.desktop",
                ]
            )
        result = run(
            ["plasma-apply-lookandfeel", "--keep-auto", "--apply", THEME_ID],
            timeout=30,
        )
        (self.evidence / "lookandfeel-apply.txt").write_text(
            result.stdout, encoding="utf-8", newline="\n"
        )
        if result.returncode != 0:
            raise RuntimeError("isolated Global Theme application failed: " + result.stdout)
        activation_method = (
            "verified defaults staged before compositor plus plasma-apply-lookandfeel"
            if os.environ.get("NOXFORGE_LIVE_PRESTAGED")
            else "plasma-apply-lookandfeel"
        )
        decoration = run(
            [
                "kreadconfig6",
                "--file",
                "kwinrc",
                "--group",
                "org.kde.kdecoration2",
                "--key",
                "theme",
            ]
        ).stdout.strip()
        if self.args.system_package and decoration != f"__aurorae__svg__{THEME_ID}":
            self.stage_headless_defaults()
            activation_method = "verified RPM defaults staged after headless apply limitation"
        run(["qdbus-qt6", "org.kde.KWin", "/KWin", "reconfigure"])
        time.sleep(1)
        readback = {
            "activationMethod": activation_method,
            "decorationLibrary": run(
                ["kreadconfig6", "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", "library"]
            ).stdout.strip(),
            "decorationTheme": run(
                ["kreadconfig6", "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", "theme"]
            ).stdout.strip(),
            "cursorTheme": run(
                ["kreadconfig6", "--file", "kcminputrc", "--group", "Mouse", "--key", "cursorTheme"]
            ).stdout.strip(),
        }
        (self.evidence / "active-theme.json").write_text(
            json.dumps(readback, indent=2) + "\n", encoding="utf-8", newline="\n"
        )

    def stage_headless_defaults(self) -> None:
        defaults = Path("/usr/share/plasma/look-and-feel") / THEME_ID / "contents/defaults"
        text = defaults.read_text(encoding="utf-8")
        required = (
            "widgetStyle=NoxForge",
            "ColorScheme=NoxForgeDark",
            "Theme=NoxForge",
            "cursorTheme=NoxForge-Cursors",
            "library=org.kde.kwin.aurorae",
            f"theme=__aurorae__svg__{THEME_ID}",
            f"LayoutName={THEME_ID}",
        )
        missing = [entry for entry in required if entry not in text]
        if missing:
            raise RuntimeError("verified RPM defaults are incomplete: " + ", ".join(missing))
        values = (
            ("kdeglobals", "KDE", "LookAndFeelPackage", THEME_ID),
            ("kdeglobals", "KDE", "widgetStyle", "NoxForge"),
            ("kdeglobals", "General", "ColorScheme", "NoxForgeDark"),
            ("kdeglobals", "Icons", "Theme", "NoxForge"),
            ("kdeglobals", "Sounds", "Theme", "NoxForge"),
            ("plasmarc", "Theme", "name", THEME_ID),
            ("kcminputrc", "Mouse", "cursorTheme", "NoxForge-Cursors"),
            ("kwinrc", "org.kde.kdecoration2", "library", "org.kde.kwin.aurorae"),
            ("kwinrc", "org.kde.kdecoration2", "theme", f"__aurorae__svg__{THEME_ID}"),
            ("kwinrc", "TabBox", "LayoutName", THEME_ID),
            ("ksplashrc", "KSplash", "Theme", THEME_ID),
        )
        for filename, group, key, value in values:
            run(
                [
                    "kwriteconfig6",
                    "--file",
                    filename,
                    "--group",
                    group,
                    "--key",
                    key,
                    value,
                ]
            )

    def configure_outputs(self) -> None:
        commands: list[str] = []
        position = 0
        for index, scale in enumerate(self.args.scales):
            output = f"Virtual-{index}"
            commands.extend(
                [
                    f"output.{output}.enable",
                    f"output.{output}.scale.{scale:g}",
                    f"output.{output}.position.{position},0",
                ]
            )
            position += round(1920 / scale)
        result = run(["kscreen-doctor", *commands], timeout=30)
        (self.evidence / "output-change.txt").write_text(result.stdout, encoding="utf-8")
        time.sleep(2)
        self.record_runtime()
        self.desktop_capture = self.screenshot("desktop-baseline")

    def record_runtime(self) -> None:
        outputs = run(["kscreen-doctor", "-o"], timeout=30).stdout
        support = run(["qdbus-qt6", "org.kde.KWin", "/KWin", "supportInformation"]).stdout
        (self.evidence / "outputs.txt").write_text(outputs, encoding="utf-8")
        (self.evidence / "kwin-support.txt").write_text(support, encoding="utf-8")
        expected = [f"Scale: \x1b[0;0m{scale:g}" for scale in self.args.scales]
        if not all(fragment in outputs for fragment in expected):
            plain_expected = [f"Scale: {scale:g}" for scale in self.args.scales]
            plain = outputs.replace("\x1b[01;33m", "").replace("\x1b[0;0m", "")
            if not all(fragment in plain for fragment in plain_expected):
                raise RuntimeError("KScreen did not read back every requested scale")
        required_support = (
            "Operation Mode: Wayland",
            "Theme: __aurorae__svg__io.github.loofiboss.noxforge.desktop",
            "Name: KWin::VirtualBackend",
        )
        missing = [fragment for fragment in required_support if fragment not in support]
        if missing:
            raise RuntimeError("KWin runtime readback is incomplete: " + ", ".join(missing))

    def input(self, *arguments: object, check: bool = True) -> subprocess.CompletedProcess[str]:
        command = [str(self.args.injector), *(str(argument) for argument in arguments)]
        return run(command, check=check, timeout=20)

    def launch(
        self,
        command: list[str],
        *,
        env: dict[str, str] | None = None,
        wait_seconds: float = 3.0,
        require_running: bool = True,
    ) -> subprocess.Popen[str]:
        child_env = os.environ.copy()
        if env:
            child_env.update(env)
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=child_env,
            text=True,
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
        )
        self.processes.append(process)
        time.sleep(wait_seconds)
        if require_running and process.poll() is not None:
            raise RuntimeError(f"live application exited early: {' '.join(command)}")
        return process

    def stop_process(self, process: subprocess.Popen[str]) -> None:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if process in self.processes:
            self.processes.remove(process)

    def screenshot(self, name: str) -> Path:
        path = self.evidence / f"{name}.png"
        result = run(["spectacle", "-b", "-n", "-o", str(path)], check=False, timeout=30)
        if result.returncode != 0 or not path.is_file() or path.stat().st_size < 2_000:
            raise RuntimeError(f"Spectacle capture failed for {name}: {result.stdout}")
        return path

    def focus_window(self) -> None:
        self.input("absolute", 700, 300)
        self.input("click")
        time.sleep(0.4)

    def maximize(self) -> None:
        self.focus_window()
        self.kwin_script("workspace.activeWindow.setMaximize(true, true);")
        time.sleep(1)

    def restore(self) -> None:
        self.kwin_script("workspace.activeWindow.setMaximize(false, false);")
        time.sleep(1)

    def kwin_script(self, statement: str) -> None:
        self.script_counter += 1
        plugin = f"noxforge-v7-live-{self.script_counter}"
        path = Path(os.environ["XDG_RUNTIME_DIR"]) / f"{plugin}.js"
        path.write_text(statement + "\n", encoding="utf-8", newline="\n")
        loaded = run(
            [
                "qdbus-qt6",
                "org.kde.KWin",
                "/Scripting",
                "org.kde.kwin.Scripting.loadScript",
                str(path),
                plugin,
            ]
        )
        if loaded.stdout.strip() in ("", "-1"):
            raise RuntimeError(f"KWin rejected qualification script: {statement}")
        run(["qdbus-qt6", "org.kde.KWin", "/Scripting", "org.kde.kwin.Scripting.start"])
        time.sleep(0.3)
        run(
            [
                "qdbus-qt6",
                "org.kde.KWin",
                "/Scripting",
                "org.kde.kwin.Scripting.unloadScript",
                plugin,
            ],
            check=False,
        )

    def plasma_script(self, statement: str) -> None:
        result = run(
            [
                "qdbus-qt6",
                "org.kde.plasmashell",
                "/PlasmaShell",
                "org.kde.PlasmaShell.evaluateScript",
                statement,
            ]
        )
        if "Error" in result.stdout:
            raise RuntimeError(f"Plasma rejected qualification script: {result.stdout}")
        time.sleep(1)

    def close(self) -> None:
        for process in list(reversed(self.processes)):
            self.stop_process(process)
        if self.kwin and self.kwin.poll() is None:
            self.kwin.terminate()
            try:
                self.kwin.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.kwin.kill()
                self.kwin.wait(timeout=5)
        self.log_handle.close()


def application_capture(session: LiveSession, command: list[str], label: str) -> None:
    process = session.launch(command)
    session.maximize()
    capture = session.screenshot(label)
    if session.desktop_capture is None:
        raise RuntimeError("desktop baseline was not captured")
    verify_maximized_capture(capture, session.desktop_capture)
    session.restore()
    session.input("keys", "--hold-ms", 100, TAB)
    session.input("keys", "--hold-ms", 100, TAB)
    session.screenshot(f"{label}-restored-focus")
    session.stop_process(process)


def icon_gallery_capture(session: LiveSession) -> None:
    gallery = Path(os.environ["XDG_RUNTIME_DIR"]) / "noxforge-v7-icon-gallery.qml"
    gallery.write_text(
        """import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

ApplicationWindow {
    visible: true
    width: 960
    height: 540
    title: "NoxForge v7 core icon visibility"
    color: "#0E1318"
    GridLayout {
        anchors.centerIn: parent
        columns: 3
        columnSpacing: 42
        rowSpacing: 28
        Repeater {
            model: [
                "draw-highlight", "view-hidden", "tools-report-bug",
                "system-suspend", "system-reboot", "system-shutdown",
                "system-lock-screen", "system-log-out", "document-print"
            ]
            delegate: ColumnLayout {
                required property string modelData
                Kirigami.Icon {
                    Layout.alignment: Qt.AlignHCenter
                    source: modelData
                    implicitWidth: 48
                    implicitHeight: 48
                }
                Label {
                    text: modelData
                    color: "#E8F0F2"
                }
            }
        }
    }
}
""",
        encoding="utf-8",
        newline="\n",
    )
    process = session.launch([QML_LAUNCHER, str(gallery)])
    session.maximize()
    session.screenshot("core-icon-gallery-140")
    session.stop_process(process)


def single_case(session: LiveSession) -> None:
    scale = session.args.scales[0]
    label = scale_label(scale)
    application_capture(
        session,
        ["systemsettings"],
        f"systemsettings-maximized-{label}",
    )
    if scale not in (1.0, 1.4, 2.0):
        return
    application_capture(session, ["dolphin", str(ROOT)], f"dolphin-maximized-{label}")
    application_capture(session, ["konsole"], f"konsole-maximized-{label}")

    if scale != 1.4:
        return

    process = session.launch(["systemsettings"])
    session.focus_window()
    session.input("keys", "--hold-ms", 120, META, LEFT)
    time.sleep(1)
    session.screenshot("systemsettings-quick-tile-left-140")
    session.input("keys", "--hold-ms", 120, META, RIGHT)
    session.input("keys", "--hold-ms", 120, META, RIGHT)
    time.sleep(1)
    session.screenshot("systemsettings-quick-tile-right-140")
    session.kwin_script("workspace.activeWindow.minimized = true;")
    session.screenshot("systemsettings-minimized-task-140")
    session.kwin_script(
        'const windows = workspace.windowList(); for (const w of windows) '
        'if (w.caption.includes("System Settings")) w.minimized = false;'
    )
    session.stop_process(process)

    process = session.launch(["konsole"])
    session.focus_window()
    session.input("keys", "--hold-ms", 120, F11)
    time.sleep(1)
    session.screenshot("konsole-fullscreen-140")
    session.input("keys", "--hold-ms", 120, F11)
    session.stop_process(process)

    process = session.launch(["systemsettings"])
    for _ in range(5):
        session.input("keys", "--hold-ms", 80, TAB)
    session.screenshot("systemsettings-keyboard-focus-140")
    session.stop_process(process)

    process = session.launch(["konsole"])
    session.input("keys", "--hold-ms", 200, ALT, F)
    time.sleep(1)
    session.screenshot("konsole-alt-mnemonic-140")
    session.input("keys", "--hold-ms", 80, ESC)
    session.stop_process(process)

    process = session.launch(["systemsettings"], env={"QT_LAYOUT_DIRECTION": "rtl"})
    session.maximize()
    session.screenshot("systemsettings-rtl-140")
    session.stop_process(process)

    process = session.launch(["systemsettings"], env={"LANGUAGE": "x-test"})
    session.maximize()
    session.screenshot("systemsettings-translation-expansion-140")
    session.stop_process(process)

    firefox_profile = Path(os.environ["XDG_RUNTIME_DIR"]) / "firefox-profile"
    firefox_profile.mkdir(parents=True, exist_ok=True)
    application_capture(
        session,
        [
            "firefox",
            "--new-instance",
            "--no-remote",
            "--profile",
            str(firefox_profile),
            "about:blank",
        ],
        "firefox-maximized-140",
    )

    dialog = session.launch(
        ["kdialog", "--title", "NoxForge v7", "--msgbox", "Operational Precision dialog"]
    )
    session.screenshot("qt-dialog-140")
    session.input("keys", "--hold-ms", 80, TAB)
    session.screenshot("qt-dialog-keyboard-focus-140")
    session.stop_process(dialog)

    icon_gallery_capture(session)

    for edge in ("bottom", "top", "left", "right"):
        session.plasma_script(
            f'const p = panels(); if (p.length !== 1) throw "expected one panel"; '
            f'p[0].location = "{edge}";'
        )
        session.screenshot(f"plasma-panel-{edge}-140")
    session.plasma_script('panels()[0].location = "bottom";')

    session.input("keys", "--hold-ms", 100, META)
    time.sleep(1)
    session.screenshot("plasma-launcher-140")
    session.input("keys", "--hold-ms", 80, ESC)

    notification = run(
        ["notify-send", "--print-id", "NoxForge v7", "Operational Precision live notification"]
    )
    time.sleep(1)
    session.screenshot("plasma-notification-140")

    run(
        [
            "qdbus-qt6",
            "org.kde.plasmashell",
            "/org/kde/osdService",
            "org.kde.osdService.showText",
            "preferences-desktop-theme",
            "NoxForge v7 Operational Precision",
        ]
    )
    time.sleep(1)
    session.screenshot("plasma-osd-140")

    notification_id = notification.stdout.strip()
    if notification_id.isdigit():
        run(
            [
                "qdbus-qt6",
                "org.freedesktop.Notifications",
                "/org/freedesktop/Notifications",
                "org.freedesktop.Notifications.CloseNotification",
                notification_id,
            ],
            check=False,
        )
    session.input("keys", "--hold-ms", 80, ESC)
    time.sleep(0.5)
    # The virtual output is 1920x1080 physical / 1371x771 logical at 140%;
    # Plasma's clock is centred near logical x=1270 in the bottom panel.
    session.input("absolute-click", 1270, 745)
    time.sleep(1)
    session.screenshot("plasma-calendar-140")
    session.input("keys", "--hold-ms", 80, ESC)

    logout = session.launch(
        [
            "/usr/libexec/ksmserver-logout-greeter",
            "--windowed",
            "--lookandfeel",
            THEME_ID,
        ],
        wait_seconds=2,
    )
    session.screenshot("logout-windowed-140")
    session.input("keys", "--hold-ms", 80, TAB)
    session.screenshot("logout-keyboard-focus-140")
    session.stop_process(logout)

    sddm = session.launch(
        [
            "sddm-greeter-qt6",
            "--test-mode",
            "--theme",
            str(
                Path("/usr/share/sddm/themes/NoxForge")
                if session.args.system_package
                else ROOT / "sddm/NoxForge"
            ),
        ],
        wait_seconds=2,
    )
    session.screenshot("sddm-test-mode-140")
    session.input("keys", "--hold-ms", 80, TAB)
    session.screenshot("sddm-keyboard-focus-140")
    session.stop_process(sddm)

    splash = session.launch(
        ["ksplashqml", "--window", "--nofork", THEME_ID],
        wait_seconds=0.6,
        require_running=False,
    )
    if splash.poll() is None:
        session.screenshot("splash-windowed-140")
    session.stop_process(splash)

    for factor, suffix in ((0, "reduced"), (1, "normal"), (4, "slow")):
        run(
            [
                "kwriteconfig6",
                "--file",
                "kdeglobals",
                "--group",
                "KDE",
                "--key",
                "AnimationDurationFactor",
                str(factor),
            ]
        )
        run(["qdbus-qt6", "org.kde.KWin", "/KWin", "reconfigure"])
        process = session.launch(["systemsettings"])
        session.maximize()
        session.restore()
        session.screenshot(f"motion-{suffix}-settled-140")
        session.stop_process(process)

    apps = [
        session.launch(["systemsettings"]),
        session.launch(["dolphin", str(ROOT)]),
        session.launch(["konsole"]),
    ]
    input_process = subprocess.Popen(
        [str(session.args.injector), "keys", "--hold-ms", "2200", str(ALT), str(TAB)],
        cwd=ROOT,
        text=True,
        stdout=session.log_handle,
        stderr=subprocess.STDOUT,
    )
    time.sleep(0.6)
    session.screenshot("tabbox-held-140")
    if input_process.wait(timeout=10) != 0:
        raise RuntimeError("held Alt+Tab input failed")
    for app in apps:
        session.stop_process(app)


def mixed_case(session: LiveSession) -> None:
    left, right = session.args.scales
    label = f"{scale_label(left)}-{scale_label(right)}"
    process = session.launch(["systemsettings"])
    session.maximize()
    session.screenshot(f"mixed-{label}-systemsettings-left")
    session.input("keys", "--hold-ms", 200, META, SHIFT, RIGHT)
    time.sleep(2)
    session.screenshot(f"mixed-{label}-systemsettings-transition")
    session.restore()
    session.maximize()
    session.screenshot(f"mixed-{label}-systemsettings-right")
    session.stop_process(process)

    apps = [
        session.launch(["systemsettings"]),
        session.launch(["dolphin", str(ROOT)]),
        session.launch(["konsole"]),
    ]
    session.screenshot(f"mixed-{label}-applications")
    for app in apps:
        session.stop_process(app)


def inner(args: argparse.Namespace) -> int:
    evidence = Path(args.evidence_dir).resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    session = LiveSession(args, evidence)
    try:
        session.start()
        session.configure_outputs()
        if args.outputs == 1:
            single_case(session)
        else:
            mixed_case(session)
        return 0
    finally:
        session.close()


def session_manifest(
    evidence_root: Path,
    cases: list[dict[str, object]],
    package: dict[str, object] | None,
) -> dict[str, object]:
    files: dict[str, dict[str, object]] = {}
    for path in sorted(evidence_root.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        relative = path.relative_to(evidence_root).as_posix()
        entry: dict[str, object] = {"sha256": sha256(path), "bytes": path.stat().st_size}
        if path.suffix == ".png":
            entry["pixelSize"] = png_size(path)
        files[relative] = entry
    return {
        "schemaVersion": 1,
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "environment": {
            "session": "isolated KWin virtual Wayland",
            "kwin": run(["kwin_wayland", "--version"]).stdout.strip(),
            "qt": run(["qmake6", "-query", "QT_VERSION"]).stdout.strip(),
            "hostSessionMutated": False,
            "input": "KWin EIS RemoteDesktop with libei sender",
            "themeSource": (
                "verified system RPM with byte-identical isolated look-and-feel staging"
                if package
                else "isolated user source install"
            ),
        },
        "package": package,
        "requiredSingleScales": [scale_label(scale) for scale in SINGLE_SCALES],
        "requiredMixedScales": [
            f"{scale_label(left)}+{scale_label(right)}" for left, right in MIXED_SCALES
        ],
        "cases": cases,
        "files": files,
        "limitations": [
            "The KWin virtual backend reports its synthetic pointer as the default cursor; physical NoxForge cursor scaling is not claimed.",
            "Hardware blur, audio output, PAM authentication, and real power actions are not exercised.",
            "The headless system-package run stages the verified RPM defaults before compositor startup because plasma-apply-lookandfeel cannot initialize a pristine headless profile by itself.",
        ],
    }


def outer(args: argparse.Namespace) -> int:
    evidence_root = Path(args.evidence_dir).resolve()
    if evidence_root == ROOT or ROOT not in evidence_root.parents:
        raise RuntimeError("evidence directory must be a dedicated path inside the repository")
    require_tools(args.injector)
    evidence_root.mkdir(parents=True, exist_ok=True)
    package = verify_system_package() if args.system_package else None
    cases: list[dict[str, object]] = []
    scenarios = [(scale,) for scale in SINGLE_SCALES] + list(MIXED_SCALES)
    if args.scenario:
        scenarios = [
            scales
            for scales in scenarios
            if (
                f"single-{scale_label(scales[0])}"
                if len(scales) == 1
                else f"mixed-{scale_label(scales[0])}-{scale_label(scales[1])}"
            )
            == args.scenario
        ]
    with tempfile.TemporaryDirectory(prefix="noxforge-v7-live-") as temporary:
        temporary_root = Path(temporary)
        for index, scales in enumerate(scenarios):
            case_name = (
                f"single-{scale_label(scales[0])}"
                if len(scales) == 1
                else f"mixed-{scale_label(scales[0])}-{scale_label(scales[1])}"
            )
            case_root = temporary_root / case_name
            env = isolated_environment(case_root)
            if not args.system_package:
                install_theme(env)
                defaults = (
                    Path(env["XDG_DATA_HOME"])
                    / "plasma/look-and-feel"
                    / THEME_ID
                    / "contents/defaults"
                )
            else:
                stage_system_lookandfeel(env)
                defaults = Path("/usr/share/plasma/look-and-feel") / THEME_ID / "contents/defaults"
            stage_prestart_defaults(env, defaults)
            case_evidence = evidence_root / case_name
            case_evidence.mkdir(parents=True, exist_ok=True)
            socket = f"noxforge-v7-{index}"
            # D-Bus activated KDE services inherit the bus daemon's original
            # environment, so the private Wayland socket must exist there
            # before dbus-run-session starts.
            env["WAYLAND_DISPLAY"] = socket
            command = [
                "dbus-run-session",
                "--",
                sys.executable,
                str(Path(__file__).resolve()),
                "--inner",
                "--injector",
                str(args.injector),
                "--evidence-dir",
                str(case_evidence),
                "--socket",
                socket,
                "--outputs",
                str(len(scales)),
                "--scales",
                *(str(scale) for scale in scales),
            ]
            if args.system_package:
                command.append("--system-package")
            started = time.monotonic()
            runner_log = case_evidence / "runner.txt"
            with runner_log.open("w", encoding="utf-8") as runner_handle:
                result = subprocess.run(
                    command,
                    cwd=ROOT,
                    env=env,
                    check=False,
                    text=True,
                    stdout=runner_handle,
                    stderr=subprocess.STDOUT,
                    timeout=240,
                )
            status = "passed" if result.returncode == 0 else "failed"
            cases.append(
                {
                    "id": case_name,
                    "status": status,
                    "scales": [scale_label(scale) for scale in scales],
                    "seconds": round(time.monotonic() - started, 3),
                }
            )
            if result.returncode != 0:
                raise RuntimeError(f"{case_name} failed; see {case_evidence / 'runner.txt'}")
            runner_log.unlink(missing_ok=True)
            (case_evidence / "session.log").unlink(missing_ok=True)
    manifest = session_manifest(evidence_root, cases, package)
    (evidence_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"NoxForge v7 isolated live matrix passed: {len(cases)} display scenarios")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inner", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--system-package",
        action="store_true",
        help="qualify the already-installed, rpm-verified system package",
    )
    parser.add_argument("--injector", type=Path, required=True)
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=ROOT / "docs/evidence/v7/live",
    )
    parser.add_argument("--socket", default="noxforge-v7-live", help=argparse.SUPPRESS)
    parser.add_argument(
        "--scenario",
        choices=(
            *(f"single-{scale_label(scale)}" for scale in SINGLE_SCALES),
            *(f"mixed-{scale_label(left)}-{scale_label(right)}" for left, right in MIXED_SCALES),
        ),
        help="run one display scenario (qualification defaults to the complete matrix)",
    )
    parser.add_argument("--outputs", type=int, choices=(1, 2), default=1, help=argparse.SUPPRESS)
    parser.add_argument("--scales", type=float, nargs="+", default=[1.0], help=argparse.SUPPRESS)
    args = parser.parse_args()
    args.injector = args.injector.resolve()
    if len(args.scales) != args.outputs:
        parser.error("--scales must provide one value per output")
    return args


def main() -> int:
    args = parse_args()
    try:
        return inner(args) if args.inner else outer(args)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"NoxForge v7 live matrix failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
