# NoxForge Implementation Plan

This file is the canonical scope and release-gate index.

## Active development scope

The active, phase-gated development authority is
[`NOXFORGE_V4_PLAN.md`](NOXFORGE_V4_PLAN.md). NoxForge v4 delivers design polish,
Qt 6 native control rendering enhancements, Plasma/QML session surface polish,
and diagnostic tool upgrades under the Industrial Precision design system in
[`DESIGN.md`](../DESIGN.md).

Implementation must proceed one phase at a time. A later phase is not
authorized until the current phase gate passes and the user explicitly requests
the next phase.

## Historical release evidence

- [`NOXFORGE_V3_PLAN.md`](NOXFORGE_V3_PLAN.md) records the completed v3.0.0
  reliability, distribution, and live-qualification release.
- [`V2_IMPLEMENTATION_PLAN.md`](V2_IMPLEMENTATION_PLAN.md) records the completed
  v2.0.0 visual rebuild scope and gates.
- [`releases/v3.0.0.md`](releases/v3.0.0.md) records the stable v3.0.0 release outcome.
- [`MANUAL_TESTING.md`](MANUAL_TESTING.md) remains authoritative for live checks;
  unavailable graphical checks stay honestly `blocked` in the structured
  evidence manifest.

Normal installation remains non-applying and reversible. No plan authorizes
automatic theme application, panel changes, SDDM activation, Plasma restarts,
publication, or external-service changes without explicit user approval.
