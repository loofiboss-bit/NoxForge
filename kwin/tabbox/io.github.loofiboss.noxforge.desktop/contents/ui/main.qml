// SPDX-License-Identifier: MIT
// qmllint disable unqualified
pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
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
        property alias currentIndex: windowList.currentIndex
        visible: tabBox.visible
        flags: Qt.Popup | Qt.X11BypassWindowManagerHint
        location: PlasmaCore.Types.Floating
        x: tabBox.screenGeometry.x + (tabBox.screenGeometry.width - width) / 2
        y: tabBox.screenGeometry.y + (tabBox.screenGeometry.height - height) / 2

        mainItem: Item {
            width: Math.min(tabBox.screenGeometry.width * 0.72, Kirigami.Units.gridUnit * 54)
            height: Math.min(Math.max(windowList.contentHeight, emptyState.implicitHeight), tabBox.screenGeometry.height * 0.66)
            Tokens { id: tokens }

            Text {
                id: emptyState
                anchors.centerIn: parent
                visible: windowList.count === 0
                text: qsTr("No windows available")
                color: tokens.textSecondary
            }

            ListView {
                id: windowList
                anchors.fill: parent
                model: tabBox.model
                spacing: Kirigami.Units.smallSpacing
                clip: true
                focus: true
                boundsBehavior: Flickable.StopAtBounds
                highlightMoveDuration: tokens.hoverDuration
                LayoutMirroring.enabled: Qt.locale().textDirection === Qt.RightToLeft
                LayoutMirroring.childrenInherit: true

                delegate: Rectangle {
                    id: windowDelegate
                    required property int index
                    required property string caption
                    required property var icon
                    required property bool minimized
                    width: windowList.width
                    height: Kirigami.Units.gridUnit * 3
                    color: index === windowList.currentIndex ? tokens.surfaceSelected : tokens.surface
                    border.color: index === windowList.currentIndex ? tokens.borderStrong : tokens.border
                    border.width: tokens.borderWidth
                    radius: tokens.radius

                    Rectangle {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        width: tokens.activeMarkerWidth
                        height: parent.height - Kirigami.Units.gridUnit
                        color: tokens.accent
                        visible: windowDelegate.index === windowList.currentIndex
                    }
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: Kirigami.Units.smallSpacing * 2
                        spacing: Kirigami.Units.smallSpacing
                        Kirigami.Icon { source: windowDelegate.icon; Layout.preferredWidth: 24; Layout.preferredHeight: 24 }
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 0
                            Text { text: windowDelegate.caption; color: windowDelegate.minimized ? tokens.textSecondary : tokens.textPrimary; elide: Text.ElideRight; Layout.fillWidth: true }
                            Text { text: qsTr("Minimized"); visible: windowDelegate.minimized; color: tokens.textDisabled; font.pixelSize: 11 }
                        }
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
}
