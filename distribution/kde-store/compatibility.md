# Compatibility and dependencies

- Fedora 44 KDE Plasma, Wayland, Plasma/KWin 6.7+, Qt 6.11.
- Arch Linux with Plasma/KWin 6.7+ and Qt 6.11: build/offscreen qualification,
  live login, and pacman lifecycle remain pending for V12.
- GTK 3/4, KSyntaxHighlighting, VS Code/Cursor, Ghostty, Alacritty, Kitty, and
  Foot assets are included in the complete-system and portable bundles.
- Component packages are user-local and may be installed independently.
- The Global Theme depends on the other selected component packages; it does
  not install them implicitly.
- Native Qt styling and SDDM are system-package concerns and are not Store
  dependencies.
