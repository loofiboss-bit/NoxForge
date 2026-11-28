# NoxForge — Duotone Visual Craft, Aurorae v2 & Live Control Suite

NoxForge 21.0.3 Duotone Visual Craft, Aurorae v2, Live Control Core & Ecosystem v4 is an original MIT-licensed Linux
visual system with Graphite (`#0D1419`) and True Obsidian OLED (`#000000`) surfaces, 6 WCAG-AA verified accents
(Electric Lime, Forge Cyan, Cyber Violet, Molten Amber, Forge Crimson, Titanium Ice), and the signature Forge Notch. It
extends KDE Plasma 6.8 with Duotone Surface system iconography (430 scalable + 896 optical icons across 16–64px while
preserving authentic upstream icons for third-party and KDE apps), 96 4× AA Xcursors + Plasma 6 scalable Wayland cursors,
Tactile Forge Audio v2 (32 events), true PNG24 wallpapers (`16:10`, `32:9`, dynamic `images_dark/`), pixel-exact Aurorae v2
seamless gradient shadows & slim 2px floating / solid flush maximized frames, canonical OSD & SystemDialog QML, 10-module
Plasma 6.8 Union CSS, differentiated GTK 3/4 Libadwaita themes, and Ecosystem v4 (25 apps including Bat, Delta, Fzf, Eza,
Wofi, Fastfetch Kinetic Studio v2, Neovim, VS Code, Zed, Yazi, Lazygit, Zellij, Tmux, Firefox, and Discord) while
preserving the read-only, user-local installation boundary.

The Global Theme is a coordinator, not a complete one-click installer. Install the matching Plasma Style, colors, Aurorae, icons, cursors, task switcher, sounds and wallpapers from the individual archives in the GitHub release using their matching KDE package managers. Store and portable editions use Breeze application controls. The complete Fedora COPR package additionally supplies the native Qt style.

Installation never applies the theme, changes panels or wallpaper, or switches the display manager. Plasma Login Manager integration remains standard wallpaper integration, with NoxForge Quiet recommended. SDDM is an optional compatibility component of the system edition.

Use the exact `noxforge-21.0.3-*.tar.xz` files and verify them against the
release `SHA256SUMS`: https://github.com/loofiboss-bit/NoxForge/releases/tag/v21.0.3

Fedora 44 and Fedora 45 pass all offscreen tests in the local gate. Arch build/live login,
physical login/PAM, audio, pointer/input, mixed physical displays, the full live
scale/RTL/motion matrix, and Arch pacman lifecycle remain pending. No X11,
Plasma 6.0 or other distribution support is claimed.
