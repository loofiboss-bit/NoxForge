# NoxForge 20.0.0 — Kinetic Iconography, Multi-Level Status Engine & Ecosystem v3

This plan records the NoxForge version 20 release scope and implementation
sequence, targeted for publication as `v20.0.0`. It builds upon the `v19.0.0`
baseline and delivers a complete animated, multi-level vector status iconography
and Plasma desktoptheme engine alongside Ecosystem v3 (`yazi`, `lazygit`, `zellij`,
`tmux`), a token-bound Lock Screen status pill, Control Center v5, Tokens Schema
16, and Doctor Schema 13 with `0` `metadata-unknown`.

## Product contract

NoxForge 20 preserves authentic graphite surfaces, true-black Obsidian OLED
variants, electric-lime precision accent, Forge Notch (`4 px`) identity, KDE
Plasma 6.8 Union Style Engine (`union/styles/noxforge*`), Wayland-native KWin
6.8 CSD rules, Fastfetch Kinetic Studio v2, three-edition packaging, and the
non-applying installation boundary.

Version 20 expands the system across six major pillars:

1. **Tokens Schema 16 & Kinetic Iconography Baseline:**
   - Upgrades `design/tokens.json` to Schema 16, adding `kineticIconography`
     (`levels`, `wifiLevels20`, `wifiLevels25`, `overdriveThreshold`, `pulseMs`,
     `sweepMs`, `spriteFrames: 16`, `respectsReducedMotion: true`) and
     `ecosystemV3` (`apps: ["yazi", "lazygit", "zellij", "tmux"]`).
   - Adds `animations` (`16x16/animations`, `22x22/animations`, `scalable/animations`)
     to `icons/NoxForge/index.theme` and `design/artwork-contract.json`.

2. **Full-Suite Animated & Multi-Level Icon Engine (`icons/NoxForge`):**
   - Extends `scripts/generate_visual_assets.py` with dynamic `ColorScheme-Highlight`
     / `.accent` bindings, `.warning` Molten Amber (`#FBBF24`), and embedded
     SMIL + CSS `@keyframes` gated behind `@media (prefers-reduced-motion: no-preference)`.
   - Generates full Freedesktop & Plasma 6.8 level ladders:
     - **Battery:** `battery-000`..`battery-100` in 10% steps + `-charging`
       with animated bolt + `-profile-{powersave,balanced,performance}` +
       peripheral batteries (`input-mouse-battery`, `input-keyboard-battery`,
       `phone-battery`, `input-gaming-battery`, `preferences-system-bluetooth-battery`,
       `battery-ups`, `battery-missing`) + distinct `-symbolic` variants.
     - **Wi-Fi & Network:** 20% and 25% steps (`network-wireless-{0,20,40,60,80,100}`,
       `network-wireless-connected-{00,20,40,60,80,100}`, `network-wireless-signal-{none,weak,ok,good,excellent}`)
       + `-locked` + `-limited` + animated `network-wireless-acquiring` +
       `network-wireless-{off,on,available,hotspot}` + Mobile 5G/LTE (`network-mobile-0..100`)
       + VPN (`network-vpn`, `network-vpn-acquiring`, `network-vpn-disconnected`) +
       Flightmode (`network-flightmode-on/off`).
     - **Audio & Microphone:** `audio-volume-{muted,low,medium,high,high-warning,high-danger}`
       + `microphone-sensitivity-{muted,low,medium,high}` + `-symbolic`.
     - **Brightness, Bluetooth & Spinner:** Dedicated `display-brightness-{off,low,medium,high}`
       and `keyboard-brightness-{off,low,medium,high}` (replacing desktop aliases),
       `network-bluetooth*` / animated `bluetooth-acquiring`, animated media &
       software-update icons, and Freedesktop `animations/process-working.svg`
       with 16-frame vertical sprite sheets (`16x256` and `22x352`).

