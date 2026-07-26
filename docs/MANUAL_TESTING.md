# Fedora KDE 44 manual visual gate

Run after RPM installation in a disposable Plasma 6.7+ Wayland session.
Capture evidence before any tag or publication. Results must be `passed`,
`failed`, `blocked`, or `not-applicable` in
`docs/evidence/v5/qualification.json`; automated evidence never substitutes for
a live result.

Current candidate: v5 development worktree on Fedora KDE 44. No v5 live case
has been run yet, so every current case remains honestly `blocked` in the v5
manifest. The table and captures below are the historical v3 baseline only;
they must not be presented as v5 results. The active maintainer desktop is not
changed by automated or offscreen checks.

## Historical v3 structural and live baseline

The evidence committed before the v2 visual rebuild was invalidated. The old
140 percent gallery file duplicated the 100 percent capture. It has now been
replaced by an eight-capture LTR/RTL matrix with distinct pixel dimensions and
image hashes at 100, 125, 140, and 200 percent. Aurorae sprite renders remain
structural evidence and do not prove a composed window decoration.

| Check | 100% | 140% | Notes |
| --- | --- | --- | --- |
| NoxForge appears and applies from Global Theme | Passed | Passed | Isolated live apply; two-output capture recorded |
| Existing panel is preserved without resetLayout | Passed | Passed | Panel hash and count were identical before/after |
| Optional compact panel has no edge seams | Passed | Passed | Bottom, top, left, and right captured |
| Popups and dialogs read correctly with blur on/off | Blocked | Blocked | Solid/translucent assets pass; live KWin blur is unqualified |
| Qt buttons, inputs, menus, tabs and lists show every state | Passed | Passed | Native style composed live at 100/140%; full state matrix also passes offscreen |
| Keyboard focus and keyboard-only navigation remain visible | Blocked | Blocked | Focus ring passes offscreen; interaction requires a disposable session |
| RTL mirrors asymmetric controls and Forge Notch safely | Offscreen | Blocked | Eight-capture matrix passes; live shell mirroring is unqualified |
| Plasma widgets load no visible default-theme fallback | Passed | Passed | Live Plasma shell, horizontal/vertical panels, and two outputs captured |
| Aurorae active/inactive/maximized/button states are intact | Blocked | Blocked | Sprite validation passes; live KWin is unqualified |
| Alt+Tab switcher handles icons, long titles and no windows | Blocked | Blocked | Requires live KWin |
| Icons are clear at 16, 22, 24, 32 and 48 px | Passed | Passed | Live horizontal/vertical panels plus exact-size contact sheet |
| Cursors are clear at 100%, 140% and 200% | Blocked | Blocked | Physical files pass; live compositor scaling is unqualified |
| System sounds are restrained and correctly routed | Passed | Passed | PipeWire route succeeded; volume event true peak was -18.1 dBFS |
| Splash, logout and lock-screen surfaces remain coherent | Passed | Passed | Real testing/windowed processes captured in isolated session |
| SDDM user/session/layout/error/power flows work | Blocked | Blocked | Runtime-mocked preview passes; recoverable live SDDM is unavailable |
| Multi-monitor placement and all panel edges work | Passed | Passed | Two virtual outputs and all four panel edges captured |

## Evidence captured (2026-07-18, local offscreen gate)

- Qt widget gallery: LTR and RTL at 100/125/140/200%, plus the data page; all files have expected dimensions and unique hashes
- SDDM: actual `Main.qml` rendered at 960×540 with mock user/session/keyboard/SDDM objects; no clipping
- Icon render: 165 scalable SVGs, 170 physical optical variants, and a five-size semantic-state contact sheet
- Cursor validation: 96 physical files with distinct canonical zoom, color-picker, cardinal-arrow, and drag sources
- Sound validation: 32 Ogg events, all valid OggS magic
- Wallpaper: deterministic 2560×1440, 3840×2160, and 3440×1440 PNGs plus dimmed SDDM background
- QML: generated tokens and physical N/F mark copies; no raw palette hex values in runtime QML

Current automated results are summarized in
`docs/evidence/v3/automated-gate.md` and validated separately from live cases.
Available live results and limitations are recorded in
`docs/evidence/v3/live-session.md`.

## Current v5 Phase 2 offscreen evidence (2026-07-26)

The native Qt style gate renders the control surface in LTR and RTL at
100/125/140/200 percent, plus separate data, menu, state and stress surfaces at
100 percent. All 12 captures use authentic Qt 6 widgets, have the expected
pixel dimensions and have unique hashes. The matrix covers mirrored
subcontrols, sort and close indicators, tri-state checkboxes, static busy
progress, disabled content, long labels and dense geometry.

These reviewed reference renders are automated structural evidence only. They
do not change the blocked v5 live qualification manifest and do not claim
keyboard interaction, compositor behavior or desktop integration.

## Remaining interactive checks (require live Plasma application)

The following cannot be closed without explicitly applying the Global Theme in
an isolated System Settings session and interacting with that desktop. No live
check above has been marked passed. The test operator must:

1. Open System Settings → Appearance → Global Theme → apply NoxForge
2. Verify panel preserved (or explicitly reset layout and check edge seams)
3. Open applications with blur enabled and disabled (System Settings → Desktop Effects)
4. Navigate with keyboard only through System Settings dialogs
5. Open KWin window and verify Aurorae active/inactive/hover/pressed states
6. Use Alt+Tab with multiple windows, long titles and no windows
7. Move windows to all panel edges and on multi-monitor setups
8. Verify SDDM at login screen after reboot

Automated validation and offscreen rendering are structural evidence only and
do not close these graphical checks.
