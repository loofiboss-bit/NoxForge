// SPDX-License-Identifier: MIT
// qmllint disable unqualified
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

Item {
    id: root
    width: screenGeometry.width
    height: screenGeometry.height
    Tokens { id: tokens }

    signal logoutRequested()
    signal haltRequested()
    signal haltUpdateRequested()
    signal suspendRequested(int method)
    signal rebootRequested()
    signal rebootRequested2(int option)
    signal rebootUpdateRequested()
    signal cancelRequested()
    signal lockScreenRequested()
    signal cancelSoftwareUpdateRequested()

    function focusFirstAction() {
        lockButton.forceActiveFocus()
    }

    LayoutMirroring.enabled: Qt.locale().textDirection === Qt.RightToLeft
    LayoutMirroring.childrenInherit: true

    Rectangle { anchors.fill: parent; color: tokens.background; opacity: 0.9 }

    Rectangle {
        anchors.centerIn: parent
        width: Math.min(parent.width - 48, Kirigami.Units.gridUnit * 34)
        height: actionColumn.implicitHeight + Kirigami.Units.gridUnit * 4
        color: tokens.surface
        border.color: tokens.border
        border.width: tokens.borderWidth
        radius: tokens.radius
        Rectangle { width: 52; height: tokens.activeMarkerWidth; color: tokens.accent; anchors.left: parent.left; anchors.top: parent.top }

        ColumnLayout {
            id: actionColumn
            anchors.centerIn: parent
            width: parent.width - Kirigami.Units.gridUnit * 4
            spacing: Kirigami.Units.smallSpacing

            RowLayout {
                Layout.fillWidth: true
                Layout.bottomMargin: Kirigami.Units.largeSpacing
                Image { source: "NoxForgeMark.svg"; Layout.preferredWidth: 48; Layout.preferredHeight: 36; fillMode: Image.PreserveAspectFit }
                ColumnLayout {
                    PlasmaComponents.Label { text: qsTr("Session"); color: tokens.textPrimary; font.pixelSize: Kirigami.Units.gridUnit * 1.35; font.weight: Font.DemiBold }
                    PlasmaComponents.Label { text: qsTr("Choose what should happen next"); color: tokens.textSecondary; elide: Text.ElideRight; Layout.fillWidth: true }
                }
            }

            PlasmaComponents.Label { text: qsTr("SESSION"); color: tokens.textSecondary; font.weight: Font.DemiBold; Layout.topMargin: Kirigami.Units.smallSpacing }
            RowLayout {
                Layout.fillWidth: true
                PlasmaComponents.Button { id: lockButton; text: qsTr("Lock"); Layout.fillWidth: true; activeFocusOnTab: true; KeyNavigation.tab: logoutButton; onClicked: root.lockScreenRequested() }
                PlasmaComponents.Button { id: logoutButton; text: qsTr("Log Out"); Layout.fillWidth: true; activeFocusOnTab: true; KeyNavigation.tab: sleepButton; onClicked: root.logoutRequested() }
            }

            PlasmaComponents.Label { text: qsTr("POWER"); color: tokens.textSecondary; font.weight: Font.DemiBold; Layout.topMargin: Kirigami.Units.largeSpacing }
            RowLayout {
                Layout.fillWidth: true
                PlasmaComponents.Button { id: sleepButton; text: qsTr("Sleep"); Layout.fillWidth: true; activeFocusOnTab: true; KeyNavigation.tab: restartButton; onClicked: root.suspendRequested(2) }
                PlasmaComponents.Button { id: restartButton; text: qsTr("Restart"); Layout.fillWidth: true; activeFocusOnTab: true; KeyNavigation.tab: shutdownButton; onClicked: root.rebootRequested() }
                PlasmaComponents.Button { id: shutdownButton; text: qsTr("Shut Down"); Layout.fillWidth: true; activeFocusOnTab: true; KeyNavigation.tab: cancelButton; onClicked: root.haltRequested() }
            }

            PlasmaComponents.Button { id: cancelButton; text: qsTr("Cancel"); Layout.fillWidth: true; Layout.topMargin: Kirigami.Units.largeSpacing; activeFocusOnTab: true; KeyNavigation.tab: lockButton; onClicked: root.cancelRequested() }
        }
    }
}