3. **Plasma Desktop Theme Multi-Element Icon Sheets (`plasma/desktoptheme/*/icons/*.svg`):**
   - Extends `design/plasma-semantic-contract.json` (`iconSheetFamilies`) and
     `scripts/generate_plasma_svgs.py` to generate 8 Plasma Desktop Theme
     multi-element icon sheets (`audio`, `battery`, `kdeconnect`, `media`,
     `network`, `notification`, `osd`, `system`) for both Graphite Standard and
     Obsidian OLED, with strict `id="current-color-scheme"` + `ColorScheme-Highlight`
     bindings and zero runtime SVG `filter=` attributes.

4. **Ecosystem v3, Lock Screen Forge Status Pill & `noxforge-ctl icons`:**
   - Deterministically generates and packages Ecosystem v3 themes for `yazi`
     (`apps/yazi/theme*.toml`), `lazygit` (`apps/lazygit/config*.yml`), `zellij`
     (`terminals/zellij/noxforge*.kdl`), and `tmux` (`terminals/tmux/noxforge*.conf`)
     with `@noxforge-version: 20.0.0` metadata and `noxforge-ctl` sync/restore support.
   - Adds a token-bound, motion-safe Lock Screen **Forge Status Pill** (`forgeStatusPill`)
     to `qml/shared/lockscreen/LockScreen.qml` (propagated to Standard & Obsidian
     via `scripts/generate_design_system.py`) with zero hex literals in QML.
   - Adds `noxforge-ctl icons [--status|--sync-accent|--verify] [--json]` with
     Bash/Zsh/Fish shell completions.

5. **Control Center v5 (`tools/control_center.py`) & Doctor Schema 13 (`tools/noxforge-doctor`):**
   - Upgrades Control Center to v5 with an interactive **"Kinetic Icon & Level Studio"**
     (`0%–120%` slider across Battery, Wi-Fi, Audio, Brightness, and Spinner,
     live `QTimer` animation loop respecting Reduced Motion, dynamic Lime/Cyan/Violet/Amber/Custom
     accent re-tinting, and full accessibility names), Ecosystem v3 toggles, and
     Schema 13 diagnostics readout.
   - Upgrades `tools/noxforge-doctor` to Schema 13 with `iconLevelMatrix` checks
     and zero `metadata-unknown` across all Ecosystem v3 formats.

6. **Packaging Parity & Release Gate Qualification:**
   - Installs and packages `apps/yazi`, `apps/lazygit`, `terminals/zellij`, `terminals/tmux`,
     and `16x16/22x22/scalable/animations` consistently across CMake, Fedora RPM,
     portable installer/uninstaller, and KDE Store component tarballs.
   - Qualifies the release through `scripts/validate.py`, `pytest`, `ctest`,
     `qmllint`, `ruff`, and `scripts/release-check.py`.

## Acceptance criteria

- `design/tokens.json` complies with Schema 16.
- `icons/NoxForge` ships complete 10%/20%/25% icon ladders, dedicated brightness
  icons, `-symbolic` optical parity, 16-frame `process-working.svg` sprite sheets,
  zero unexpected SHA256 duplicates, and exact match to `design/edge-polish-contract.json`.
- All 8 `plasma/desktoptheme/*/icons/*.svg` multi-element icon sheets exist in
  both Standard and Obsidian variants and pass Plasma Style SVG validation.
- Ecosystem v3 themes (`yazi`, `lazygit`, `zellij`, `tmux`) are deterministically
  generated, reversible via `noxforge-ctl ecosystem apply/restore`, and report
  zero `metadata-unknown` in `noxforge-doctor` Schema 13.
- Lock Screen `forgeStatusPill` uses strict `tokens.*` bindings (zero QML hex literals)
  and passes `qmllint` and QML variant drift checks.
- Control Center v5 passes offscreen Qt tests including Kinetic Icon & Level Studio
  and accessibility audit checks.
- All Python (`pytest`, `run_python_tests.py`), CTest, `scripts/validate.py`, and
  `scripts/release-check.py` gates pass cleanly.
