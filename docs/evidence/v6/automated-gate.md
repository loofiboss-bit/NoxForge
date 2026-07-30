# NoxForge v6 Phase 7 automated qualification

The Phase 7 local gate ran against the `6.0.0-dev` source tree on 2026-07-30
without installing or applying NoxForge. It covers the complete release check,
ASan/UBSan, deterministic evidence, accessibility, scale and direction
matrices, and performance against the immutable reviewed v5 baseline.

`accessibility-review.json` records all 15 contrast pairs, non-color semantic
indicators, KDE system-font behavior, keyboard traversal, RTL, reduced motion,
and 100/125/140/200 percent coverage. The Qt 6.11 offscreen platform reported
`NoPreference` through its accessibility hints API, so live high-contrast mode
is not claimed.

`performance.json` records eleven warmed, interleaved medians for gallery
startup, control rendering, and SDDM first frame. All remain within ten percent
of the v5 baseline. Its native stress probe completed 500 input and animation
cycles with no failed case, no active idle timer, no retained widget state, and
heap growth within the fixed 256 KiB ceiling.

The complete local gate passed with 135 Python tests, 21 CTest cases,
ASan/UBSan, QML lint, generator and evidence drift checks, non-mutating install
and uninstall dry-runs, byte-identical source archives, and clean Fedora
SRPM/RPM `rpmlint`.

This is automated and offscreen evidence. It is not a disposable Wayland
session, composed KWin/Plasma interaction, real SDDM authentication, injected
keyboard/pointer input, multi-output placement, or live high-contrast proof.
Every such case remains blocked in `qualification.json`.
