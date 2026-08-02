# NoxForge Implementation Plan

This file is the canonical scope and release-gate index.

## Active release scope

The active, phase-gated release authority is
[`NOXFORGE_V7_PLAN.md`](NOXFORGE_V7_PLAN.md). NoxForge v7 Operational Precision
corrects P0 Aurorae scaling and icon-resolution defects before reconciling
application, shell, session, accessibility, diagnostics, and release evidence.
It preserves the released Kinetic Precision identity and non-destructive
installation policy.

Implementation proceeds one phase at a time. Every phase gate must pass before
its checkpoint. Unavailable graphical checks remain pending or blocked; a
pending P0 live gate prevents a v7 release-ready claim. Local phase completion
does not imply a commit, installation, theme application, publication, or
remote change.

## Historical release evidence

- [`NOXFORGE_V6_PLAN.md`](NOXFORGE_V6_PLAN.md) records the completed v6 scope,
  public release, COPR publication, and bounded live evidence.
- [`NOXFORGE_V5_PLAN.md`](NOXFORGE_V5_PLAN.md) records the completed v5 scope,
  stable release, publication and independent readback.
- [`NOXFORGE_V4_PLAN.md`](NOXFORGE_V4_PLAN.md) records the closed v4 scope and
  its source-tag-only public outcome.
- [`releases/v4.0.0.md`](releases/v4.0.0.md) records that the public v4 release
  has no attached artifacts and makes no COPR or fresh live-qualification claim.
- [`NOXFORGE_V3_PLAN.md`](NOXFORGE_V3_PLAN.md) records the completed v3.0.0
  reliability, distribution, and live-qualification release.
- [`V2_IMPLEMENTATION_PLAN.md`](V2_IMPLEMENTATION_PLAN.md) records the completed
  v2.0.0 visual rebuild scope and gates.
- [`releases/v3.0.0.md`](releases/v3.0.0.md) records the stable v3.0.0 release outcome.
- [`MANUAL_TESTING.md`](MANUAL_TESTING.md) remains authoritative for current
  live checks; unavailable graphical checks stay honestly `blocked` in the
  versioned structured evidence manifest.

Normal installation remains non-applying and reversible. No plan authorizes
automatic theme application, panel changes, SDDM activation, Plasma restarts,
publication, or external-service changes without explicit user approval.
