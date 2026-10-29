
## 2024-10-21 - [Accessibility] Exposing keyboard shortcuts in tooltips and labeling dynamic inputs
**Learning:** Qt applications with dynamically generated inputs or global keyboard shortcuts often miss implicit accessibility annotations. Unlabeled sliders and hidden global shortcuts are frustrating for power users and those relying on screen readers. Explicitly assigning `setAccessibleName` to UI elements and including shortcut hints in tooltips makes the app feel vastly more discoverable.
**Action:** Always assign explicit `setAccessibleName()` to dynamically generated Qt input widgets, and append text-based shortcut hints (e.g., "(Ctrl+S)") to the tooltips of visual action buttons that trigger them.

## 2026-10-29 - [Accessibility] Link QLabels to inputs using setBuddy
**Learning:** When developing Qt/PySide6 UIs, dynamic labels lack implicit associations with inputs, creating accessibility gaps for screen readers.
**Action:** Always use `lbl.setBuddy(input_widget)` to explicitly link descriptive text to UI controls to ensure full keyboard navigation and screen reader support.
