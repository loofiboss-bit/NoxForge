# NoxForge 18.0.0 — Libadwaita Parity, Reversible Ecosystem Engine v2 & Dynamic Control Core

This plan records the NoxForge version 18 release scope and implementation
sequence, targeted for publication as `v18.0.0`. It builds upon the `v17.0.1`
baseline and elevates NoxForge into a reversible, reactive, and architecturally
unified desktop system across KDE Plasma 6.7+, Qt 6.11, GTK 3/4, Libadwaita,
Flatpak, and third-party developer tools.

## Product contract

NoxForge 18 preserves the authentic graphite surfaces, true-black Obsidian OLED
variant, electric-lime precision accent, Forge Notch (4 px) identity, system
typography, KDE package roots, three-edition architecture, and non-applying
installation boundary.

Version 18 expands and hardens the system across five major pillars:

1. **Tokens Schema 14 & Baseline Hygiene (PR #70 & #71):**
   - Upgrades `design/tokens.json` to Schema 14, codifying the `gtk` dynamic
     CSS variable contract (`dynamicCssVariables: true`, `managedUserImport: true`)
     and the `ecosystem` state and backup contract (`syncPolicy: "stateful-reversible"`,
     `backupSuffix: ".noxforge.bak"`, `stateFile: "noxforge/ecosystem-state.json"`).
   - Incorporates baseline quality refinements from PR #70 (flattened event
     dispatch in `tools/noxforge-live-input.cpp`) and PR #71 (explicit
     `AccessibleName` annotations on schedule time inputs in `tools/control_center.py`).
2. **GTK 3/4, Libadwaita & Flatpak Parity:**
   - Upgrades `gtk_theme_css()` in `scripts/generate_design_system.py` so interactive
     and focus selectors (`button:focus`, `button.suggested-action`, `entry:focus`,
     `checkbutton:checked`, `switch:checked`, `progressbar progress`, `scale highlight`,
     and selection states) bind to `@accent_color`, `@accent_bg_color`,
     `@accent_fg_color`, and `@theme_selected_bg_color` instead of static hex literals.
   - Replaces the partial GTK accent snippet in `noxforge-ctl` with a managed
     non-destructive `@import` + `@define-color` pipeline in
     `~/.config/gtk-3.0/gtk.css` and `~/.config/gtk-4.0/gtk.css`, ensuring
     modern GTK 4 / Libadwaita applications adopt both the active NoxForge surface
     (`NoxForge` or `NoxForgeObsidian`) and active accent override in real time.
   - Adds opt-in Flatpak theme override orchestration (`noxforge-ctl flatpak
     --enable|--disable|--status`) covering `xdg-data/themes:ro`,
     `xdg-config/gtk-3.0:ro`, and `xdg-config/gtk-4.0:ro`.
3. **Reversible & Reactive Ecosystem Engine v2:**
   - Adds automatic non-destructive backup creation (`<file>.noxforge.bak`) prior
     to deploying ecosystem configurations (`starship.toml`, `fastfetch/config.jsonc`,
     Firefox `userChrome.css`, etc.) and introduces `noxforge-ctl ecosystem restore [apps...|all]`.
   - Tracks deployed ecosystem targets in `~/.config/noxforge/ecosystem-state.json`.
   - Automatically propagates both profile switches (`graphite` <-> `obsidian`) and
     accent overrides (`lime`, `cyan`, `violet`, `amber`, or custom WCAG AA `#RRGGBB`)
     into all deployed ecosystem applications (Firefox, Starship, Fastfetch, Discord,
     btop, Zed, Ghostty, Kitty, Alacritty, Foot) and active Konsole profiles whenever
     `noxforge-ctl switch`, `apply`, `sync`, or `accent` is executed.
4. **Shared Core Library (`tools/noxforge_core.py`) & Control Center v3:**
   - Extracts `tools/noxforge_core.py` (installed across portable, RPM, and Arch
     packages) to unify version lookup, XDG path resolution, `kreadconfig6`/`kwriteconfig6`
     wrappers, WCAG 2.1 contrast calculation, and dynamic Qt stylesheet generation
     while preserving 100% backwards compatibility for all existing CLI/GUI entrypoints.
   - Upgrades `tools/control_center.py` and `tools/opacity_gui.py` with live
     self-theming (`build_qt_stylesheet(profile, accent_hex)`), dynamically re-skinning
     the GUI canvas between Graphite (`#0D1419`) and Obsidian (`#000000`) and
     reflecting the active accent color in real time.
   - Enhances Control Center Tab 5 (`Ecosystem & Apps`) with per-application
     `Restore Backup` actions, `Restore All Backups`, live profile/accent sync
     badges, and an interactive Flatpak Theme Override card.
   - Adds system-wide Reduced Motion orchestration (`noxforge-ctl motion`),
     5-variant Wallpaper Suite switching (`noxforge-ctl wallpaper`), portable
     JSON preset export/import (`noxforge-ctl export` / `import`), interactive
     `QColorDialog` custom accent picking, Top Status Header Banner, visual
     Doctor health summary badges, and accent-reactive 60fps Opacity preview canvas.
