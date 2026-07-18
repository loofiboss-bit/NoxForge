# Fedora KDE 44 manual visual gate

Run after both installation stages in a Plasma 6.7+ Wayland session. Capture
evidence before any tag or publication. Unavailable checks remain **Pending**.

Session: Plasma 6.7.3 / Wayland (wayland-0) / Fedora KDE 44, 2026-07-18

## Structural and offscreen checks (not full interactive gate)

| Check | 100% | 140% | Notes |
| --- | --- | --- | --- |
| NoxForge appears and applies from Global Theme | Pending | Pending | kpackagetool6 lists id; live apply requires manual System Settings |
| Existing panel is preserved without resetLayout | Pending | Pending | Live Plasma required |
| Optional compact panel has no edge seams | Pending | Pending | Explicit reset only |
| Popups and dialogs read correctly with blur on/off | Pending | Pending | Solid/translucent SVG variants confirmed present; live KWin blur required |
| Qt buttons, inputs, menus, tabs and lists show every state | Offscreen | Offscreen | widget_gallery.cpp offscreen render passed at 100% and 140%; all controls visible |
| Keyboard focus and keyboard-only navigation remain visible | Pending | Pending | Focus ring visible in offscreen gallery; interactive navigation requires live session |
| RTL mirrors asymmetric controls and Forge Notch safely | Offscreen | Offscreen | noxforge_widget_gallery --rtl offscreen render passed; full mirror confirmed |
| Plasma widgets load no visible default-theme fallback | Pending | Pending | No FallbackTheme in plasmarc; no Breeze reference in SVGs; live runtime log required |
| Aurorae active/inactive/maximized/button states are intact | Pending | Pending | All 8 button states + 9 decoration positions confirmed by validate.py; live KWin required |
| Alt+Tab switcher handles icons, long titles and no windows | Pending | Pending | Live KWin required |
| Icons are clear at 16, 22, 24, 32 and 48 px | Offscreen | Offscreen | ImageMagick render: 16 icons × 4 sizes all passed correct dimensions |
| Cursors are clear at 100%, 140% and 200% | Pending | Pending | 96 Xcursor files validated (24/32/48px); live cursor display requires session |
| System sounds are restrained and correctly routed | Pending | Pending | 32 Ogg events validated as valid audio; live routing requires headphones/speakers |
| Splash, logout and lock-screen surfaces remain coherent | Pending | Pending | QML files validated structurally; live Plasma required |
| SDDM user/session/layout/error/power flows work | Pending | Pending | QML flows validated; CTest offscreen startup passed; interactive SDDM requires reboot |
| Multi-monitor placement and all panel edges work | Pending | Pending | Live multi-monitor required |

## Evidence captured (2026-07-18, Plasma 6.7.3 Wayland)

- `kpackagetool6 --list --type Plasma/LookAndFeel` → `io.github.loofiboss.noxforge.desktop` listed
- `./scripts/install.sh --user` → "Installed NoxForge for the current user. No KDE settings were changed."
- Qt widget gallery offscreen (LTR, RTL, 140% DPI) → all pass, all controls correctly styled
- Icon render: 165 SVGs across 9 categories, 16 checks × 4 sizes = 16/16 pass
- Cursor validation: 96 files, all correct Xcursor magic + 24/32/48px chunks
- Sound validation: 32 Ogg events, all valid OggS magic
- Wallpaper: 2560×1440 PNG, MIT license, NoxForge Industrial Precision design confirmed
- SDDM: Qt 6, all 6 required QML flows, no Breeze imports, preview.png 960×540
- All 34 Python automated tests pass; all 4 CMake/CTest tests pass

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
