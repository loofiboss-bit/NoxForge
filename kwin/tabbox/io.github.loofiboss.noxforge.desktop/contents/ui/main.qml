// SPDX-License-Identifier: MIT
pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
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
        property alias currentIndex: windowList.currentIndex
        visible: tabBox.visible
        flags: Qt.Popup | Qt.X11BypassWindowManagerHint
        location: PlasmaCore.Types.Floating
        x: tabBox.screenGeometry.x + (tabBox.screenGeometry.width - width) / 2
        y: tabBox.screenGeometry.y + (tabBox.screenGeometry.height - height) / 2

        mainItem: ListView {
            id: windowList
            width: Math.min(tabBox.screenGeometry.width * 0.72, Kirigami.Units.gridUnit * 54)
            height: Math.min(contentHeight, tabBox.screenGeometry.height * 0.66)
            model: tabBox.model
            spacing: Kirigami.Units.smallSpacing
            clip: true
            focus: true
            highlightMoveDuration: 140

            delegate: Rectangle {
                id: windowDelegate
                required property int index
                required property string caption
                required property var icon
                required property bool minimized
                width: windowList.width
                height: Kirigami.Units.gridUnit * 3
                color: index === windowList.currentIndex ? "#26361D" : "#141B21"
                border.color: index === windowList.currentIndex ? "#A3FF47" : "#2B3942"
                border.width: 1
                radius: 6

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.smallSpacing
                    spacing: Kirigami.Units.smallSpacing
                    Kirigami.Icon { source: windowDelegate.icon; Layout.preferredWidth: 24; Layout.preferredHeight: 24 }
                    Text { text: windowDelegate.caption; color: windowDelegate.minimized ? "#6F7C82" : "#E8F0F2"; elide: Text.ElideRight; Layout.fillWidth: true }
                }
                TapHandler {
                    onTapped: {
                        windowList.currentIndex = windowDelegate.index
                        windowList.model.activate(windowDelegate.index)
                    }
                }
            }
        }
    }
}
