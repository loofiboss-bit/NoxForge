%global upstream_version 5.0.0

Name:           noxforge
Version:        5.0.0
Release:        1%{?dist}
Summary:        Industrial Precision global theme for KDE Plasma 6

License:        MIT
URL:            https://github.com/loofiboss-bit/NoxForge
Source0:        %{url}/releases/download/v%{upstream_version}/noxforge-%{upstream_version}.tar.xz

BuildRequires:  cmake >= 3.24
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  qt6-qtbase-devel >= 6.7
BuildRequires:  qt6-qtdeclarative-devel >= 6.7

Requires:       kwin >= 6.7
Requires:       plasma-workspace >= 6.7
Requires:       qt6-qtbase-gui >= 6.7
Requires:       sddm

%description
NoxForge is an original complete Global Theme for Fedora KDE. It includes a
Plasma Look-and-Feel package, Plasma Style, color scheme, Aurorae decoration,
KWin switcher, icons, cursors, sounds, wallpaper, a native Qt 6 style plugin,
and an SDDM theme. Package installation does not apply or activate the theme.

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
%{_datadir}/color-schemes/NoxForgeDark.colors
%{_datadir}/plasma/desktoptheme/io.github.loofiboss.noxforge.desktop/
%{_datadir}/aurorae/themes/io.github.loofiboss.noxforge.desktop/
%{_datadir}/icons/NoxForge/
%{_datadir}/icons/NoxForge-Cursors/
%{_datadir}/sounds/NoxForge/
%{_datadir}/plasma/look-and-feel/io.github.loofiboss.noxforge.desktop/
%{_datadir}/kwin/tabbox/io.github.loofiboss.noxforge.desktop/
%{_datadir}/wallpapers/NoxForge/
%{_datadir}/sddm/themes/NoxForge/

%changelog
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
