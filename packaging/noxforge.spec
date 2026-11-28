%global upstream_version 21.0.5
%global use_source_date_epoch_as_buildtime 1
%global _buildhost fedora
%undefine _unique_build_ids
%global _no_recompute_build_ids 1
%global debug_package %{nil}

Name:           noxforge
Version:        21.0.5
Release:        1%{?dist}
Summary:        Ecosystem and app parity KDE Plasma components

License:        MIT
URL:            https://github.com/loofiboss-bit/NoxForge
Source0:        %{url}/releases/download/v%{upstream_version}/noxforge-%{upstream_version}-source.tar.xz

BuildRequires:  cmake >= 3.24
BuildRequires:  gcc-c++
BuildRequires:  kf6-kirigami
BuildRequires:  ninja-build
BuildRequires:  qt6-qtbase-devel >= 6.7
BuildRequires:  qt6-qtdeclarative-devel >= 6.7

Requires:       kwin >= 6.8
Requires:       plasma-workspace >= 6.8
Requires:       python3
Requires:       qt6-qtbase-gui >= 6.7
Requires:       breeze-icon-theme
Recommends:     python3-pyside6
Recommends:     plasma-union
%description
NoxForge Ecosystem & App Parity is an MIT-licensed collection of separately
installable KDE Plasma components for Fedora KDE. The package contains a Plasma
Look-and-Feel package, Plasma Style, color scheme, Aurorae decoration, KWin
switcher, icons, cursors, sounds, three wallpaper variants, the native Qt 6
style plugin, and an SDDM compatibility theme. Fedora 44 and 45 Plasma Login
Manager uses its standard wallpaper integration and does not support
third-party greeter QML. Store and portable editions use Breeze app controls;
this system package provides the optional native style integration. Package
installation does not apply a theme, configure a login surface, or switch
display managers.

%prep
%autosetup -n NoxForge-%{upstream_version}

%build
%cmake -GNinja -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%check
%ctest

%files
%license LICENSE LICENSES.md
%doc README.md docs/INSTALL_FEDORA.md docs/TROUBLESHOOTING.md
%{_bindir}/noxforge-doctor
%{_bindir}/noxforge-opacity
%{_bindir}/noxforge-ctl
%{_mandir}/man1/noxforge-doctor.1*
%{_mandir}/man1/noxforge-opacity.1*
%{_mandir}/man1/noxforge-ctl.1*
%{_qt6_plugindir}/styles/libnoxforge6.so
%{_datadir}/applications/io.github.loofiboss.noxforge.opacity.desktop
%{_datadir}/applications/io.github.loofiboss.noxforge.controlcenter.desktop
%{_datadir}/icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.opacity.svg
%{_datadir}/icons/hicolor/scalable/apps/noxforge-opacity.svg
%{_datadir}/icons/hicolor/scalable/apps/io.github.loofiboss.noxforge.controlcenter.svg
%{_datadir}/icons/hicolor/scalable/apps/noxforge-controlcenter.svg
%{_datadir}/noxforge/VERSION
%{_datadir}/noxforge/release-manifest.json
%{_datadir}/noxforge/noxforge_core.py
%{_datadir}/noxforge/opacity_gui.py
%{_datadir}/noxforge/control_center.py
%{_datadir}/color-schemes/NoxForgeDark.colors
%{_datadir}/color-schemes/NoxForgeObsidian.colors
%{_datadir}/konsole/NoxForge.colorscheme
%{_datadir}/konsole/NoxForgeObsidian.colorscheme
%{_datadir}/themes/NoxForge/
%{_datadir}/themes/NoxForgeObsidian/
%{_datadir}/org.kde.syntax-highlighting/themes/NoxForge.theme
%{_datadir}/org.kde.syntax-highlighting/themes/NoxForgeObsidian.theme
%{_datadir}/noxforge/terminals/
%{_datadir}/noxforge/editors/
%{_datadir}/noxforge/browsers/
%{_datadir}/noxforge/apps/
%{_datadir}/noxforge/fastfetch/
%{_datadir}/union/styles/noxforge/
%{_datadir}/union/styles/noxforge-obsidian/
%{_datadir}/plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/
%{_datadir}/plasma/desktoptheme/io.github.loofiboss.noxforge.obsidian.desktop/
%{_datadir}/aurorae/themes/io.github.loofiboss.noxforge.desktop/
%{_datadir}/aurorae/themes/io.github.loofiboss.noxforge.obsidian.desktop/
%{_datadir}/icons/NoxForge/
%{_datadir}/icons/NoxForge-Cursors/
%{_datadir}/sounds/NoxForge/
%{_datadir}/plasma/look-and-feel/io.github.loofiboss.noxforge.desktop/
%{_datadir}/plasma/look-and-feel/io.github.loofiboss.noxforge.obsidian.desktop/
%{_datadir}/kwin/tabbox/io.github.loofiboss.noxforge.desktop/
%{_datadir}/kwin/tabbox/io.github.loofiboss.noxforge.obsidian.desktop/
%{_datadir}/wallpapers/NoxForge/
%{_datadir}/wallpapers/NoxForge-Quiet/
%{_datadir}/wallpapers/NoxForge-Ultrawide/
%{_datadir}/wallpapers/NoxForge-Obsidian/
%{_datadir}/wallpapers/NoxForge-Obsidian-Ultrawide/
%{_datadir}/sddm/themes/NoxForge/
%{_datadir}/sddm/themes/NoxForgeObsidian/

