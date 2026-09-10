#!/usr/bin/env python3
"""Capture a local candidate in a disposable, network-isolated Fedora container.

The caller must install the candidate into the container first. No host session,
user directory, D-Bus socket or display socket may be mounted into it.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import run_v7_live_matrix as live

ROOT = Path(__file__).resolve().parents[1]


def capture(args):
    session = live.LiveSession(args, args.evidence_dir)
    try:
        session.start()
        readback_path = args.evidence_dir / 'active-theme.json'
        readback = json.loads(readback_path.read_text())
        readback['activationMethod'] = 'isolated candidate CMake defaults and explicit theme/wallpaper activation'
        readback_path.write_text(json.dumps(readback, indent=2) + '\n')
        session.configure_outputs()
        session.screenshot('desktop')
        live.application_capture(session, ['dolphin', str(Path.home())], 'dolphin')
        live.application_capture(session, ['systemsettings'], 'system-settings')
        session.input('keys', '--hold-ms', 100, live.META)
        time.sleep(1)
        launcher = session.screenshot('launcher')
        live.require_visual_change(args.evidence_dir / 'desktop.png', launcher, 'launcher expansion')
        session.input('keys', '--hold-ms', 80, live.ESC)
        dolphin = session.launch(['dolphin', str(Path.home())])
        settings = session.launch(['systemsettings'])
        session.restore()
        keys = subprocess.Popen([str(args.injector), 'keys', '--hold-ms', '3500', str(live.ALT), str(live.TAB)])
        try:
            time.sleep(1)
            session.screenshot('aurorae-tabbox')
        finally:
            keys.wait(timeout=10)
        session.stop_process(settings)
        session.stop_process(dolphin)
        # Request blur-off; retain pending status until compositor state is verified.
        live.run(['kwriteconfig6', '--file', 'kwinrc', '--group', 'Plugins', '--key', 'blurEnabled', 'false'])
        live.run(['qdbus-qt6', 'org.kde.KWin', '/KWin', 'reconfigure'])
        session.input('keys', '--hold-ms', 100, live.META)
        time.sleep(1)
        launcher = session.screenshot('launcher-no-blur')
        live.require_visual_change(args.evidence_dir / 'desktop.png', launcher, 'no-blur launcher expansion')
        runtime = live.run(['rpm', '-q', 'qt6-qtbase', 'plasma-workspace', 'kwin']).stdout.splitlines()
        report = {'version': (ROOT/'VERSION').read_text().strip(), 'provenance': 'live-isolated-container', 'runtime': runtime,
                  'viewport': [args.width, args.height], 'scale': 1.0, 'physicalQualification': False, 'blurDisabledQualification': 'pending: compositor state not verified',
                  'captures': {p.name: live.sha256(p) for p in args.evidence_dir.glob('*.png')}}
        (args.evidence_dir/'capture.json').write_text(json.dumps(report, indent=2)+'\n')
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inner', action='store_true')
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--injector', type=Path, required=True)
    parser.add_argument('--probe', type=Path, required=True)
    args = parser.parse_args()
    if not Path('/run/.containerenv').is_file():
        parser.error('requires a disposable Podman container; refusing a host session')
    args.evidence_dir = args.evidence_dir.resolve()
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    args.system_package = True
    args.outputs = 1
    args.scales = [1.0]
    args.socket = 'noxforge-v10-capture'
    args.width, args.height = 2560, 1440
    if args.inner:
        if os.environ.get('WAYLAND_DISPLAY') != args.socket:
            parser.error('missing private capture socket configuration')
        capture(args)
        return 0
    live.require_tools(args.injector, args.probe)
    with tempfile.TemporaryDirectory(prefix='noxforge-demo-') as name:
        env = live.isolated_environment(Path(name))
        for folder in ('Documents', 'Pictures', 'Projects'):
            (Path(env['HOME']) / folder).mkdir()
        (Path(env['HOME']) / 'Documents/Welcome.txt').write_text('NoxForge Everyday Precision demo workspace.\n')
        for key in ('DISPLAY', 'DBUS_SESSION_BUS_ADDRESS', 'SESSION_MANAGER', 'XAUTHORITY'):
            env.pop(key, None)
        env['WAYLAND_DISPLAY'] = args.socket
        env.update(KWIN_COMPOSE='O2')
        live.stage_prestart_defaults(env, ROOT / 'look-and-feel' / live.THEME_ID / 'contents/defaults')
        live.run(['dbus-run-session', '--', sys.executable, str(Path(__file__).resolve()),
                  '--inner', '--evidence-dir', str(args.evidence_dir), '--injector', str(args.injector), '--probe', str(args.probe)], env=env, capture=False, timeout=240)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
