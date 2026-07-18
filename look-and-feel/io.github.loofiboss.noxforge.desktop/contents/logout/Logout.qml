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
                    PlasmaComponents.Label { text: qsTr("Choose what should happen next"); color: tokens.textSecondary }
                }
            }

            PlasmaComponents.Label { text: qsTr("SESSION"); color: tokens.textSecondary; font.weight: Font.DemiBold; Layout.topMargin: Kirigami.Units.smallSpacing }
            RowLayout {
                Layout.fillWidth: true
                PlasmaComponents.Button { text: qsTr("Lock"); Layout.fillWidth: true; onClicked: root.lockScreenRequested() }
                PlasmaComponents.Button { text: qsTr("Log Out"); Layout.fillWidth: true; onClicked: root.logoutRequested() }
            }

            PlasmaComponents.Label { text: qsTr("POWER"); color: tokens.textSecondary; font.weight: Font.DemiBold; Layout.topMargin: Kirigami.Units.largeSpacing }
            RowLayout {
                Layout.fillWidth: true
                PlasmaComponents.Button { text: qsTr("Sleep"); Layout.fillWidth: true; onClicked: root.suspendRequested(2) }
                PlasmaComponents.Button { text: qsTr("Restart"); Layout.fillWidth: true; onClicked: root.rebootRequested() }
                PlasmaComponents.Button { text: qsTr("Shut Down"); Layout.fillWidth: true; onClicked: root.haltRequested() }
            }

            PlasmaComponents.Button { text: qsTr("Cancel"); Layout.fillWidth: true; Layout.topMargin: Kirigami.Units.largeSpacing; onClicked: root.cancelRequested() }
        }
    }
}
