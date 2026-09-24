# Compatibility and dependencies

- Fedora 44 KDE Plasma, Wayland, Plasma/KWin 6.7+, Qt 6.11.
- Arch Linux with Plasma/KWin 6.7+ and Qt 6.11: V13 build/live login and
  pacman lifecycle qualification remain pending.
- GTK 3/4, KSyntaxHighlighting, VS Code/Cursor, Ghostty, Alacritty, Kitty, and
  Foot assets are included in the complete-system and portable bundles. V13
  also includes Neovim and Helix themes in Graphite and Obsidian variants.
- V13 adds Obsidian Plasma Style, Global Theme, and Aurorae components, plus
  Obsidian wallpaper and SDDM assets. Login-manager assets remain optional and
  are never configured automatically.
- Component packages are user-local and may be installed independently.
- The Global Theme depends on the other selected component packages; it does
  not install them implicitly.
- Native Qt styling and SDDM are system-package concerns and are not Store
  dependencies.
