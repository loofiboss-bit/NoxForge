# Plasma 6 compatibility record

Verified on 2026-07-18 against Fedora KDE 44 and current upstream
documentation. The local system reports Plasma 6.7.3, KWin 6.7.3, KDE
Frameworks packages at 6.28.0, and Fedora 44.

## Verified package contracts

| Component | User-local path | Metadata and required structure |
| --- | --- | --- |
| Plasma Style | `~/.local/share/plasma/desktoptheme/noxforge/` | `metadata.json` with a `KPlugin` object; SVG assets in `dialogs/` and `widgets/`; an optional `colors` file |
| Color scheme | `~/.local/share/color-schemes/NoxForgeDark.colors` | KDE color-scheme INI format |
| Aurorae | `~/.local/share/aurorae/themes/io.github.loofiboss.noxforge.desktop/` | `metadata.desktop`, matching `io.github.loofiboss.noxforge.desktoprc`, `decoration.svg`, and button SVGs |
| Icon theme | `~/.local/share/icons/NoxForge/` | freedesktop `index.theme`, declared directories, and inheritance |
| Wallpaper | `~/.local/share/wallpapers/NoxForge/` | image package with `metadata.json` and `contents/images/2560x1440.png` |

The Plasma Style is not a Global Theme or Look-and-Feel package. Therefore the
Plasma 6 `manifest.json` requirement for `Plasma/LookAndFeel` packages does not
apply. Look-and-Feel integration is explicitly deferred.

## Verified SVG contracts

The prototype uses the Plasma 6 nine-slice frame identifiers `top`,
`topright`, `right`, `bottomright`, `bottom`, `bottomleft`, `left`, `topleft`,
and `center`, plus file-specific prefixes documented by KDE:

- `button.svg`: `normal`, `hover`, `focus`, `pressed`, and `toolbutton-*` frames;
- `tasks.svg`: `normal`, `hover`, `focus`, `attention`, `minimized`, and
  `progress` frames, including panel-orientation variants;
- `lineedit.svg`: `base`, `hover`, and `focus` frames;
- `plasmoidheading.svg`: `header` and `footer` frames;
- `viewitem.svg`: `normal`, `hover`, `selected`, and `selected+hover` frames;
- panel, dialog, popup, and tooltip frames use the standard nine-slice IDs and
  margin/inset hints.

SVGs use a `<style id="current-color-scheme">` block and KDE's documented
`ColorScheme-*` classes. `ColorScheme-Highlight` is reserved for elements that
should follow the user's selected accent color.

Aurorae `decoration.svg` uses the standard nine-slice `decoration-*` elements,
with `decoration-inactive-*` for inactive windows. Each supplied button SVG has
at least an `active-center` element and may provide `inactive`, `hover`,
`hover-inactive`, `pressed`, `pressed-inactive`, `deactivated`, and
`deactivated-inactive` states. Aurorae has no fallback for missing button files,
so the prototype must supply every button enabled by its configuration.

## Packaging and safety decisions

- Plasma Style metadata uses JSON. The older Plasma 5 `metadata.desktop`
  format is not used for Plasma Style packages.
- No package contains symlinks.
- The icon theme inherits `breeze-dark,breeze,hicolor` in that order.
- Installation remains user-local, never changes live KDE settings, and never
  restarts Plasma Shell.
- Wayland always uses compositing. The release checklist still tests readable
  opaque surfaces with blur disabled rather than relying on the X11-only
  `opaque/` fallback mechanism.

## Sources

- KDE Plasma Style quickstart: <https://develop.kde.org/docs/plasma/theme/quickstart/>
- KDE background SVG format: <https://develop.kde.org/docs/plasma/theme/background-svg/>
- KDE system and accent colors: <https://develop.kde.org/docs/plasma/theme/theme-colors/>
- KDE theme elements reference: <https://develop.kde.org/docs/plasma/theme/theme-elements/>
- KDE Plasma 6 porting notes: <https://develop.kde.org/docs/plasma/theme/theme-porting-to-plasma6/>
- KDE Aurorae documentation: <https://develop.kde.org/docs/plasma/aurorae/>
- freedesktop icon theme specification: <https://specifications.freedesktop.org/icon-theme-spec/latest/>

Installed Fedora package contents under `/usr/share/plasma/desktoptheme/default`
were inspected only for metadata shape, package paths, filenames, and SVG
element IDs. No artwork was copied.
