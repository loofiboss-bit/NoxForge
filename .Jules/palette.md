
## 2024-10-21 - [Accessibility] Exposing keyboard shortcuts in tooltips and labeling dynamic inputs
**Learning:** Qt applications with dynamically generated inputs or global keyboard shortcuts often miss implicit accessibility annotations. Unlabeled sliders and hidden global shortcuts are frustrating for power users and those relying on screen readers. Explicitly assigning `setAccessibleName` to UI elements and including shortcut hints in tooltips makes the app feel vastly more discoverable.
**Action:** Always assign explicit `setAccessibleName()` to dynamically generated Qt input widgets, and append text-based shortcut hints (e.g., "(Ctrl+S)") to the tooltips of visual action buttons that trigger them.
## 2024-05-18 - Qt Label Buddies
**Learning:** In Qt/PySide6, standalone `QLabel` widgets are not automatically announced by screen readers when navigating to adjacent inputs. Using `lbl.setBuddy(input_widget)` correctly associates the label and enables click-to-focus behavior, mimicking HTML's `<label for="...">`.
**Action:** Always link standalone descriptive text labels to their adjacent interactive inputs (`QComboBox`, `QSlider`, `QTimeEdit`) using `setBuddy()`.
