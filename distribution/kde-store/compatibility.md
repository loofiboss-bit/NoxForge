# Compatibility and dependencies

- Fedora 44 and Fedora 45 KDE Plasma, Wayland, Plasma/KWin 6.8+, Qt 6.11.
- Arch Linux with Plasma/KWin 6.8+ and Qt 6.11.
- GTK 3/4, KSyntaxHighlighting, VS Code/Cursor, Zed, Neovim, Helix, Yazi,
  Lazygit, Zellij, Tmux, Ghostty, Alacritty, Kitty, Foot, btop, Starship,
  Obsidian, Rofi, Discord, and Firefox ecosystem templates are included in the
  complete-system and portable bundles.
- V20 introduces multi-level optical icon ladders (`16x16`/`22x22`/`scalable`),
  16-frame sprite animations, Plasma 6.8 Union Style Engine (`plasma-union`),
  Lock Screen Forge Status Pill, and Control Center v5 Kinetic Icon Studio,
  alongside Graphite & Obsidian Plasma Styles, Global Themes, Aurorae,
  wallpapers, and optional SDDM / Plasma Login Manager assets.
- Component packages are user-local and may be installed independently.
- The Global Theme depends on the other selected component packages; it does
  not install them implicitly.
- Native Qt styling and SDDM are system-package concerns and are not Store
  dependencies.
