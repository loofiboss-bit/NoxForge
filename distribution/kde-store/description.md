# NoxForge Forge Identity

NoxForge is an original MIT-licensed Plasma visual system for Fedora 44 and
the verified Arch Plasma/KWin 6.7+ and Qt 6.11 environment. The Global Theme,
Plasma Style, colors, Aurorae, icons, cursors, task switcher, sounds, and
wallpapers are separate packages because KDE installs these package types in
separate resource roots.

The Global Theme package is a coordinator and is **not** a complete one-click
transaction. Install the components you want through the matching KDE package
manager. Store and portable packages use Breeze application controls and never
install a native Qt plugin, SDDM, or root-owned files. A complete system
edition is available separately through Fedora or Arch packaging.

Upload names are the exact `noxforge-8.0.0-*.tar.xz` names from the release
manifest. The companion `SHA256SUMS` file binds each Store upload to its
checksum; do not rename or combine component archives.

Compatibility is intentionally narrow and verified. No X11, Plasma 6.0,
Debian, Ubuntu, openSUSE, Nix, Flatpak, or AppImage claim is made.
