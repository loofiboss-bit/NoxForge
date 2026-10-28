
## 2024-10-21 - [Accessibility] Exposing keyboard shortcuts in tooltips and labeling dynamic inputs
**Learning:** Qt applications with dynamically generated inputs or global keyboard shortcuts often miss implicit accessibility annotations. Unlabeled sliders and hidden global shortcuts are frustrating for power users and those relying on screen readers. Explicitly assigning `setAccessibleName` to UI elements and including shortcut hints in tooltips makes the app feel vastly more discoverable.
**Action:** Always assign explicit `setAccessibleName()` to dynamically generated Qt input widgets, and append text-based shortcut hints (e.g., "(Ctrl+S)") to the tooltips of visual action buttons that trigger them.
## 2024-10-22 - [Accessibility] Utilizing setBuddy in Qt Applications
**Learning:** In Qt applications, adding labels for input controls is only half the battle. Screen readers cannot infer the visual proximity of a QLabel to its input. If they aren't explicitly linked, the accessibility context is lost, and inputs are announced generically.
**Action:** Always use `QLabel.setBuddy(input_widget)` when creating label/input pairs in PySide6 to programmatically bind them. This is the Qt equivalent of HTML's `<label for="id">` and is essential for baseline screen reader compatibility.
