# NoxForge Implementation Plan

This file is the canonical scope and release-gate index.

## Active development scope

The active, phase-gated development authority is
[`NOXFORGE_V3_PLAN.md`](NOXFORGE_V3_PLAN.md). NoxForge v3 is a reliability,
distribution, and live-qualification release. It preserves the Industrial
Precision design in [`DESIGN.md`](../DESIGN.md) and does not authorize a visual
rewrite.

Implementation must proceed one phase at a time. A later phase is not
authorized until the current phase gate passes and the user explicitly requests
the next phase.

## Historical release evidence

- [`V2_IMPLEMENTATION_PLAN.md`](V2_IMPLEMENTATION_PLAN.md) records the completed
  v2.0.0 visual rebuild scope and gates.
- [`releases/v2.0.0.md`](releases/v2.0.0.md) records the stable release outcome.
- [`MANUAL_TESTING.md`](MANUAL_TESTING.md) remains authoritative for live checks;
  unavailable graphical checks stay honestly `blocked` in the structured v3
  evidence manifest.

Normal installation remains non-applying and reversible. No plan authorizes
automatic theme application, panel changes, SDDM activation, Plasma restarts,
publication, or external-service changes without explicit user approval.
