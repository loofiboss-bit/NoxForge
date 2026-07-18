# Fedora KDE 44 manual visual gate

Run this checklist in a Plasma 6.7+ Wayland session after user-local
installation. Record evidence before any tag or publication. Unavailable checks
remain **Pending** and must never be reported as passed.

| Check | 100% | 140% | Notes |
| --- | --- | --- | --- |
| Panel edges and floating panel have no seams | Pending | Pending | Live Plasma required |
| Popup/dialog surfaces are readable with blur enabled | Pending | Pending | Live Plasma required |
| Popup/dialog surfaces are readable with blur disabled | Pending | Pending | Live Plasma required |
| Button hover, focus, pressed, and toolbutton states are clear | Pending | Pending | Live Plasma required |
| Task normal, hover, focus, attention, minimized, and progress states are clear | Pending | Pending | Live Plasma required |
| Selection, line edit, heading, and tooltip states are intact | Pending | Pending | Live Plasma required |
| Aurorae active/inactive, maximized, restore, minimize, and close states are not clipped | Pending | Pending | Live KWin required |
| All 24 icons are clear and an intentionally missing icon falls back to Breeze | Pending | Pending | System Settings and app views required |
| Wallpaper and core shell assets form a recognizable design together | Pending | Pending | Desktop review required |

Also confirm that changing the system accent updates the SVG elements using
`ColorScheme-Highlight`, while cyan and violet remain subordinate details.

Automated SVG rendering checks are useful structural evidence but do not close
these live graphical checks.
