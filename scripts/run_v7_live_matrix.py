#!/usr/bin/env python3
"""Run the input-capable v7 matrix in disposable KWin Wayland sessions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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
LIVE_PROBE = Path(shutil.which("noxforge-live-probe") or "noxforge-live-probe")
SINGLE_SCALES = (1.0, 1.25, 1.4, 1.5, 1.75, 2.0)
MIXED_SCALES = ((1.0, 1.4), (1.0, 2.0))
META = 125
SHIFT = 42
ALT = 56
TAB = 15
ENTER = 28
SPACE = 57
UP = 103
DOWN = 108
LEFT = 105
RIGHT = 106
ESC = 1
F = 33
F11 = 87
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
REQUIRED_COMPOSED_CHECKS = (
    "applications-maximize-restore",
    "aurorae-edges-and-states",
    "core-and-session-icons",
    "plasma-shell-surfaces",
    "blur-enabled-disabled",
    "session-surfaces",
    "tabbox-state-matrix",
    "motion-matrix",
    "keyboard-focus-and-activation",
    "translation-expansion",
    "rtl-layout",
    "runtime-readback",
)


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


def normalized_text_evidence(text: str, *, quote: bool = False) -> str:
    """Keep command evidence readable and safe for deterministic Git diffs."""
    lines = [ANSI_ESCAPE.sub("", line).rstrip() for line in text.splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    if quote:
        lines = [f"| {line}" if line else "|" for line in lines]
    return "\n".join(lines) + "\n"


def verify_maximized_capture(path: Path, desktop: Path, output_count: int = 1) -> None:
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
    minimum_width = width - 16 if output_count == 1 else width // output_count - 16
    if (
        bounds is None
        or bounds[0] > 8
        or bounds[1] > 8
        or bounds[2] - bounds[0] < minimum_width
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


def require_tools(injector: Path, probe: Path) -> None:
    required = (
        "dbus-run-session",
        "dolphin",
        "firefox",
        "kdialog",
        "konsole",
        "kscreen-doctor",
        "kwin_wayland",
        "plasma-apply-lookandfeel",
        "plasma-apply-wallpaperimage",
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
    if not probe.is_file() or not os.access(probe, os.X_OK):
        raise RuntimeError(f"live style probe is not executable: {probe}")


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


def verify_system_package(candidate_rpm: Path) -> dict[str, object]:
    if not candidate_rpm.is_file():
        raise RuntimeError("--candidate-rpm must identify the installed qualification RPM")
    nevra = run(["rpm", "-q", "noxforge"]).stdout.strip()
    candidate_nevra = run(
        ["rpm", "-qp", "--qf", "%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}", str(candidate_rpm)]
    ).stdout.strip()
    if candidate_nevra != nevra:
        raise RuntimeError("installed NoxForge package does not match --candidate-rpm")
    verification = run(["rpm", "-V", "noxforge"], check=False)
    if verification.returncode != 0 or verification.stdout.strip():
        raise RuntimeError("installed NoxForge RPM failed verification: " + verification.stdout)
    doctor = json.loads(run([str(ROOT / "tools/noxforge-doctor"), "--json"]).stdout)
    if doctor.get("status") != "ok" or doctor.get("missing"):
        raise RuntimeError("installed NoxForge package failed doctor readback")
    return {
        "nevra": nevra,
        "sha256": sha256(candidate_rpm),
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
            normalized_text_evidence(result.stdout), encoding="utf-8", newline="\n"
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
        wallpaper = (
            Path("/usr/share")
            if self.args.system_package
            else Path(os.environ["XDG_DATA_HOME"])
        ) / "wallpapers/NoxForge/contents/images/1920x1080.png"
        if not wallpaper.is_file():
            raise RuntimeError(f"verified NoxForge wallpaper is missing: {wallpaper}")
        run(["plasma-apply-wallpaperimage", str(wallpaper)], timeout=30)
        activation_method += " plus verified wallpaper default"
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
        (self.evidence / "output-change.txt").write_text(
            normalized_text_evidence(result.stdout), encoding="utf-8", newline="\n"
        )
        time.sleep(2)
        self.record_runtime()
        self.qualify_runtime_readback()
        self.desktop_capture = self.screenshot("desktop-baseline")

    def qualify_runtime_readback(self) -> None:
        containment_config = (
            Path(os.environ["XDG_CONFIG_HOME"])
            / "plasma-org.kde.plasma.desktop-appletsrc"
        )
        if not containment_config.is_file():
            raise RuntimeError("composed-session Plasma containment config is missing")
        shutil.copyfile(containment_config, self.evidence / "plasma-containments.ini")
        report = json.loads(run([str(ROOT / "tools/noxforge-doctor"), "--json"]).stdout)
        (self.evidence / "doctor-runtime.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        expected_active = {
            "qtStyle": "NoxForge",
            "colorScheme": "NoxForgeDark",
            "icons": "NoxForge",
            "soundTheme": "NoxForge",
            "plasmaStyle": THEME_ID,
            "cursorTheme": "NoxForge-Cursors",
            "aurorae": f"__aurorae__svg__{THEME_ID}",
            "kwinSwitcher": THEME_ID,
            "splash": THEME_ID,
            "iconInheritance": "breeze-dark,breeze,hicolor",
            "wallpaper": "NoxForge",
        }
        active = report.get("active", {})
        drift = {
            key: {"expected": value, "actual": active.get(key)}
            for key, value in expected_active.items()
            if active.get(key) != value
        }
        icons = report.get("criticalIcons", {})
        display = report.get("session", {}).get("displayScales", {})
        actual_scales = sorted(
            float(output["scale"])
            for output in display.get("outputs", [])
            if output.get("enabled") and output.get("connected")
        )
        expected_scales = sorted(float(scale) for scale in self.args.scales)
        if (
            report.get("status") != "ok"
            or report.get("missing")
            or drift
            or icons.get("status") != "ok"
            or icons.get("unresolved")
            or display.get("status") != "ok"
            or actual_scales != expected_scales
        ):
            raise RuntimeError(
                "composed-session doctor readback failed: "
                + json.dumps(
                    {
                        "status": report.get("status"),
                        "missing": report.get("missing"),
                        "activeDrift": drift,
                        "criticalIcons": icons,
                        "expectedScales": expected_scales,
                        "actualScales": actual_scales,
                    },
                    sort_keys=True,
                )
            )

    def record_runtime(self) -> None:
        outputs = run(["kscreen-doctor", "-o"], timeout=30).stdout
        support = run(["qdbus-qt6", "org.kde.KWin", "/KWin", "supportInformation"]).stdout
        (self.evidence / "outputs.txt").write_text(
            normalized_text_evidence(outputs), encoding="utf-8", newline="\n"
        )
        (self.evidence / "kwin-support.txt").write_text(
            normalized_text_evidence(support, quote=True), encoding="utf-8", newline="\n"
        )
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
    if session.desktop_capture is None:
        raise RuntimeError("desktop baseline was not captured")
    for attempt in range(3):
        session.maximize()
        capture = session.screenshot(label)
        try:
            verify_maximized_capture(capture, session.desktop_capture, session.args.outputs)
            break
        except RuntimeError:
            if attempt == 2:
                raise
            time.sleep(1)
    session.restore()
    session.input("keys", "--hold-ms", 100, TAB)
    session.input("keys", "--hold-ms", 100, TAB)
    session.screenshot(f"{label}-restored-focus")
    session.stop_process(process)


def icon_gallery_capture(session: LiveSession, label: str) -> None:
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
    session.screenshot(f"core-icon-gallery-{label}")
    session.stop_process(process)


def require_visual_change(before: Path, after: Path, subject: str) -> None:
    with Image.open(before) as source:
        first = source.convert("RGB")
    with Image.open(after) as source:
        second = source.convert("RGB")
    if first.size != second.size or ImageChops.difference(first, second).getbbox() is None:
        raise RuntimeError(f"keyboard activation produced no visible state change: {subject}")


def has_visual_change(before: Path, after: Path) -> bool:
    with Image.open(before) as source:
        first = source.convert("RGB")
    with Image.open(after) as source:
        second = source.convert("RGB")
    return first.size != second.size or ImageChops.difference(first, second).getbbox() is not None


def semantic_color_pixels(
    path: Path,
    color: tuple[int, int, int],
    *,
    tolerance: int = 0,
) -> int:
    with Image.open(path) as source:
        rgb = source.convert("RGB")
        colors = rgb.getcolors(maxcolors=rgb.width * rgb.height)
    if colors is None:
        raise RuntimeError(f"could not inspect semantic colors in {path}")
    return sum(
        count
        for count, pixel in colors
        if max(abs(channel - target) for channel, target in zip(pixel, color)) <= tolerance
    )


def require_color_presence(
    path: Path,
    color: tuple[int, int, int],
    subject: str,
    *,
    minimum: int = 16,
    tolerance: int = 0,
) -> None:
    if semantic_color_pixels(path, color, tolerance=tolerance) < minimum:
        raise RuntimeError(f"expected semantic color is absent from {subject}: {path}")


def require_color_row_span(
    path: Path,
    color: tuple[int, int, int],
    subject: str,
    *,
    minimum: int = 400,
) -> None:
    with Image.open(path) as source:
        rgb = source.convert("RGB")
        top = round(rgb.height * 0.45)
        bottom = round(rgb.height * 0.80)
        widest = max(
            dict(
                (pixel, count)
                for count, pixel in (
                    rgb.crop((0, y, rgb.width, y + 1)).getcolors(maxcolors=rgb.width) or []
                )
            ).get(color, 0)
            for y in range(top, bottom)
        )
    if widest < minimum:
        raise RuntimeError(f"expected focused semantic span is absent from {subject}: {path}")


def require_process_exit(process: subprocess.Popen[str], subject: str) -> None:
    try:
        returncode = process.wait(timeout=5)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"keyboard activation did not complete: {subject}") from error
    if returncode != 0:
        raise RuntimeError(f"keyboard activation failed for {subject}: exit {returncode}")


def keyboard_dialog_activation(session: LiveSession, label: str) -> None:
    for key_name, key_code in (("enter", ENTER), ("space", SPACE)):
        dialog = session.launch(
            ["kdialog", "--title", "NoxForge v7", "--msgbox", f"Activate with {key_name}"]
        )
        session.screenshot(f"qt-dialog-{key_name}-before-{label}")
        session.input("keys", "--hold-ms", 80, key_code)
        require_process_exit(dialog, f"Qt dialog {key_name}")
        if dialog in session.processes:
            session.processes.remove(dialog)


def set_blur_state(session: LiveSession, enabled: bool) -> None:
    method = "loadEffect" if enabled else "unloadEffect"
    run(
        [
            "qdbus-qt6",
            "org.kde.KWin",
            "/Effects",
            f"org.kde.kwin.Effects.{method}",
            "blur",
        ]
    )
    time.sleep(0.5)
    state = run(
        [
            "qdbus-qt6",
            "org.kde.KWin",
            "/Effects",
            "org.kde.kwin.Effects.isEffectLoaded",
            "blur",
        ]
    ).stdout.strip().lower()
    if state != str(enabled).lower():
        raise RuntimeError(f"KWin blur effect did not reach requested state: {enabled}")


def blur_state_capture(session: LiveSession, label: str) -> None:
    scale = session.args.scales[0]
    logical_width = round(1920 / scale)
    logical_height = round(1080 / scale)
    for enabled in (True, False):
        state = "enabled" if enabled else "disabled"
        set_blur_state(session, enabled)
        baseline = session.screenshot(f"plasma-shell-baseline-blur-{state}-{label}")

        task = session.launch(["systemsettings"])
        session.kwin_script("workspace.activeWindow.minimized = true;")
        task_capture = session.screenshot(f"plasma-task-manager-blur-{state}-{label}")
        require_visual_change(baseline, task_capture, f"task manager with blur {state}")

        tooltip_source = Path(os.environ["XDG_RUNTIME_DIR"]) / "noxforge-tooltip.qml"
        tooltip_source.write_text(
            "import QtQuick\n"
            "import org.kde.plasma.core as PlasmaCore\n"
            "Item {\n"
            "    id: root\n"
            "    property bool qualifyTooltip: false\n"
            "    Timer {\n"
            "        interval: 2500\n"
            "        running: true\n"
            "        onTriggered: root.qualifyTooltip = true\n"
            "    }\n"
            "    PlasmaCore.Dialog {\n"
            "        visible: root.qualifyTooltip\n"
            "        type: PlasmaCore.Dialog.Tooltip\n"
            "        outputOnly: true\n"
            "        mainItem: Rectangle {\n"
            "            width: 420\n"
            "            height: 112\n"
            "            color: \"#151D23\"\n"
            "            border.color: \"#A3FF47\"\n"
            "            Text {\n"
            "                anchors.centerIn: parent\n"
            "                text: \"NoxForge Plasma tooltip surface\"\n"
            "                color: \"#E8F0F2\"\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n",
            encoding="utf-8",
            newline="\n",
        )
        session.input("absolute", max(1, logical_width - 5), 5)
        tooltip_process = session.launch(
            [QML_LAUNCHER, str(tooltip_source)], wait_seconds=0.3
        )
        tooltip_baseline = session.screenshot(
            f"plasma-tooltip-before-blur-{state}-{label}"
        )
        time.sleep(3)
        tooltip = session.screenshot(f"plasma-tooltip-blur-{state}-{label}")
        require_visual_change(
            tooltip_baseline,
            tooltip,
            f"PlasmaCore tooltip with blur {state}",
        )
        session.stop_process(tooltip_process)

        session.input("keys", "--hold-ms", 100, META)
        time.sleep(1)
        launcher = session.screenshot(f"plasma-launcher-blur-{state}-{label}")
        require_visual_change(task_capture, launcher, f"launcher with blur {state}")
        session.input("keys", "--hold-ms", 80, ESC)

        session.input(
            "absolute-click",
            max(1, logical_width - 140),
            max(1, logical_height - 20),
        )
        time.sleep(1)
        tray = session.screenshot(f"plasma-tray-blur-{state}-{label}")
        if not has_visual_change(task_capture, tray):
            session.input(
                "absolute-click",
                max(1, logical_width - 140),
                max(1, logical_height - 20),
            )
            time.sleep(1)
            tray = session.screenshot(f"plasma-tray-blur-{state}-{label}")
        require_visual_change(task_capture, tray, f"system tray with blur {state}")
        session.input("keys", "--hold-ms", 80, ESC)

        session.input(
            "absolute-click",
            logical_width // 2,
            logical_height // 2,
            273,
        )
        time.sleep(1)
        popup = session.screenshot(f"plasma-popup-blur-{state}-{label}")
        require_visual_change(task_capture, popup, f"desktop popup with blur {state}")
        session.input("keys", "--hold-ms", 80, ESC)

        notification = run(
            [
                "notify-send",
                "--print-id",
                "NoxForge v7",
                f"Operational Precision blur {state}",
            ]
        )
        time.sleep(1)
        notification_capture = session.screenshot(
            f"plasma-notification-blur-{state}-{label}"
        )
        require_visual_change(
            task_capture,
            notification_capture,
            f"notification with blur {state}",
        )
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

        run(
            [
                "qdbus-qt6",
                "org.kde.plasmashell",
                "/org/kde/osdService",
                "org.kde.osdService.showText",
                "preferences-desktop-theme",
                f"NoxForge v7 blur {state}",
            ]
        )
        time.sleep(1)
        osd = session.screenshot(f"plasma-osd-blur-{state}-{label}")
        require_visual_change(task_capture, osd, f"OSD with blur {state}")

        dialog = session.launch(
            [
                "kdialog",
                "--title",
                f"NoxForge blur {state}",
                "--msgbox",
                "Translucent dialog surface",
            ]
        )
        dialog_capture = session.screenshot(f"plasma-dialog-blur-{state}-{label}")
        require_visual_change(task_capture, dialog_capture, f"dialog with blur {state}")
        session.stop_process(dialog)

        session.input(
            "absolute-click",
            max(1, logical_width - 100),
            max(1, logical_height - 20),
        )
        time.sleep(1)
        calendar = session.screenshot(f"plasma-calendar-blur-{state}-{label}")
        require_visual_change(task_capture, calendar, f"calendar with blur {state}")
        session.input("keys", "--hold-ms", 80, ESC)
        session.stop_process(task)


def tabbox_window(session: LiveSession, name: str, title: str) -> subprocess.Popen[str]:
    source = Path(os.environ["XDG_RUNTIME_DIR"]) / f"noxforge-tabbox-{name}.qml"
    source.write_text(
        "import QtQuick\n"
        "Window {\n"
        "    visible: true\n"
        "    width: 720\n"
        "    height: 420\n"
        f"    title: {json.dumps(title)}\n"
        "    color: \"#0E1318\"\n"
        "}\n",
        encoding="utf-8",
        newline="\n",
    )
    return session.launch([QML_LAUNCHER, str(source)])


def iconless_tabbox_window(session: LiveSession, label: str) -> subprocess.Popen[str]:
    report_path = session.evidence / f"tabbox-iconless-client-{label}.json"
    process = session.launch(
        [
            str(session.args.probe),
            "--mode",
            "iconless-window",
            "--report",
            str(report_path),
        ]
    )
    report = wait_for_json_report(report_path, process)
    if (
        report.get("result") != "passed"
        or report.get("title") != "NoxForge genuine iconless client"
        or report.get("applicationIconNull") is not True
        or report.get("windowIconNull") is not True
    ):
        raise RuntimeError("TabBox client did not prove a genuinely null application/window icon")
    return process


def held_tabbox_capture(session: LiveSession, name: str) -> None:
    input_process = subprocess.Popen(
        [str(session.args.injector), "keys", "--hold-ms", "2200", str(ALT), str(TAB)],
        cwd=ROOT,
        text=True,
        stdout=session.log_handle,
        stderr=subprocess.STDOUT,
    )
    time.sleep(0.6)
    session.screenshot(name)
    if input_process.wait(timeout=10) != 0:
        raise RuntimeError(f"held Alt+Tab input failed for {name}")


def tabbox_state_matrix(session: LiveSession, label: str) -> None:
    held_tabbox_capture(session, f"tabbox-empty-{label}")

    single = tabbox_window(session, "single", "NoxForge single-window state")
    held_tabbox_capture(session, f"tabbox-single-{label}")
    session.stop_process(single)

    normal = session.launch(["systemsettings"])
    missing = iconless_tabbox_window(session, label)
    missing_capture = session.evidence / f"tabbox-missing-icon-{label}.png"
    held_tabbox_capture(session, missing_capture.stem)
    require_color_presence(
        missing_capture,
        (163, 255, 71),
        "TabBox application-x-executable fallback glyph",
        tolerance=18,
    )
    session.stop_process(missing)
    session.stop_process(normal)

    normal = session.launch(["systemsettings"])
    long_title = tabbox_window(
        session,
        "long-title",
        "NoxForge extraordinarily long localized window title for live elision qualification",
    )
    held_tabbox_capture(session, f"tabbox-long-title-{label}")
    session.stop_process(long_title)
    session.stop_process(normal)

    normal = session.launch(["systemsettings"])
    error = session.launch(
        ["kdialog", "--title", "NoxForge error state", "--error", "Live error semantics"]
    )
    held_tabbox_capture(session, f"tabbox-error-{label}")
    session.stop_process(error)
    session.stop_process(normal)

    apps = [
        session.launch(["systemsettings"]),
        session.launch(["dolphin", str(ROOT)]),
        session.launch(["konsole"]),
        tabbox_window(session, "many-a", "NoxForge many-window state A"),
        tabbox_window(session, "many-b", "NoxForge many-window state B"),
    ]
    held_tabbox_capture(session, f"tabbox-many-{label}")
    session.kwin_script(
        'const windows = workspace.windowList(); for (const w of windows) '
        'if (w.caption.includes("many-window state A")) w.minimized = true;'
    )
    held_tabbox_capture(session, f"tabbox-minimized-{label}")
    for app in apps:
        session.stop_process(app)


def wait_for_json_report(path: Path, process: subprocess.Popen[str]) -> dict[str, object]:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
        if process.poll() is not None:
            raise RuntimeError(f"live style probe exited before writing {path.name}")
        time.sleep(0.05)
    raise RuntimeError(f"timed out waiting for live style probe report: {path.name}")


def require_distinct_captures(first: Path, second: Path, subject: str) -> None:
    with Image.open(first) as source:
        first_image = source.convert("RGB")
    with Image.open(second) as source:
        second_image = source.convert("RGB")
    if (
        first_image.size != second_image.size
        or ImageChops.difference(first_image, second_image).getbbox() is None
    ):
        raise RuntimeError(f"{subject} captures do not show an observable layout change")


def layout_qualification(session: LiveSession, label: str) -> None:
    reports: dict[str, dict[str, object]] = {}
    captures: dict[str, Path] = {}
    for mode, options in (
        ("ltr", []),
        ("rtl", ["--rtl"]),
        ("pseudo", ["--pseudo"]),
    ):
        report_path = session.evidence / f"layout-{mode}-{label}.json"
        process = session.launch(
            [
                str(session.args.probe),
                "--mode",
                "layout",
                "--report",
                str(report_path),
                *options,
            ],
            wait_seconds=0.2,
        )
        reports[mode] = wait_for_json_report(report_path, process)
        captures[mode] = session.screenshot(
            f"layout-{'translation-expansion' if mode == 'pseudo' else mode}-{label}"
        )
        session.stop_process(process)

    for mode, report in reports.items():
        if report.get("result") != "passed" or report.get("styleClass") != "NoxForgeStyle":
            raise RuntimeError(f"{mode} live layout probe did not use the installed NoxForge style")
    ltr = reports["ltr"]
    rtl = reports["rtl"]
    pseudo = reports["pseudo"]
    if (
        ltr.get("layoutDirection") != "ltr"
        or rtl.get("layoutDirection") != "rtl"
        or int(ltr["markerX"]) >= int(ltr["windowWidth"]) // 2
        or int(rtl["markerX"]) <= int(rtl["windowWidth"]) // 2
    ):
        raise RuntimeError("live RTL probe did not mirror the semantic leading edge")
    displayed = str(pseudo.get("displayedText", ""))
    if (
        pseudo.get("pseudoLocalized") is not True
        or not displayed.startswith("xx ")
        or not displayed.endswith(" xx")
        or int(pseudo["textWidth"]) <= int(pseudo["normalTextWidth"]) * 2
    ):
        raise RuntimeError(
            "live pseudo-localization probe did not render observable expansion markers"
        )
    require_distinct_captures(captures["ltr"], captures["rtl"], "RTL")
    require_distinct_captures(captures["ltr"], captures["pseudo"], "pseudo-localization")


def motion_qualification(session: LiveSession, label: str) -> None:
    reports: dict[str, dict[str, object]] = {}
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
        report_path = session.evidence / f"motion-{suffix}-{label}.json"
        frames_prefix = session.evidence / f"motion-{suffix}-{label}"
        process = session.launch(
            [
                str(session.args.probe),
                "--mode",
                "motion",
                "--report",
                str(report_path),
                "--frames-prefix",
                str(frames_prefix),
            ],
            wait_seconds=0.2,
        )
        report = wait_for_json_report(report_path, process)
        reports[suffix] = report
        session.screenshot(f"motion-{suffix}-settled-{label}")
        session.stop_process(process)
        if (
            report.get("result") != "passed"
            or report.get("styleClass") != "NoxForgeStyle"
            or float(report.get("configuredFactor", -1)) != factor
            or int(report.get("styleHintDurationMs", -1)) != 120 * factor
            or int(report.get("measuredExpectedDurationMs", -1)) != 90 * factor
            or report.get("initialSha256") == report.get("finalSha256")
        ):
            raise RuntimeError(f"{suffix} live motion probe failed exact-style readback")

    reduced = reports["reduced"]
    normal = reports["normal"]
    slow = reports["slow"]
    if (
        int(reduced["distinctTransitionFrames"]) != 1
        or int(reduced["lastChangeMs"]) != -1
        or not 0 <= int(reduced.get("immediateSettleMs", -1)) <= 40
    ):
        raise RuntimeError("reduced motion was not immediate and static")
    for suffix, report in (("normal", normal), ("slow", slow)):
        if (
            int(report["distinctTransitionFrames"]) < 3
            or report.get("intermediateFrameCaptured") is not True
        ):
            raise RuntimeError(f"{suffix} motion did not produce measured intermediate frames")
    normal_last = int(normal["lastChangeMs"])
    slow_last = int(slow["lastChangeMs"])
    if normal_last < 50 or slow_last < normal_last * 2.5 or slow_last > 550:
        raise RuntimeError("live motion timing did not scale with AnimationDurationFactor")


def single_case(session: LiveSession) -> None:
    scale = session.args.scales[0]
    label = scale_label(scale)
    application_capture(
        session,
        ["systemsettings"],
        f"systemsettings-maximized-{label}",
    )
    application_capture(session, ["dolphin", str(ROOT)], f"dolphin-maximized-{label}")
    application_capture(session, ["konsole"], f"konsole-maximized-{label}")

    process = session.launch(["systemsettings"])
    session.focus_window()
    session.input("keys", "--hold-ms", 120, META, LEFT)
    time.sleep(1)
    session.screenshot(f"systemsettings-quick-tile-left-{label}")
    session.input("keys", "--hold-ms", 120, META, RIGHT)
    session.input("keys", "--hold-ms", 120, META, RIGHT)
    time.sleep(1)
    session.screenshot(f"systemsettings-quick-tile-right-{label}")
    session.kwin_script("workspace.activeWindow.minimized = true;")
    session.screenshot(f"systemsettings-minimized-task-{label}")
    session.kwin_script(
        'const windows = workspace.windowList(); for (const w of windows) '
        'if (w.caption.includes("System Settings")) w.minimized = false;'
    )
    session.stop_process(process)

    process = session.launch(["konsole"])
    session.focus_window()
    session.input("keys", "--hold-ms", 120, F11)
    time.sleep(1)
    session.screenshot(f"konsole-fullscreen-{label}")
    session.input("keys", "--hold-ms", 120, F11)
    session.stop_process(process)

    process = session.launch(["systemsettings"])
    for _ in range(5):
        session.input("keys", "--hold-ms", 80, TAB)
    session.screenshot(f"systemsettings-keyboard-focus-{label}")
    session.stop_process(process)

    process = session.launch(["konsole"])
    session.input("keys", "--hold-ms", 200, ALT, F)
    time.sleep(1)
    session.screenshot(f"konsole-alt-mnemonic-{label}")
    session.input("keys", "--hold-ms", 80, ESC)
    session.stop_process(process)

    layout_qualification(session, label)

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
        f"firefox-maximized-{label}",
    )

    keyboard_dialog_activation(session, label)

    icon_gallery_capture(session, label)

    for edge in ("bottom", "top", "left", "right"):
        session.plasma_script(
            f'const p = panels(); if (p.length !== 1) throw "expected one panel"; '
            f'p[0].location = "{edge}";'
        )
        session.screenshot(f"plasma-panel-{edge}-{label}")
    session.plasma_script('panels()[0].location = "bottom";')

    blur_state_capture(session, label)

    logout = session.launch(
        [
            "/usr/libexec/ksmserver-logout-greeter",
            "--windowed",
            "--lookandfeel",
            THEME_ID,
        ],
        wait_seconds=2,
    )
    session.screenshot(f"logout-windowed-{label}")
    for _ in range(6):
        session.input("keys", "--hold-ms", 80, TAB)
    time.sleep(0.5)
    logout_cancel = session.screenshot(f"logout-cancel-focus-{label}")
    require_color_row_span(
        logout_cancel,
        (163, 255, 71),
        "Logout cancel focus",
    )
    session.input("keys", "--hold-ms", 80, SPACE)
    require_process_exit(logout, "Logout cancel with Space")
    if logout in session.processes:
        session.processes.remove(logout)

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
    # In SDDM test mode the first injected Tab resumes from the final power
    # action even though the inactive greeter still paints username focus.
    # Traverse the explicit cyclic KeyNavigation chain to the primary action.
    for _ in range(4):
        session.input("keys", "--hold-ms", 80, TAB)
    time.sleep(0.5)
    session.input("keys", "--hold-ms", 80, ENTER)
    time.sleep(0.5)
    sddm_validation = session.screenshot(f"sddm-enter-validation-{label}")
    require_color_presence(
        sddm_validation,
        (255, 107, 122),
        "SDDM Enter validation",
        tolerance=32,
    )
    session.stop_process(sddm)

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
    session.screenshot(f"sddm-test-mode-{label}")
    session.screenshot(f"sddm-username-focus-{label}")
    session.stop_process(sddm)

    splash = session.launch(
        ["ksplashqml", "--window", "--nofork", THEME_ID],
        wait_seconds=0.6,
    )
    session.screenshot(f"splash-windowed-{label}")
    session.stop_process(splash)

    motion_qualification(session, label)

    tabbox_state_matrix(session, label)


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
    single_case(session)


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
        "requiredChecksPerCase": list(REQUIRED_COMPOSED_CHECKS),
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
    require_tools(args.injector, args.probe)
    if evidence_root.exists():
        shutil.rmtree(evidence_root)
    evidence_root.mkdir(parents=True, exist_ok=True)
    if args.system_package and args.candidate_rpm is None:
        raise RuntimeError("--candidate-rpm is required with --system-package")
    package = verify_system_package(args.candidate_rpm) if args.system_package else None
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
                "--probe",
                str(args.probe),
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
                    timeout=480,
                )
            status = "passed" if result.returncode == 0 else "failed"
            cases.append(
                {
                    "id": case_name,
                    "status": status,
                    "scales": [scale_label(scale) for scale in scales],
                    "checks": list(REQUIRED_COMPOSED_CHECKS) if status == "passed" else [],
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
    parser.add_argument(
        "--injector",
        type=Path,
        default=Path(shutil.which("noxforge-live-input") or "noxforge-live-input"),
        help="bounded EIS input helper (defaults to the helper built by the qualification image)",
    )
    parser.add_argument(
        "--probe",
        type=Path,
        default=LIVE_PROBE,
        help="installed-style live probe (defaults to the helper built by the qualification image)",
    )
    parser.add_argument(
        "--candidate-rpm",
        type=Path,
        help="exact installed RPM whose digest is bound into the live manifest",
    )
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
    args.probe = args.probe.resolve()
    if args.candidate_rpm is not None:
        args.candidate_rpm = args.candidate_rpm.resolve()
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
