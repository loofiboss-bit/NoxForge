# NoxForge Design System

NoxForge uses an atmospheric, technical visual language called
**Industrial Precision**. This file is the visual authority for every NoxForge
component.

<!-- Hallmark · pre-emit critique: P5 H5 E4 S5 R5 V4 -->

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

## Component voice

- Selected rows use `surfaceSelected`, primary text and a lime edge/notch.
- Primary buttons use lime with graphite text; secondary buttons stay graphite.
- Focus is always visible without relying on hover or color fill alone.
- Destructive buttons become red only when hovered, pressed or confirmed.
- Active windows receive a short lime title indicator; inactive windows lose it.
- Motion is restrained: 90 ms press, 140 ms hover and 180 ms popup transitions.
  Reduced-motion environments receive immediate state changes.

## Artwork

All artwork is original NoxForge work. Installed themes may be inspected only
for technical contracts, identifiers and package structure.