%changelog
* Sat Nov 28 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 21.0.5-1
- Fix unreadable dark-on-dark selected sidebar items in KDE System Settings, Discover, Dolphin, and QQC2/Qt6 apps by adapting PE_PanelItemViewItem and PE_PanelItemViewRow to QPalette::HighlightedText WCAG luminance, adding SE_ItemViewItemText leading inset, fixing QSettings IniFormat QStringList AccentColor parsing, expanding CT_SpinBox/CT_ComboBox width margins (preventing clipped percentage suffixes), adding visible State_On checked toggle button states, and refining disabled indicators and flat buttons in libnoxforge6.so
- Upgrade [Colors:Selection] semantic foreground roles (Negative/Neutral/Visited) to WCAG AAA contrast, align Plasma 6.8 Union CSS selectors with real Union 6.8 elements, fix GTK 3/4 checkbutton/radiobutton container fills and missing GTK 3 widget rules with zero Gtk.CssProvider errors, and polish Plasma SVGs, Aurorae v2 corners/close button, icons, Wayland scalable cursors, shared QML session surfaces (LockScreen revealPassword/CapsLock, OSD overdrive, TabBox layout, Logout/SystemDialog keyboard nav, SDDM guards), and ecosystem themes
- Fix noxforge-ctl (@import ordering before existing GTK CSS rules, live colorscheme applier ordering with -a accent, Union full-mode preservation, Aurorae version refresh and dual-profile accent sync), control_center.py, opacity_gui.py (--gui handling), and noxforge-doctor (detect shadowing user/local libnoxforge6.so copies and .svgz Aurorae customizations); add Requires: python3

* Sat Nov 28 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 21.0.4-1
- Make Fastfetch strictly opt-in in noxforge-ctl so bulk ecosystem apply ("all" / Control Center "Deploy All Detected Themes") never overwrites users' existing ~/.config/fastfetch/config.jsonc or logo.txt
- Fix fastfetch status check to require NoxForge tracking in ecosystem-state.json rather than flagging unrelated user fastfetch configs as synced, and preserve fastfetch state tracking on explicit opt-in so backups restore reliably

