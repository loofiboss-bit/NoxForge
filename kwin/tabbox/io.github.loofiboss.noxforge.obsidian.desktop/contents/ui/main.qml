// SPDX-License-Identifier: MIT
// qmllint disable unqualified
pragma ComponentBehavior: Bound
import QtQuick
import org.kde.kwin as KWin
import org.kde.plasma.core as PlasmaCore

KWin.TabBoxSwitcher {
    id: tabBox
    currentIndex: (dialogLoader.object as NoxForgeDialog)?.currentIndex ?? currentIndex

    Instantiator {
        id: dialogLoader
        active: tabBox.visible
        delegate: NoxForgeDialog { }
    }

    component NoxForgeDialog: PlasmaCore.Dialog {
        id: dialog
        property alias currentIndex: switcher.currentIndex
        visible: tabBox.visible
        flags: Qt.Popup | Qt.X11BypassWindowManagerHint
        location: PlasmaCore.Types.Floating
        x: tabBox.screenGeometry.x + (tabBox.screenGeometry.width - width) / 2
        y: tabBox.screenGeometry.y + (tabBox.screenGeometry.height - height) / 2

        mainItem: Switcher {
            id: switcher
            windowModel: tabBox.model
            screenGeometry: tabBox.screenGeometry
            currentIndex: tabBox.currentIndex

            Connections {
                target: tabBox
                function onCurrentIndexChanged() {
                    switcher.syncFromTabBox(tabBox.currentIndex)
                }
            }
        }

        onVisibleChanged: {
            if (visible) {
                switcher.syncFromTabBox(tabBox.currentIndex)
                switcher.focusFirstAction()
            }
        }

        Keys.onPressed: event => {
            if (event.key === Qt.Key_Left || event.key === Qt.Key_Up) {
                switcher.selectPrevious()
                event.accepted = true
            } else if (event.key === Qt.Key_Right || event.key === Qt.Key_Down || event.key === Qt.Key_Tab) {
                switcher.selectNext()
                event.accepted = true
            } else if (event.key === Qt.Key_Backtab) {
                switcher.selectPrevious()
                event.accepted = true
            } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
                switcher.activateCurrent()
                event.accepted = true
            }
        }

        onSceneGraphError: () => {
        }
    }
}
