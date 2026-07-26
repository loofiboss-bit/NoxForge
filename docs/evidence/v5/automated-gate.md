# NoxForge v5 Phase 6 automated gate

The Phase 6 gate runs the complete release check, deterministic accessibility
review, eleven-sample performance medians, focused Phase 6 tests and a separate
AddressSanitizer/UndefinedBehaviorSanitizer CMake/CTest build.

The accessibility review covers every documented contrast pair, the KDE
system-font contract, keyboard and RTL structure, all committed scale
compositions, reduced motion and non-color state indicators. Its source-bound
result is recorded in `accessibility-review.json`.

The performance review compares the current candidate with Phase 0 commit
`e3faefd481026cffafb9b48e11aa79987781fa78` on the same host. Gallery startup,
control rendering and QML first-frame medians must each remain at or below
1.10 times the baseline. Raw samples and medians are recorded in
`performance.json`.

This report is automated and offscreen evidence. It never substitutes for a
live Plasma, KWin, cursor, audio or SDDM result.

Version: 5.0.0
Qualified baseline commit: 98da2ffcf3129974d9cc2489cf56b59c5ef9a857

## Public delivery readback

- Annotated tag `v5.0.0` resolves to
  `c979515e6bb99f0201e630be269bb7ecc097c35c`.
- Required-check CI run `30193489199`: passed all three checks.
- Exact-tag release workflow run `30193932579`: passed.
- GitHub release `v5.0.0`: six public assets downloaded independently and
  verified against `SHA256SUMS`; the manifest and report bind the tag to the
  exact release commit.
- COPR build `10774386`: terminal `succeeded` for Fedora 44 x86_64 from the
  public release SRPM.
- Disposable Fedora 44 public-COPR install: package availability, `rpm -V`,
  `noxforge-doctor`, KDE/SDDM configuration snapshots and
  `dnf remove --no-autoremove` passed.

The explicitly blocked Phase 6 hardware, input, audio, splash and real SDDM
cases remain release limitations.
