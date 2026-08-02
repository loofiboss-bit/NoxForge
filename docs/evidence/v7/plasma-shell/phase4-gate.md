# Phase 4 Gate — Plasma Shell and Panel Polish

Date: 2026-08-02

## Result

`PASSED` for local automated and offscreen qualification.

- 124 active Python tests passed; nine historical v6 modules skipped.
- Four sanitizer probes passed.
- 22 CTest cases passed.
- QML lint passed with the documented standalone KWin import warning.
- All deterministic generators and 56 Plasma SVG assets passed four runs.
- Source archives were byte-identical.
- Fedora development SRPM and all four RPM packages built successfully.
- `rpmlint` reported zero errors and zero warnings.
- Non-mutating install dry-runs and `git diff --check` passed.

## Contract evidence

- Shell grid: 4 logical pixels.
- Panel and toolbar margins: 4 logical pixels.
- Popup, dialog, and tooltip margins: 8 logical pixels.
- Radius roles: 4, 6, and 8 logical pixels.
- All four panel-edge frame elements remain present.
- v6 and v7 raster atlases use identical viewports for comparable evidence.

## Pending live qualification

Activated panel-edge, tray, popup, calendar, notification, dialog, and OSD
inspection is `pending`. Offscreen and raster evidence is not promoted to live
session evidence, and no host theme or layout was activated or changed.
