#!/usr/bin/env python3
"""Verify actual RPM transactions inside a disposable Fedora container."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-rpm', type=Path, required=True)
    parser.add_argument('--candidate-rpm', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if not Path('/run/.containerenv').is_file():
        parser.error('requires a disposable Podman container; refusing host installation')
    for package, version in ((args.baseline_rpm, '9.0.0'), (args.candidate_rpm, '10.0.0')):
        if run('rpm', '-qp', '--qf', '%{NAME} %{VERSION}', str(package)) != f'noxforge {version}':
            parser.error(f'wrong package: {package}')
    if subprocess.run(['rpm', '-q', 'noxforge'], stdout=subprocess.DEVNULL).returncode == 0:
        parser.error('requires a clean container without an installed NoxForge RPM')
    config = [Path('/home/demo/.config') / name for name in
              ('kdeglobals', 'plasma-org.kde.plasma.desktop-appletsrc', 'plasmawallpaperrc')]
    config += [Path('/etc/plasmalogin.conf'), Path('/etc/sddm.conf.d/noxforge-user.conf')]
    for path in config:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('[UserChoice]\nvalue=preserve-byte-for-byte\n')
    def hashes():
        return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in config}
    before = hashes()
    phases = []
    steps = [('v9-install', args.baseline_rpm, '9.0.0', []),
             ('v10-upgrade', args.candidate_rpm, '10.0.0', []),
             ('v10-reinstall', args.candidate_rpm, '10.0.0', ['--replacepkgs']),
             ('v9-rollback', args.baseline_rpm, '9.0.0', ['--oldpackage'])]
    for label, package, version, flags in steps:
        run('rpm', '-Uvh', *flags, str(package))
        assert run('rpm', '-q', '--qf', '%{VERSION}', 'noxforge') == version
        run('rpm', '-V', 'noxforge')
        assert hashes() == before, f'configuration changed: {label}'
        phases.append({'phase': label, 'status': 'passed', 'configurationHashes': hashes()})
    owned = run('rpm', '-ql', 'noxforge').splitlines()
    run('rpm', '-e', 'noxforge')
    assert subprocess.run(['rpm', '-q', 'noxforge'], stdout=subprocess.DEVNULL).returncode != 0
    assert not any(Path(path).is_file() for path in owned), 'owned file remains after removal'
    assert hashes() == before, 'configuration changed on removal'
    phases.append({'phase': 'uninstall', 'status': 'passed', 'configurationHashes': hashes()})
    report = {'version': '10.0.0', 'status': 'passed', 'scope': 'real RPM transactions in isolated Fedora container',
              'hostMutated': False, 'phases': phases,
              'packageHashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (args.baseline_rpm, args.candidate_rpm)}}
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print('RPM upgrade, reinstall, rollback and removal passed; configuration preserved')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
