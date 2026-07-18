# NoxForge Design System

NoxForge uses an atmospheric, technical visual language called
**Industrial Precision**. This file is the visual authority for every NoxForge
component.

<!-- Hallmark · pre-emit critique: P5 H5 E5 S5 R5 V5 -->

## Principles

- Graphite surfaces establish depth; color never replaces hierarchy.
- Electric lime is a precision signal for focus, primary action and active
  state. It must not fill large navigation or selection areas.
- The Forge Notch is a four-pixel clipped top-left detail used only on active,
  selected or branded surfaces.
- Cyan communicates information and progress. Violet is a rare secondary brand
  detail. Red is reserved for destructive and error states.
- Controls stay compact, keyboard-visible and native to KDE behavior.

## Palette

| Token | Value | Use |
| --- | --- | --- |
| `background` | `#0E1318` | Canvas and deep views |
| `surface` | `#141B21` | Windows, panels and popups |
| `surfaceRaised` | `#1A232B` | Controls and raised regions |
| `surfaceHover` | `#202C34` | Hover without chromatic noise |
| `surfaceSelected` | `#26361D` | Large selected regions |
| `border` | `#2B3942` | Hairlines and separators |
| `borderStrong` | `#3B4B55` | Focus-adjacent structure |
| `textPrimary` | `#E8F0F2` | Primary content |
| `textSecondary` | `#A6B4B9` | Supporting content |
| `textDisabled` | `#6F7C82` | Disabled content |
| `accent` | `#A3FF47` | Focus, primary action and active markers |
| `accentPressed` | `#82D936` | Pressed primary action |
| `detailCyan` | `#22D3EE` | Information and progress |
| `detailViolet` | `#A78BFA` | Secondary identity detail |
| `negative` | `#FF6B7A` | Destructive and error states |
| `neutral` | `#FBBF24` | Warning states |

## Geometry and spacing

- Base grid: 4 px.
- Standard radius: 6 px; compact radius: 4 px.
- Forge Notch: 4 px at the top-left corner.
- Border: 1 px; focus ring: 2 px.
- Standard control height: 32 px; large control height: 36 px.
- Panels and toolbars remain compact and use spacing in 4 px increments.

## Typography

- KDE's configured system font is the only application and shell typeface.
- Body and control text use normal weight. Demi-bold is reserved for primary
  headings, the NoxForge wordmark and the current time on login surfaces.
- Letter spacing remains neutral except for the uppercase wordmark, which uses
  three pixels of tracking. Labels and section titles are never italic.
- Text must elide or wrap within its owner; interactive labels stay on one line.

## State hierarchy

1. Default controls use a plain raised graphite surface and one-pixel border.
2. Hover changes surface lightness. It does not add a glow or resize geometry.
3. Focus uses one immediate two-pixel lime indicator. A control must never draw
   both an accent border and a second focus frame.
4. Pressed controls use a darker surface or `accentPressed`; they do not scale.
5. Selected rows use `surfaceSelected` plus a three-pixel leading marker that
   mirrors in RTL. Full lime outlines around large rows are forbidden.
6. Disabled controls use `textDisabled` and 55 percent opacity while preserving
   their geometry.
7. Error and destructive states pair red with text or a glyph; color alone is
   not sufficient. Success remains quiet and uses an icon where needed.

## Forge Notch

- The four-pixel clipped top-left corner is a signature, not the default shape.
- It appears only on focused, selected, active-window or branded surfaces.
- Normal inputs, buttons, cards, menus and toolbars retain the standard radius.
- RTL mirrors leading markers, but the brand notch itself remains top-left.

## Iconography

- Canonical glyphs use a 24-pixel grid, 1.7-pixel round strokes and no embedded
  raster or text nodes.
- State-bearing icons must be semantically distinct. Connected/disconnected,
  play/pause/stop, directional, volume and battery states may not alias each
  other even when they share a family.
- Dense action, status and applet glyphs receive optical 16- and 22-pixel
  variants when the scalable source loses clarity at those sizes.
- Lime is a detail and may cover at most 12 percent of an icon. Red, cyan and
  violet keep their semantic roles from the palette.

## Surface composition

- Shell surfaces are left-biased or edge-anchored where the workflow allows it;
  centred layouts are reserved for login, logout and transient switchers.
- A surface has one containment layer. Card-in-card decoration is avoided.
- Elevation comes from lighter graphite surfaces, not colored glow shadows.
- Large lime fills are reserved for a single primary action, never navigation,
  list selection or ambient decoration.

## Component voice

- Selected rows use `surfaceSelected`, primary text and a lime edge/notch.
- Primary buttons use lime with graphite text; secondary buttons stay graphite.
- Focus is always visible without relying on hover or color fill alone.
- Destructive buttons become red only when hovered, pressed or confirmed.
- Active windows receive a short lime title indicator; inactive windows lose it.
- Motion is restrained: 90 ms press, 140 ms hover and 180 ms popup transitions.
  Reduced-motion environments receive immediate state changes.

## Component contracts

- Plasma Style owns every Plasma 6.7 widget family used by core shell flows,
  including edge-specific task and panel states and solid/translucent variants.
- The Qt style must use the same metrics and state hierarchy as Plasma Style.
- Splash, logout, Alt+Tab and SDDM consume generated physical token files; raw
  palette values are not authored independently in those QML files.
- Visible form labels, keyboard focus, RTL and stable error/status regions are
  required on login and session surfaces.

## Artwork

All artwork is original NoxForge work. Installed themes may be inspected only
for technical contracts, identifiers and package structure.
