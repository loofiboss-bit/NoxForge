# NoxForge v2 visual baseline

This baseline records the state found before the in-place v2.0.0 visual rebuild.
It is historical evidence, not a list of current failures.

## Invalidated candidate artifacts

- The previous local v2 archive and checksum predated the visual gate and were
  invalid for release decisions.
- `gallery_ltr_140pct.png` was byte-identical to the 100 percent capture.
- The old global-theme and SDDM previews were illustrative compositions rather
  than captures of rendered product surfaces.
- Aurorae sprite images proved source structure only, not a composed live KWin
  decoration.

## Baseline implementation gaps

- Plasma families `dragger`, `glowbar`, `margins-highlight`, and `monitor` were
  missing, as was weather artwork and complete edge-specific task coverage.
- Volume, battery, connection, direction, media, zoom, and cursor states reused
  semantically incorrect glyphs.
- Selected/focused controls could stack indicators, selected rows used too much
  lime, and scrollbar end areas produced dark blocks.
- Runtime QML repeated raw palette values and SDDM lacked visible field labels,
  stable feedback space, complete keyboard focus, and accessibility names.
- The widget gallery did not cover dense data views, popup actions, vertical
  controls, long text, or the full LTR/RTL scale matrix.

## Current interpretation

Automated checks now cover these regressions, including generated-source drift,
all 43 Plasma 6.7 widget families, semantic duplicate allowlists, cursor
animation frames, QML token parity, raster dimensions, and unique scale data.

`qmllint` is clean for SDDM, Splash, and Logout. Standalone linting of the KWin
TabBox surface reports that `org.kde.kwin` is unavailable in the generic lint
import path; the package can only close that runtime import check inside KWin.
That warning and every live Plasma/KWin/SDDM visual check remain documented as
Pending in `docs/MANUAL_TESTING.md`.
