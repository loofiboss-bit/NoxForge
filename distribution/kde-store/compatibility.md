# Compatibility and dependencies

- Fedora 44 and Fedora 45 KDE Plasma, Wayland, Plasma/KWin 6.8+, Qt 6.11.
- Arch Linux with Plasma/KWin 6.8+ and Qt 6.11.
- GTK 3/4 (differentiated Libadwaita), KSyntaxHighlighting, VS Code/Cursor,
  Zed, Neovim, Helix, Yazi, Lazygit, Zellij, Tmux, Ghostty, Alacritty, Kitty,
  Foot, btop, Starship, Obsidian, Rofi, Wofi, Bat, Delta, Fzf, Eza, Fastfetch
  Kinetic Studio v2, Discord/Vesktop/Equibop, and Firefox/Zen/LibreWolf
  ecosystem templates (25 apps) are included in the complete-system and
  portable bundles.
- V21 introduces Duotone Surface Iconography (`16x16`..`64x64` + `scalable`,
  482 scalable + 1052 optical icons), 5-size 4x AA Xcursors + 96 Plasma 6
  scalable Wayland cursor suites, Tactile Forge Audio v2 (32 events), true
  PNG24 wallpapers (`16:10`, `32:9`, `images_dark/`), Aurorae v2 (ambient
  shadows & flush maximized frames), canonical OSD & SystemDialog Look-and-Feel
  QML, 10-module Plasma 6.8 Union CSS, Control Center v6 with 6 WCAG-AA accents
  + Wallpaper Accent Extractor + Named Presets, and Doctor Schema 14.
- Component packages are user-local and may be installed independently.
- The Global Theme depends on the other selected component packages; it does
  not install them implicitly.
- Native Qt styling and SDDM are system-package concerns and are not Store
  dependencies.