* Sat Nov 28 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 21.0.3-1
- Fix near-invisible text selection in Plasma Kickoff, KRunner, and PlasmaComponents3 TextField by updating [Colors:Selection] in NoxForgeDark, NoxForgeObsidian, and Plasma Desktop Theme colors to high-contrast accentPressed (#82D936) with dark ink (#0D1419 / #000000), raising selection-vs-input contrast from 1.35:1 to 10.10:1 with WCAG AAA (10.54:1 / 11.93:1) text readability
- Fix GTK 3 and GTK 4 CSS parsing error ("Invalid name of pseudo-class") by removing unsupported ::selection pseudo-element from generated gtk.css files while preserving valid GTK selection node selectors

* Fri Nov 27 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 21.0.2-1
- Fix floating green dot artifact on Dolphin dock resize handle by replacing inverted-axis dots with a crisp 1px structural divider (PM_DockWidgetSeparatorExtent=1, PM_SplitterWidth=4)
- Fix Aurorae v2 floating window borders: eliminate dashed green top-edge tiling (add hint-stretch-borders, move Forge Notch accent highlight exclusively to fixed decoration-topleft), align all 36 9-patch cell bounds to exact integer pixels, replace stepped shadow blocks with seamless filter-free linear/radial gradient shadows, and refine floating borders to 2px with matching 2px bottom corners
- Fix 0.5px subpixel corner overflow in Plasma Desktop Theme SVG edge highlights (exact 6x6 corners across dialogs, panels, and tooltips)
- Synchronize decoration.svgz alongside decoration.svg in noxforge-ctl accent sync and noxforge-opacity

* Fri Nov 27 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 21.0.1-1
- Preserve upstream icons for third-party and external KDE apps by restricting icons/NoxForge/*/apps/ to NoxForge's own 4 app icons (430 scalable + 896 optical system/places/mimetypes icons)
- Fix maximized Aurorae v2 titlebar transparency and KF6Svg style stripping by moving custom classes out of <style id="current-color-scheme"> across Aurorae and Plasma SVGs and adding decoration-maximized-inactive frames
- Purge ksvg-elements and icon-cache.kcache and broadcast KGlobalSettings IconChanged in noxforge-ctl and noxforge-opacity reloads

* Thu Nov 26 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 21.0.0-1
- Release v21.0.0 Duotone Visual Craft, Aurorae v2, Live Control Core & Ecosystem v4
- Upgrade icons/NoxForge to Duotone Surface craft at 32px/48px/64px + 482 scalable icons (56 apps, 30 mimetypes, 28 places)
- Upgrade cursors to 4x4 AA + contrast halo across [24..64]px + Plasma 6 Wayland cursors_scalable/
- Upgrade wallpapers to true PNG24 (zero PNG8 banding), 16:10 & 32:9 aspect ratios, and KDE Plasma 6 Dynamic Wallpaper (images_dark/)
- Upgrade Tactile Forge Audio v2 (27 distinct DSP sources across 32 events)
- Upgrade Aurorae v2 (Shadow=true, filter-free ambient shadows, flush maximized frames, metadata.json) and add Look-and-Feel OSD & SystemDialog QML
- Expand C++ Qt 6 style (CC_Dial, CC_TitleBar, CC_MdiControls, slider ticks, spinbox states, reactive QFileSystemWatcher cache, 6 accents) + modular Plasma 6.8 Union CSS + deep GTK4/Libadwaita
- Upgrade Control Center v6 (async CommandWorker, NoxForge QStyle dogfooding, 6-accent matrix, wallpaper accent extractor, named presets, live preview, Fastfetch selector) and live hot-reload CLI
- Expand Ecosystem v4 to 25 tools (bat, delta, fzf, eza, wofi, Fastfetch Kinetic Studio v2, deepened Neovim/VS Code/Firefox/Zen/Discord/Starship/Kitty) and Doctor Schema 14

* Sat Nov 14 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 20.0.0-1
- Release v20.0.0 Kinetic Iconography, Multi-Level Status Engine & Ecosystem v3
- Expand icons/NoxForge with continuous 0-100% battery/Wi-Fi/audio/brightness levels and 16-frame loader sprites
- Generate 8 semantic Plasma DesktopTheme icons/*.svg sheets across Graphite and Obsidian variants
- Add Lock Screen Kinetic Status Pill with zero-literal token bindings and Reduced Motion suppression
- Upgrade Ecosystem Engine to v3 (Yazi, Lazygit, Zellij, Tmux), Doctor Schema 13, noxforge-ctl icons, and Control Center v5 Studio

* Sun Nov 01 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 19.0.0-1
- Release v19.0.0 KDE Plasma 6.8 Union Style Engine, Fastfetch Kinetic Studio v2 & Wayland Precision
- Generate native Union CSS/QQuick styles (union/styles/noxforge and union/styles/noxforge-obsidian)
- Add noxforge-ctl union, fastfetch, and kwin-csd subcommands plus System Monitor telemetry preset
- Upgrade Doctor to Schema 12 with Union/Wayland diagnostics and zero metadata-unknown warnings
- Upgrade Control Center to v4 with Plasma 6.8 Union, KWin CSD, and Fastfetch Kinetic Studio controls
- Qualify Fedora 45 and Fedora 44 with KDE Plasma 6.8+ and Qt 6.11+ Wayland baseline

* Sat Oct 24 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 18.0.0-1
- Release v18.0.0 Libadwaita Parity, Reversible Ecosystem Engine v2 & Dynamic Control Core
- Dynamic @accent_color GTK 3/4 CSS and managed @import chaining for Libadwaita parity
- Opt-in Flatpak theme override management in noxforge-ctl and Control Center
- Reversible Ecosystem Engine v2 with .noxforge.bak backups, restore command, and reactive profile/accent sync
- Shared tools/noxforge_core.py library and Control Center v3 real-time self-theming
- Tokens Schema 14 and Doctor Schema 11 diagnostics

* Sun Oct 18 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 17.0.1-1
- Release v17.0.1 Authentic Dolphin Grid & Quick Onboarding
- Genuine KDE Plasma 6 Dolphin icon grid view showcase in store screenshots
- Elevated floating panel mode in desktop layout script
- Automated 1-click noxforge-ctl apply [profile] [--layout] profile onboarding
- Quick Onboarding button in Control Center GUI overview tab

* Fri Oct 16 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 17.0.0-1
- Release v17.0.0 Total Single-Source Authority, Dynamic Accent Ecosystem & Portable Integrity
- Total single-source generation across all 12 QML variant surfaces (QML Schema 2)
- Token Schema 13 with dynamic selection tinting and accent matrix harmonization
- SDDM & Lock Screen security posture (allowEmptyPassword=false, reveal toggle with 5s auto-hide)
- Control Center Tab 5 Ecosystem & Apps and unified devtool integration (Zed, btop, Discord, Firefox, Starship, Fastfetch)
- noxforge-ctl GTK 3/4 accent override syncing and configurable schedule time windows
- Portable bundle parity and Doctor Schema 10 diagnostics

* Sun Oct 11 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 16.0.0-1
- Release v16.0.0 Single-Source Architecture, Kinetic Edge Polish & LoofiFaceID
- Canonical single-source QML architecture and synchronized variant generation
- Kinetic motion accessibility (reduced-motion, edge-flash, WCAG AA custom accent)
- Guarded LoofiFaceID face authentication in SDDM and lockscreen
- Unified Control Center with Accessibility tab, --tab routing, and headless tests
- Doctor Schema 9 comprehensive diagnostics and release qualification

* Tue Oct 06 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 15.0.0-1
- Release v15.0.0 Kinetic Signal & Adaptive Motion Suite
- Multi-tier dynamic Wi-Fi/networking kinetic icons
- Dynamic audio waves and reactive visualizers
- Kinetic battery charging glyphs and pulse cues
- Adaptive spring & easing curves in Plasma style & KWin switcher
- Plasma 6.7 compatibility and complete-system parity

* Fri Oct 02 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 14.0.2-1
- Fix noxforge-opacity hollow user theme directories and prevent System Settings KSvg crash
- Validate metadata integrity before writing user-local customization receipts

* Wed Sep 30 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 14.0.0-1
- Dual-palette parity (Graphite & Obsidian OLED), KWin Alt+Tab parity, Lock Screen,
  Forge Accent Matrix, noxforge-ctl unified orchestration and Control Center GUI

* Thu Sep 24 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 13.0.2-1
- Opacity configurator stabilization, active wallpaper sampling, and doctor coherence

* Thu Sep 24 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 13.0.1-1
- Add noxforge-opacity transparency configurator and Qt 6 GUI

* Wed Sep 23 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 13.0.0-1
- Release True Obsidian OLED Parity & Dual-Stack Architecture

* Mon Sep 14 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 12.0.0-1
- Release Ecosystem and App Parity with GTK 3/4 themes, Kate syntax and terminals

* Mon Sep 14 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 11.0.0-1
- Release Deep Focus native Qt style completeness, terminal themes and Obsidian palette

* Wed Sep 09 2026 NoxForge Contributors <noxforge@users.noreply.github.com> - 10.0.0-1
- Prepare Everyday Precision diagnostics, focus, contrast and removal fixes

* Thu Aug 13 2026 Loofi <noreply@example.invalid> - 9.0.0-1
- Release NoxForge v9 System Coherence with Fedora 44 PLM diagnostics

* Thu Aug 13 2026 Loofi <noreply@example.invalid> - 9.0.0~dev-1
- Start NoxForge v9 System Coherence development

* Sun Aug 09 2026 Loofi <noreply@example.invalid> - 8.0.0-1
- Release NoxForge v8 Forge Identity with manifest-driven Store and portable components

* Sun Aug 02 2026 Loofi <noreply@example.invalid> - 7.0.0-1
- Release NoxForge v7 Operational Precision with composed Wayland qualification

* Sun Aug 02 2026 Loofi <noreply@example.invalid> - 7.0.0~dev-1
- Start the phase-gated NoxForge v7 Operational Precision development cycle

* Thu Jul 30 2026 Loofi <noreply@example.invalid> - 6.0.0-1
- Release the NoxForge v6 Kinetic Precision visual and motion system

* Thu Jul 30 2026 Loofi <noreply@example.invalid> - 6.0.0~dev-1
- Start the phase-gated NoxForge v6 Kinetic Precision development cycle

* Sun Jul 26 2026 Loofi <noreply@example.invalid> - 5.0.0-1
- Release the complete NoxForge v5 visual system and qualification evidence

* Sun Jul 26 2026 Loofi <noreply@example.invalid> - 5.0.0~dev-1
- Start the phase-gated NoxForge v5 development cycle

* Sat Jul 25 2026 Loofi <noreply@example.invalid> - 4.0.0-1
- Refine native Qt controls and expand original icon coverage

* Fri Jul 24 2026 Loofi <noreply@example.invalid> - 3.0.0-1
- Add Fedora packaging, CI, structured qualification, and read-only diagnostics

* Fri Jul 24 2026 Loofi <noreply@example.invalid> - 2.0.0-1
- Add the package-managed Fedora installation contract
