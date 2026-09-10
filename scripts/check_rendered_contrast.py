#!/usr/bin/env python3
"""Check composited state colors, not just isolated palette swatches."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def blend(foreground: str, background: str, opacity: float) -> str:
    return '#' + ''.join(f'{round(int(foreground[i:i+2], 16) * opacity + int(background[i:i+2], 16) * (1-opacity)):02X}' for i in (1, 3, 5))


def contrast(first: str, second: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
        channels = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
        return sum(v * weight for v, weight in zip(channels, (0.2126, 0.7152, 0.0722)))
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def check(tokens: dict) -> dict:
    colors = tokens['colors']
    cases = []
    for name, state in tokens['states']['hierarchy'].items():
        role = tokens['semanticRoles'][state['role']]
        overlay = tokens['overlay'][state['overlay']]
        surface = blend(colors[overlay['color']], colors[role['background']], overlay['opacity'])
        alpha = tokens['opacity'][state['opacity']]
        minimum = {'textDisabled': 3.0, 'textSecondary': 4.5, 'textPrimary': 7.0, 'accentInk': 7.0}.get(role['foreground'], 4.5)
        for parent in ('background', 'surface', 'surfaceRaised', 'surfaceOverlay'):
            background = blend(surface, colors[parent], alpha)
            foreground = blend(colors[role['foreground']], colors[parent], alpha)
            ratio = contrast(foreground, background)
            if ratio < minimum:
                raise ValueError(f'{name} on {parent}: composited contrast {ratio:.2f} < {minimum}')
            cases.append({'state': name, 'parent': parent, 'foreground': foreground, 'background': background, 'ratio': round(ratio, 3), 'minimum': minimum})
    return {'schemaVersion': 1, 'version': tokens['version'], 'provenance': 'computed-compositing', 'cases': cases}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = check(json.loads((ROOT / 'design/tokens.json').read_text()))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(f"Composited contrast passed: {len(report['cases'])} state/parent combinations")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
