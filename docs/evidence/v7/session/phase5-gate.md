# Phase 5 Gate — SDDM, Logout, and TabBox

Date: 2026-08-02

## Result

`PASSED` for local automated and offscreen qualification.

- 130 active Python tests passed; nine historical v6 modules skipped.
- Four sanitizer probes passed.
- 46 CTest cases passed, including 29 session-surface cases.
- QML lint passed with the documented standalone KWin import warning.
- All deterministic generators and evidence checks passed.
- Source archives were byte-identical.
- Fedora development SRPM and all four RPM packages built successfully.
- `rpmlint` reported zero errors and zero warnings.
- Non-mutating install dry-runs and `git diff --check` passed.

## Contract evidence

- Authentication and power calls remain unchanged.
- Important controls are 40 logical pixels high.
- SDDM uses Qt Quick Controls `BusyIndicator` and reports Caps Lock.
- Logout uses distinct lock, logout, suspend, restart, and shutdown icons.
- TabBox provides a missing-icon fallback and keyboard activation.
- SDDM, Splash, Logout, and TabBox render at 100/125/140/150/200 percent.
- TabBox covers empty, many-window, long RTL, keyboard, missing-icon, and
  minimized cases.

## Pending live qualification

Real SDDM authentication and power actions, held Alt-Tab, keyboard/pointer
traversal, and per-output mixed-DPI migration are `pending`. Offscreen evidence
is not live evidence, and no host theme, SDDM, or session setting was changed.
