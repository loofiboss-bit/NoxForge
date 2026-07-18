// SPDX-License-Identifier: MIT
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

Item {
    id: root
    width: screenGeometry.width
    height: screenGeometry.height

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

    Rectangle { anchors.fill: parent; color: "#D90E1318" }

    Rectangle {
        anchors.centerIn: parent
        width: Math.min(parent.width - 48, Kirigami.Units.gridUnit * 34)
        height: actionColumn.implicitHeight + Kirigami.Units.gridUnit * 4
        color: "#141B21"
        border.color: "#2B3942"
        border.width: 1
        radius: 6

        Rectangle { width: 44; height: 2; color: "#A3FF47"; anchors.left: parent.left; anchors.top: parent.top }

        ColumnLayout {
            id: actionColumn
            anchors.centerIn: parent
            width: parent.width - Kirigami.Units.gridUnit * 4
            spacing: Kirigami.Units.smallSpacing

            PlasmaComponents.Label {
                text: qsTr("Session")
                color: "#E8F0F2"
                font.pixelSize: Kirigami.Units.gridUnit * 1.4
                font.weight: Font.DemiBold
                Layout.bottomMargin: Kirigami.Units.largeSpacing
            }
            PlasmaComponents.Button { text: qsTr("Lock"); Layout.fillWidth: true; onClicked: root.lockScreenRequested() }
            PlasmaComponents.Button { text: qsTr("Log Out"); Layout.fillWidth: true; onClicked: root.logoutRequested() }
            PlasmaComponents.Button { text: qsTr("Sleep"); Layout.fillWidth: true; onClicked: root.suspendRequested(2) }
            PlasmaComponents.Button { text: qsTr("Restart"); Layout.fillWidth: true; onClicked: root.rebootRequested() }
            PlasmaComponents.Button { text: qsTr("Shut Down"); Layout.fillWidth: true; onClicked: root.haltRequested() }
            PlasmaComponents.Button { text: qsTr("Cancel"); Layout.fillWidth: true; onClicked: root.cancelRequested() }
        }
    }
}
