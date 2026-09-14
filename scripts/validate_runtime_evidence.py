#!/usr/bin/env python3
"""Reject stale or incomplete runtime source bindings before release promotion."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

RUNTIME_ROOTS = ('src', 'tools', 'design', 'plasma', 'aurorae', 'kwin', 'sddm',
                 'look-and-feel', 'color-schemes', 'icons', 'cursors', 'sounds', 'wallpapers')


def runtime_paths(root: Path) -> set[str]:
    paths = {'VERSION', 'CMakeLists.txt'}
    for directory in RUNTIME_ROOTS:
        paths.update(path.relative_to(root).as_posix() for path in (root / directory).rglob('*')
                     if path.is_file() and '__pycache__' not in path.parts)
    return paths


def evidence_root(root: Path) -> Path:
    fallback = root / 'docs/evidence/v11'
    manifest_path = root / 'distribution/release-manifest.json'
    if not manifest_path.is_file():
        return fallback
    try:
        manifest = json.loads(manifest_path.read_text())
        configured = manifest.get('evidence', {}).get('activeRoot')
    except (OSError, ValueError, TypeError, AttributeError):
        return fallback
    if not isinstance(configured, str) or not configured:
        return fallback
    candidate = (root / configured).resolve()
    return candidate if candidate.is_relative_to(root.resolve()) else fallback


def validate(root: Path) -> list[str]:
    root = root.resolve()
    evidence = evidence_root(root)
    record = json.loads((evidence / 'qualification.json').read_text())
    hashes_path = (evidence / record['candidate']['runtimeSourceHashes']).resolve()
    if not hashes_path.is_relative_to(evidence):
        return ['Runtime hash manifest escapes evidence directory']
    hashes = json.loads(hashes_path.read_text())
    errors = []
    expected = runtime_paths(root)
    if set(hashes) != expected:
        errors.append('Runtime hash coverage differs: ' + ', '.join(sorted(set(hashes) ^ expected)))
    for name, digest in hashes.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append(f'Missing or escaped runtime source: {name}')
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append(f'Stale runtime evidence: {name}; recapture or requalify before publication')
    return errors


def update(root: Path) -> Path:
    root = root.resolve()
    evidence = evidence_root(root)
    record = json.loads((evidence / 'qualification.json').read_text())
    hashes_path = (evidence / record['candidate']['runtimeSourceHashes']).resolve()
    if not hashes_path.is_relative_to(evidence):
        raise ValueError('Runtime hash manifest escapes evidence directory')
    paths = sorted(runtime_paths(root))
    hashes = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths}
    hashes_path.write_text(json.dumps(hashes, indent=2) + '\n')
    return hashes_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--update', action='store_true', help='Update the runtime evidence hash manifest')
    args = parser.parse_args()
    if args.update:
        manifest = update(args.root)
        print(f'Updated runtime evidence hashes in {manifest}')
        return 0
    try:
        errors = validate(args.root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors = [f'Invalid runtime evidence: {error}']
    if errors:
        print('\n'.join(errors))
        return 1
    print('Runtime evidence hashes and coverage match the release source')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
