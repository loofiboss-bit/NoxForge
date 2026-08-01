# NoxForge v6 isolated Wayland qualification

Captured on 2026-08-01 in separate KWin 6.7.3 virtual Wayland sessions on
Fedora KDE 44. The runs used a temporary `HOME`, XDG configuration tree,
runtime directory, D-Bus session, and Wayland socket. NoxForge was installed
only into the temporary home. A composite SHA-256 over the maintainer KDE and
SDDM configuration remained
`ec3527073cbd9fecba101850f45d3d275cfc24ad2bf6e349d11f5fc6922b7bd2`
before and after the qualification.

## Passed observations

- `plasma-multi-output.png` shows two independent 1280 by 720 outputs with the
  v6 wallpaper, Plasma Style, icons, and panel composed by KWin.
- The isolated panel configuration SHA-256 remained
  `bd8c6a3cc0d883c7208e91d3403fec1b8793543f96d87c1fa45600b795827c26`
  before and after `plasma-apply-lookandfeel`; the panel count remained one.
- `panel-edges.png` contains live bottom, top, left, and right panel
  placements from Plasma's scripting API. All four placements are seam-free.
- `qt-composed-140.png` shows a real System Settings process under KWin at
  scale 1.4 using the NoxForge Qt style and Aurorae decoration.
- Required shell icons are distinct on horizontal and vertical panels, and no
  missing Plasma artwork is visible.

## Available processes with limited claims

- `aurorae-composed.png` shows Aurorae around real applications, but it does
  not prove every active, inactive, maximized, hover, and press transition.
- `logout-test.png` is the real windowed Plasma logout greeter, and
  `sddm-test-mode.png` is the real SDDM greeter in test mode.
- The splash test runner displayed its generic KDE test presentation, so that
  capture was rejected and is not committed as v6 live evidence.

## Blocked cases

- The virtual framebuffer cannot prove hardware-composited blur.
- No trusted input injector is available for complete Qt motion, Logout
  keyboard/pointer flow, Aurorae hover/press transitions, a held Alt+Tab
  cycle, or controlled cursor motion and scaling.
- SDDM test mode cannot prove PAM authentication or real power actions.
- Production splash integration is not proven by the generic test runner.

Offscreen renders and deterministic asset checks are linked only from the
automated report and do not satisfy any live case.
