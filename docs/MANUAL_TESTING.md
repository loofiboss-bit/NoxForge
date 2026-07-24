# Fedora KDE 44 manual visual gate

Run after RPM installation in a disposable Plasma 6.7+ Wayland session.
Capture evidence before any tag or publication. Results must be `passed`,
`failed`, `blocked`, or `not-applicable` in
`docs/evidence/v3/qualification.json`; automated evidence never substitutes for
a live result.

Current candidate: v3 implementation worktree on Fedora KDE 44, 2026-07-24.
Live qualification is **Blocked** because no disposable graphical user or VM is
available. The active maintainer desktop has not been changed.

## Structural and offscreen checks (not full interactive gate)

The evidence committed before the v2 visual rebuild was invalidated. The old
140 percent gallery file duplicated the 100 percent capture. It has now been
replaced by an eight-capture LTR/RTL matrix with distinct pixel dimensions and
image hashes at 100, 125, 140, and 200 percent. Aurorae sprite renders remain
structural evidence and do not prove a composed window decoration.

| Check | 100% | 140% | Notes |
| --- | --- | --- | --- |
| NoxForge appears and applies from Global Theme | Blocked | Blocked | Requires a disposable session and explicit selection |
| Existing panel is preserved without resetLayout | Blocked | Blocked | Requires before/after state in a disposable session |
| Optional compact panel has no edge seams | Blocked | Blocked | Explicit optional layout in a disposable session only |
| Popups and dialogs read correctly with blur on/off | Blocked | Blocked | Solid/translucent assets pass; live KWin blur is unqualified |
| Qt buttons, inputs, menus, tabs and lists show every state | Offscreen | Offscreen | Real widget gallery rendered at 100/125/140/200%; controls and data page are non-empty and unclipped |
| Keyboard focus and keyboard-only navigation remain visible | Blocked | Blocked | Focus ring passes offscreen; interaction requires a disposable session |
| RTL mirrors asymmetric controls and Forge Notch safely | Offscreen | Blocked | Eight-capture matrix passes; live shell mirroring is unqualified |
| Plasma widgets load no visible default-theme fallback | Blocked | Blocked | Structural no-fallback checks pass; runtime observation is required |
| Aurorae active/inactive/maximized/button states are intact | Blocked | Blocked | Sprite validation passes; live KWin is unqualified |
| Alt+Tab switcher handles icons, long titles and no windows | Blocked | Blocked | Requires live KWin |
| Icons are clear at 16, 22, 24, 32 and 48 px | Offscreen | Offscreen | Contact sheet uses physical 16/22px assets and scalable 24/32/48px renders |
| Cursors are clear at 100%, 140% and 200% | Blocked | Blocked | Physical files pass; live compositor scaling is unqualified |
| System sounds are restrained and correctly routed | Blocked | Blocked | 32 Ogg events pass; audible routing is unqualified |
| Splash, logout and lock-screen surfaces remain coherent | Blocked | Blocked | QML passes structurally; live Plasma is unqualified |
| SDDM user/session/layout/error/power flows work | Blocked | Blocked | Runtime-mocked preview passes; recoverable live SDDM is unavailable |
| Multi-monitor placement and all panel edges work | Blocked | Blocked | Requires an isolated multi-output session |

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
