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
