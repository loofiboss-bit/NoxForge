#!/usr/bin/env python3
"""Verify actual RPM transactions inside a disposable Fedora container."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-rpm', type=Path, required=True)
    parser.add_argument('--candidate-rpm', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'distribution/release-manifest.json').read_text())
    release = manifest['release']
    baseline_version = release['baseline']['version']
    candidate_version = release['stableVersion']
    if not any(Path(marker).is_file() for marker in ('/run/.containerenv', '/.dockerenv')):
        parser.error('requires a disposable container; refusing host installation')
    for package, version in ((args.baseline_rpm, baseline_version), (args.candidate_rpm, candidate_version)):
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
    steps = [(f'{baseline_version}-install', args.baseline_rpm, baseline_version, []),
             (f'{candidate_version}-upgrade', args.candidate_rpm, candidate_version, []),
             (f'{candidate_version}-reinstall', args.candidate_rpm, candidate_version, ['--replacepkgs']),
             (f'{baseline_version}-rollback', args.baseline_rpm, baseline_version, ['--oldpackage'])]
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
    report = {'version': candidate_version, 'baselineVersion': baseline_version, 'status': 'passed', 'scope': 'real RPM transactions in isolated Fedora container',
              'hostMutated': False, 'phases': phases,
              'packageHashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (args.baseline_rpm, args.candidate_rpm)}}
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print('RPM upgrade, reinstall, rollback and removal passed; configuration preserved')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
