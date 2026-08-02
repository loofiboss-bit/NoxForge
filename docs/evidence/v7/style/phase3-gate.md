# Phase 3 gate — native application interaction

Date: 2026-08-02

## Result

Automated and offscreen gate: **passed**
Live application and input matrix: **pending**
Release readiness: **not ready**

## Verified

- KDE `[KDE] SingleClick=true` and `false` are honored, while an absent key
  falls back to QCommonStyle behavior.
- Shortcut underlines and menu-bar Alt navigation delegate to QCommonStyle.
- The scrollbar has a 16 logical pixel functional extent and a centered visual
  track no wider than 6 pixels; thumb and page hit testing pass.
- Existing focus, selected-row marker, disabled, RTL, unsupported-control,
  motion, and high-DPI probes remain green.
- Python discovery passed 120 active tests; nine historical source-bound v6
  modules were skipped explicitly.
- Four ASan/UBSan probes and all 22 CTest cases passed.
- QML lint, deterministic generators, source archive reproducibility,
  non-mutating install/uninstall dry-runs, and `git diff --check` passed.
- Fedora 44 development SRPM/RPM construction passed; four packages produced
  zero `rpmlint` errors and zero warnings.

## Pending live evidence

System Settings, Dolphin, Konsole, standard Qt menus/dialogs, keyboard-only Alt
mnemonics, and pointer interaction require complete Global Theme activation in
an input-capable disposable or real Plasma session. No host setting changed.
