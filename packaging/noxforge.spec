%global upstream_version 18.0.0
%global use_source_date_epoch_as_buildtime 1
%global _buildhost fedora
%undefine _unique_build_ids
%global _no_recompute_build_ids 1
%global debug_package %{nil}

Name:           noxforge
Version:        18.0.0
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

Requires:       kwin >= 6.7
Requires:       plasma-workspace >= 6.7
Requires:       qt6-qtbase-gui >= 6.7
Requires:       breeze-icon-theme
Recommends:     python3-pyside6
%description
NoxForge Ecosystem & App Parity is an MIT-licensed collection of separately
installable KDE Plasma components for Fedora KDE. The package contains a Plasma
Look-and-Feel package, Plasma Style, color scheme, Aurorae decoration, KWin
switcher, icons, cursors, sounds, three wallpaper variants, the native Qt 6
style plugin, and an SDDM compatibility theme. Fedora 44 Plasma Login Manager
uses its standard wallpaper integration and does not support third-party greeter
QML. Store and portable editions use Breeze app controls; this system package
provides the optional native style integration. Package installation does not
apply a theme, configure a login surface, or switch display managers.

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
