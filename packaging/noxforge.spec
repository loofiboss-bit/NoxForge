%global upstream_version 12.0.1
%global use_source_date_epoch_as_buildtime 1
%global _buildhost fedora
%undefine _unique_build_ids
%global _no_recompute_build_ids 1

Name:           noxforge
Version:        12.0.1
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
%{_mandir}/man1/noxforge-doctor.1*
%{_qt6_plugindir}/styles/libnoxforge6.so
%{_datadir}/noxforge/VERSION
%{_datadir}/noxforge/release-manifest.json
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
%{_datadir}/plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/
%{_datadir}/aurorae/themes/io.github.loofiboss.noxforge.desktop/
%{_datadir}/icons/NoxForge/
%{_datadir}/icons/NoxForge-Cursors/
%{_datadir}/sounds/NoxForge/
%{_datadir}/plasma/look-and-feel/io.github.loofiboss.noxforge.desktop/
%{_datadir}/kwin/tabbox/io.github.loofiboss.noxforge.desktop/
%{_datadir}/wallpapers/NoxForge/
%{_datadir}/wallpapers/NoxForge-Quiet/
%{_datadir}/wallpapers/NoxForge-Ultrawide/
%{_datadir}/sddm/themes/NoxForge/

%changelog
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
