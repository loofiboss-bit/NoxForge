# Artwork inventory and provenance

All shipped visual assets are original NoxForge project work and are licensed
under the repository's MIT License. No artwork from Breeze or another theme is
included. Installed KDE assets and upstream documentation were inspected only
for package layout and required identifiers.

The wallpaper composition was explored with an OpenAI-generated concept using
the locked NoxForge palette. The concept image is not shipped. The final
wallpaper was authored separately as editable project-owned vector geometry in
`wallpapers/NoxForge/contents/source/NoxForge.svg` and is deterministically
rendered to `contents/images/2560x1440.png`.

The Aurorae decoration and all 24 icon SVGs are emitted from original geometry
in `scripts/generate_visual_assets.py`. Their generated SVG files are committed
so they can be inspected, edited, installed, and validated without network
access.

## Icon coverage

- Actions: `configure`, `document-new`, `document-open`, `document-save`,
  `edit-copy`, `edit-delete`, `edit-paste`, `system-search`.
- Places: `folder`, `folder-open`, `network-workgroup`, `user-desktop`,
  `user-home`.
- Devices: `audio-card`, `computer`, `drive-harddisk`, `input-keyboard`,
  `input-mouse`, `phone`.
- Status: `audio-volume-high`, `battery-good`, `dialog-warning`,
  `network-wired`, `network-wireless`.

Icons not listed above deliberately resolve through
`breeze-dark,breeze,hicolor` inheritance.