5. **Doctor Schema 11, Packaging Parity & Release Qualification:**
   - Upgrades `tools/noxforge-doctor` to Schema 11, auditing `noxforge_core.py`
     presence, GTK 3/4/Libadwaita `@import` and `@accent_color` chain coherence
     (`gtkChainStatus`), and reversible ecosystem state/backup integrity
     (`ecosystemState`).
   - Updates `CMakeLists.txt`, `packaging/noxforge.spec`, `packaging/arch/PKGBUILD`,
     `scripts/install.sh`, `scripts/uninstall.sh`, `scripts/uninstall-system.sh`,
     and `scripts/build_store_packages.py` to stage and clean `noxforge_core.py`.
   - Adds comprehensive automated verification in `tests/test_v18_contracts.py`.

## Sequential phases

1. **Baseline Hygiene & Tokens Schema 14:** Incorporate PR #70 and PR #71
   improvements, bump `VERSION` to `18.0.0` via `scripts/sync_version.py`,
   upgrade `design/tokens.json` to Schema 14, and update `IMPLEMENTATION_PLAN.md`
   and `distribution/release-manifest.json` (`baseline`: `17.0.1`).
2. **Shared Python Core (`tools/noxforge_core.py`):** Create `tools/noxforge_core.py`
   with shared constants, XDG/KConfig helpers, WCAG contrast math, and dynamic
   Qt stylesheet builder; wire `noxforge-ctl`, `noxforge-doctor`, `noxforge-opacity`,
   `control_center.py`, and `opacity_gui.py` to use it with full fallback safety.
3. **GTK 3/4, Libadwaita & Flatpak Parity:** Update `scripts/generate_design_system.py`
   to emit `@accent_color`-bound GTK 3/4 CSS, regenerate GTK themes, implement
   managed `@import` + accent chaining in `noxforge-ctl`, and add the `flatpak`
   subcommand.
4. **Reversible & Reactive Ecosystem Engine v2:** Implement `.noxforge.bak`
   backup/restore lifecycle, `~/.config/noxforge/ecosystem-state.json` tracking,
   dynamic profile + accent injection across deployed user configs, and Konsole
   colorscheme synchronization.
5. **Control Center v3 Live Self-Theming & Ecosystem UI:** Connect live
   `build_qt_stylesheet()` updates in `control_center.py` and `opacity_gui.py`,
   and upgrade `EcosystemTab` with backup restoration and Flatpak controls.
6. **Doctor Schema 11, Packaging & Release Gate:** Upgrade `tools/noxforge-doctor`
   to Schema 11, update CMake/RPM/Arch/portable install scripts for `noxforge_core.py`,
   initialize `docs/evidence/v18`, author `tests/test_v18_contracts.py`, and pass
   all validation and release gates.

## Acceptance criteria

- `design/tokens.json` complies with Schema 14.
- Generated `themes/NoxForge*/gtk-{3,4}.0/gtk.css` files bind interactive accent
  rules to `@accent_color` / `@accent_bg_color` with zero drift.
- `noxforge-ctl switch` and `noxforge-ctl accent` maintain a valid `@import` +
  `@define-color` chain in `~/.config/gtk-{3,4}.0/gtk.css` for Libadwaita parity.
- `noxforge-ctl ecosystem apply` creates non-destructive `.noxforge.bak` backups,
  records state in `ecosystem-state.json`, injects active profile and accent
  colors into deployed targets, and `noxforge-ctl ecosystem restore` cleanly
  restores originals.
- `tools/control_center.py` dynamically re-skins its own UI when switching between
  Graphite/Obsidian or changing accents, and exposes Ecosystem Restore and
  Flatpak Override controls.
- `noxforge-doctor` Schema 11 audits `noxforge_core.py`, `gtkChainStatus`, and
  `ecosystemState` with 0 regressions.
- All Python (`pytest`, `run_python_tests.py`), CTest, and `scripts/validate.py`
  checks pass cleanly.
