# Phase 1 gate — Aurorae maximized fallback

Date: 2026-08-02

## Result

Automated and offscreen gate: **passed**
Live Wayland compositor matrix: **pending**
Release readiness: **not ready**

## Verified

- `scripts/check_v7_aurorae.py --check` passed the active/inactive nine-slice,
  normal-frame fallback, canonical SVGZ, title-edge, source-hash, and 48-case
  static scale/state contract.
- Python discovery passed 111 active tests; nine historical source-bound v6
  modules were skipped explicitly.
- Four ASan/UBSan probes and all 21 CTest cases passed.
- QML lint and deterministic generator checks passed.
- Two independently generated source archives were byte-identical.
- Fedora 44 development SRPM/RPM construction passed; four packages produced
  zero `rpmlint` errors and zero warnings.
- Non-mutating install/uninstall dry-runs and `git diff --check` passed.

## Pending live evidence

The single-output 100%, 125%, 140%, 150%, 175%, and 200% cases, mixed-output
100% + 140% and 100% + 200% cases, output transitions, quick tiling, window
button pointer targets, and composed active/inactive rendering require a real
Wayland/KWin session. They were not claimed from static or offscreen evidence.
