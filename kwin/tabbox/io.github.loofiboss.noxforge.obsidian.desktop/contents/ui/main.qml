// SPDX-License-Identifier: MIT
// qmllint disable unqualified
pragma ComponentBehavior: Bound
import QtQuick
import org.kde.kwin as KWin
import org.kde.plasma.core as PlasmaCore

KWin.TabBoxSwitcher {
    id: tabBox
    currentIndex: (dialogLoader.object as NoxForgeDialog)?.currentIndex ?? 0

    Instantiator {
        id: dialogLoader
        active: tabBox.visible
        delegate: NoxForgeDialog { }
    }

    component NoxForgeDialog: PlasmaCore.Dialog {
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
        }
    }
}
