// GENERATED from qml/shared/systemdialog/SystemDialog.qml — do not edit directly
// SPDX-License-Identifier: MIT
// qmllint disable unqualified
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Rectangle {
    id: root
    implicitWidth: Math.max(360, dialogLayout.implicitWidth + tokens.standardSpacing * 6)
    implicitHeight: Math.max(180, dialogLayout.implicitHeight + tokens.standardSpacing * 6)
    radius: tokens.overlayRadius
    color: tokens.surfaceOverlay
    border.color: tokens.edgeHighlight
    border.width: tokens.borderWidth
    focus: true

    Tokens { id: tokens }
    MotionPolicy { id: motion }

    property string title: qsTr("System Confirmation")
    property string subtitle: ""
    property string iconName: "dialog-information"
    property string acceptLabel: qsTr("Confirm")
    property string rejectLabel: qsTr("Cancel")
    property bool destructive: false
    property bool reducedMotion: motion.reducedMotion

    signal accepted()
    signal rejected()

    Accessible.role: Accessible.Dialog
    Accessible.name: root.title

    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.topMargin: tokens.borderWidth
        anchors.leftMargin: tokens.standardSpacing
        width: 18
        height: 2
        color: root.destructive ? tokens.negative : tokens.accent
    }

    ColumnLayout {
        id: dialogLayout
        anchors.fill: parent
        anchors.margins: tokens.standardSpacing * 3
        spacing: tokens.standardSpacing * 2

        RowLayout {
            Layout.fillWidth: true
            spacing: tokens.standardSpacing * 2

            Kirigami.Icon {
                source: root.iconName
                Layout.preferredWidth: Kirigami.Units.iconSizes.large
                Layout.preferredHeight: Kirigami.Units.iconSizes.large
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: tokens.compactSpacing

                Text {
                    Layout.fillWidth: true
                    text: root.title
                    color: tokens.textPrimary
                    font.pixelSize: tokens.sectionTitleSize
                    font.weight: tokens.headingWeight
                    wrapMode: Text.WordWrap
                }

                Text {
                    Layout.fillWidth: true
                    visible: root.subtitle.length > 0
                    text: root.subtitle
                    color: tokens.textSecondary
                    font.pixelSize: tokens.bodySize
                    wrapMode: Text.WordWrap
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: tokens.standardSpacing
            Item { Layout.fillWidth: true }

            Rectangle {
                id: rejectBtn
                implicitWidth: rejectText.implicitWidth + tokens.standardSpacing * 3
                implicitHeight: tokens.controlHeight
                radius: tokens.compactRadius
                color: rejectHover.containsMouse ? tokens.surfaceHover : tokens.surfaceRaised
                border.color: rejectBtn.activeFocus ? tokens.accent : tokens.outlineMuted
                border.width: rejectBtn.activeFocus ? tokens.focusWidth : tokens.borderWidth
                activeFocusOnTab: true
                Accessible.role: Accessible.Button
                Accessible.name: root.rejectLabel

                Text {
                    id: rejectText
                    anchors.centerIn: parent
                    text: root.rejectLabel
                    color: tokens.textPrimary
                    font.pixelSize: tokens.controlLabelSize
                }

                MouseArea {
                    id: rejectHover
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: root.rejected()
                }
                Keys.onReturnPressed: root.rejected()
            }

            Rectangle {
                id: acceptBtn
                implicitWidth: acceptText.implicitWidth + tokens.standardSpacing * 3
                implicitHeight: tokens.controlHeight
                radius: tokens.compactRadius
                color: root.destructive ? tokens.negative : tokens.accent
                border.color: acceptBtn.activeFocus ? tokens.textPrimary : (root.destructive ? tokens.negative : tokens.accent)
                border.width: acceptBtn.activeFocus ? tokens.focusWidth : tokens.borderWidth
                activeFocusOnTab: true
                Accessible.role: Accessible.Button
                Accessible.name: root.acceptLabel

                Text {
                    id: acceptText
                    anchors.centerIn: parent
                    text: root.acceptLabel
                    color: tokens.accentInk
                    font.pixelSize: tokens.controlLabelSize
                    font.weight: tokens.headingWeight
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: root.accepted()
                }
                Keys.onReturnPressed: root.accepted()
            }
        }
    }
}
