# NoxForge Ecosystem & App Parity

NoxForge 12.0.1 Ecosystem & App Parity is an original MIT-licensed Linux
visual system with graphite surfaces, electric lime and the Forge Notch. It
extends the KDE Plasma system with GTK 3/4 themes, KSyntaxHighlighting themes,
VS Code/Cursor themes, and matching Ghostty, Alacritty, Kitty, and Foot
terminal configurations while preserving the read-only, user-local
installation boundary.

The Global Theme is a coordinator, not a complete one-click installer. Install the matching Plasma Style, colors, Aurorae, icons, cursors, task switcher, sounds and wallpapers from the individual archives in the GitHub release using their matching KDE package managers. Store and portable editions use Breeze application controls. The complete Fedora COPR package additionally supplies the native Qt style.

Installation never applies the theme, changes panels or wallpaper, or switches the display manager. Plasma Login Manager integration remains standard wallpaper integration, with NoxForge Quiet recommended. SDDM is an optional compatibility component of the system edition.

Use the exact `noxforge-12.0.1-*.tar.xz` files and verify them against the
release `SHA256SUMS`: https://github.com/loofiboss-bit/NoxForge/releases/tag/v12.0.1

Fedora 44 passes 72 offscreen tests in the local gate. Arch build/live login,
physical login/PAM, audio, pointer/input, mixed physical displays, the full live
scale/RTL/motion matrix, and Arch pacman lifecycle remain pending. No X11,
Plasma 6.0 or other distribution support is claimed.
