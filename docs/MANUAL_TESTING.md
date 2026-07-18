# Fedora KDE 44 manual visual gate

Run after both installation stages in a Plasma 6.7+ Wayland session. Capture
evidence before any tag or publication. Unavailable checks remain **Pending**.

Session: Plasma 6.7.3 / Wayland (wayland-0) / Fedora KDE 44, 2026-07-18

## Structural and offscreen checks (not full interactive gate)

The evidence committed before the v2 visual rebuild was invalidated. The old
140 percent gallery file duplicated the 100 percent capture. It has now been
replaced by an eight-capture LTR/RTL matrix with distinct pixel dimensions and
image hashes at 100, 125, 140, and 200 percent. Aurorae sprite renders remain
structural evidence and do not prove a composed window decoration.

| Check | 100% | 140% | Notes |
| --- | --- | --- | --- |
| NoxForge appears and applies from Global Theme | Pending | Pending | kpackagetool6 lists id; live apply requires manual System Settings |
| Existing panel is preserved without resetLayout | Pending | Pending | Live Plasma required |
| Optional compact panel has no edge seams | Pending | Pending | Explicit reset only |
| Popups and dialogs read correctly with blur on/off | Pending | Pending | Solid/translucent SVG variants confirmed present; live KWin blur required |
| Qt buttons, inputs, menus, tabs and lists show every state | Offscreen | Offscreen | Real widget gallery rendered at 100/125/140/200%; controls and data page are non-empty and unclipped |
| Keyboard focus and keyboard-only navigation remain visible | Pending | Pending | Focus ring visible in offscreen gallery; interactive navigation requires live session |
| RTL mirrors asymmetric controls and Forge Notch safely | Offscreen | Offscreen | Eight-capture LTR/RTL matrix passed with distinct data; live shell mirroring remains Pending |
| Plasma widgets load no visible default-theme fallback | Pending | Pending | No FallbackTheme in plasmarc; no Breeze reference in SVGs; live runtime log required |
| Aurorae active/inactive/maximized/button states are intact | Pending | Pending | All 8 button states + 9 decoration positions confirmed by validate.py; live KWin required |
| Alt+Tab switcher handles icons, long titles and no windows | Pending | Pending | Live KWin required |
| Icons are clear at 16, 22, 24, 32 and 48 px | Offscreen | Offscreen | Contact sheet uses physical 16/22px assets and scalable 24/32/48px renders |
| Cursors are clear at 100%, 140% and 200% | Pending | Pending | 96 physical Xcursor files validated; wait/progress have 12 × 80ms frames at 24/32/48px; live display requires session |
| System sounds are restrained and correctly routed | Pending | Pending | 32 Ogg events validated as valid audio; live routing requires headphones/speakers |
| Splash, logout and lock-screen surfaces remain coherent | Pending | Pending | QML files validated structurally; live Plasma required |
| SDDM user/session/layout/error/power flows work | Pending | Pending | Authentic QML preview rendered with runtime mocks; interactive authentication and power actions require real SDDM |
| Multi-monitor placement and all panel edges work | Pending | Pending | Live multi-monitor required |

## Evidence captured (2026-07-18, local offscreen gate)

- Qt widget gallery: LTR and RTL at 100/125/140/200%, plus the data page; all files have expected dimensions and unique hashes
- SDDM: actual `Main.qml` rendered at 960×540 with mock user/session/keyboard/SDDM objects; no clipping
- Icon render: 165 scalable SVGs, 170 physical optical variants, and a five-size semantic-state contact sheet
- Cursor validation: 96 physical files with distinct canonical zoom, color-picker, cardinal-arrow, and drag sources
- Sound validation: 32 Ogg events, all valid OggS magic
- Wallpaper: deterministic 2560×1440, 3840×2160, and 3440×1440 PNGs plus dimmed SDDM background
- QML: generated tokens and physical N/F mark copies; no raw palette hex values in runtime QML

Current automated test counts and archive checks are recorded by the local gate
run, rather than frozen into this checklist.

## Remaining interactive checks (require live Plasma application)

The following cannot be closed without explicitly applying the Global Theme in
System Settings and interacting with the running desktop. No graphical checks
above have been falsely marked as passed. These require the user to:

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
