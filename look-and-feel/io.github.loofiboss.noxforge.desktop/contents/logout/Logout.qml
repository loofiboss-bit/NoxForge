// SPDX-License-Identifier: MIT
// qmllint disable unqualified
import QtQuick
import QtQuick.Layouts
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

    component ForgeButton: Rectangle {
        id: button
        required property string label
        signal clicked()
        implicitHeight: tokens.largeControlHeight
        radius: tokens.radius
        color: activeFocus ? tokens.surfaceSelected : pointer.containsMouse ? tokens.surfaceHover : tokens.surfaceRaised
        border.color: activeFocus ? tokens.accent : tokens.border
        border.width: activeFocus ? tokens.focusWidth : tokens.borderWidth
        activeFocusOnTab: true
        Accessible.role: Accessible.Button
        Accessible.name: label

        Text {
            anchors.centerIn: parent
            width: parent.width - tokens.standardSpacing * 2
            text: button.label
            color: tokens.textPrimary
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }
        MouseArea {
            id: pointer
            anchors.fill: parent
            hoverEnabled: true
            onClicked: button.clicked()
        }
        Keys.onReturnPressed: clicked()
        Keys.onSpacePressed: clicked()
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
                    Text { text: qsTr("Session"); color: tokens.textPrimary; font.pixelSize: Kirigami.Units.gridUnit * 1.35; font.weight: Font.DemiBold }
                    Text { text: qsTr("Choose what should happen next"); color: tokens.textSecondary; elide: Text.ElideRight; Layout.fillWidth: true }
                }
            }

            Text { text: qsTr("SESSION"); color: tokens.textSecondary; font.weight: Font.DemiBold; Layout.topMargin: Kirigami.Units.smallSpacing }
            RowLayout {
                Layout.fillWidth: true
                ForgeButton { id: lockButton; label: qsTr("Lock"); Layout.fillWidth: true; KeyNavigation.tab: logoutButton; onClicked: root.lockScreenRequested() }
                ForgeButton { id: logoutButton; label: qsTr("Log Out"); Layout.fillWidth: true; KeyNavigation.tab: sleepButton; onClicked: root.logoutRequested() }
            }

            Text { text: qsTr("POWER"); color: tokens.textSecondary; font.weight: Font.DemiBold; Layout.topMargin: Kirigami.Units.largeSpacing }
            RowLayout {
                Layout.fillWidth: true
                ForgeButton { id: sleepButton; label: qsTr("Sleep"); Layout.fillWidth: true; KeyNavigation.tab: restartButton; onClicked: root.suspendRequested(2) }
                ForgeButton { id: restartButton; label: qsTr("Restart"); Layout.fillWidth: true; KeyNavigation.tab: shutdownButton; onClicked: root.rebootRequested() }
                ForgeButton { id: shutdownButton; label: qsTr("Shut Down"); Layout.fillWidth: true; KeyNavigation.tab: cancelButton; onClicked: root.haltRequested() }
            }

            ForgeButton { id: cancelButton; label: qsTr("Cancel"); Layout.fillWidth: true; Layout.topMargin: Kirigami.Units.largeSpacing; KeyNavigation.tab: lockButton; onClicked: root.cancelRequested() }
        }
    }
}
