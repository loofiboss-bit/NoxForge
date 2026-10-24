
## 2024-10-21 - [Accessibility] Exposing keyboard shortcuts in tooltips and labeling dynamic inputs
**Learning:** Qt applications with dynamically generated inputs or global keyboard shortcuts often miss implicit accessibility annotations. Unlabeled sliders and hidden global shortcuts are frustrating for power users and those relying on screen readers. Explicitly assigning `setAccessibleName` to UI elements and including shortcut hints in tooltips makes the app feel vastly more discoverable.
**Action:** Always assign explicit `setAccessibleName()` to dynamically generated Qt input widgets, and append text-based shortcut hints (e.g., "(Ctrl+S)") to the tooltips of visual action buttons that trigger them.

## 2024-10-24 - Remove redundant screen reader labels
**Learning:** Qt automatically exposes QCheckBox and QRadioButton label text to accessibility APIs, making redundant setAccessibleName assignments an anti-pattern that bloats the a11y tree.
**Action:** Removed redundant setAccessibleName calls on checkboxes.
