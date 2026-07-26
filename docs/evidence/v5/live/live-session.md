# NoxForge v5 isolated Wayland qualification

Captured on 2026-07-26 in separate KWin 6.7.3 virtual Wayland sessions on
Fedora KDE 44. The runs used a temporary `HOME`, XDG configuration tree,
runtime directory, D-Bus session and Wayland socket. NoxForge was installed
only into that temporary home. The maintainer desktop, panel, active theme and
SDDM configuration were not read or changed.

## Passed observations

- `plasma-multi-output.png` shows two independent 1280 by 720 outputs with the
  v5 wallpaper, Plasma Style, icons and panel composed by KWin.
- The isolated panel configuration SHA-256 remained
  `8420d394e52b95d24b8e2a05e51d5bbe5f94efbf7f16993e5d4282b3779de4ca`
  before and after `plasma-apply-lookandfeel`; the panel count remained one.
- `panel-edges.png` contains live bottom, top, left and right panel placements
  from Plasma's scripting API. All four placements are seam-free.
- `qt-controls-100.png` and `qt-controls-140.png` show real System Settings
  processes under KWin at scale 1.0 and 1.4.
- Required shell icons are distinct on horizontal and vertical panels.

## Available processes with limited claims

- `logout-test.png` is the real windowed Plasma logout greeter and
  `sddm-test-mode.png` is the real SDDM greeter in test mode.
- `lock-test.png` confirms that the intentionally inherited Plasma lock screen
  remains available. NoxForge does not ship a private lock-screen
  implementation.
- `splash-test.png` records the available splash test process, but that process
  displayed its generic test presentation rather than proving the v5 splash
  integration.
- `alt-tab.png` records the decorated live applications used for the switcher
  attempt. The D-Bus shortcut invocation did not leave a visible switcher in
  the capture, so it is not Alt+Tab evidence.

## Blocked cases

- The virtual framebuffer cannot prove hardware-composited blur.
- No input injector is available for complete keyboard-only traversal,
  Aurorae hover/pressed transitions, a held Alt+Tab cycle or controlled cursor
  motion.
- The isolated Plasma shell did not provide a trustworthy live RTL mirroring
  result.
- The isolated runtime has no independently qualified PipeWire
  speaker/headphone route.
- SDDM test mode cannot prove PAM authentication or real power actions.

Offscreen renders and deterministic asset checks are linked only from the
automated report and do not satisfy any live case.
