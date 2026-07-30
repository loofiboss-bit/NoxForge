// SPDX-License-Identifier: MIT
// qmllint disable unqualified
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: root
    width: screenGeometry.width
    height: screenGeometry.height
    property bool reducedMotion: motion.reducedMotion
    property real testProgress: -1
    property bool entryReady: false
    property real entryProgress: testProgress >= 0 ? testProgress : entryReady ? 1 : 0

    Tokens { id: tokens }
    MotionPolicy { id: motion }

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
        required property string iconName
        property bool danger: false
        signal clicked()
        implicitHeight: tokens.largeControlHeight
        radius: tokens.radius
        color: activeFocus
            ? tokens.surfaceSelected
            : pointer.containsMouse
            ? tokens.surfaceHover
            : tokens.surfaceRaised
        border.color: activeFocus
            ? tokens.accent
            : pointer.containsMouse
            ? tokens.edgeHighlight
            : tokens.outlineMuted
        border.width: activeFocus ? tokens.focusWidth : tokens.borderWidth
        activeFocusOnTab: true
        Accessible.role: Accessible.Button
        Accessible.name: label

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: tokens.standardSpacing
            anchors.rightMargin: tokens.standardSpacing
            spacing: tokens.compactSpacing
            Kirigami.Icon {
                source: button.iconName
                Layout.preferredWidth: Kirigami.Units.iconSizes.smallMedium
                Layout.preferredHeight: Kirigami.Units.iconSizes.smallMedium
            }
            Text {
                Layout.fillWidth: true
                text: button.label
                color: button.danger && (pointer.containsMouse || button.activeFocus)
                    ? tokens.negative
                    : tokens.textPrimary
                font.pixelSize: tokens.controlLabelSize
                horizontalAlignment: Text.AlignLeft
                elide: Text.ElideRight
            }
            Rectangle {
                Layout.preferredWidth: tokens.activeMarkerWidth
                Layout.preferredHeight: Kirigami.Units.gridUnit
                color: button.danger ? tokens.negative : tokens.accent
                opacity: button.activeFocus || pointer.containsMouse ? 1 : 0
                Behavior on opacity {
                    enabled: !root.reducedMotion
                    NumberAnimation { duration: motion.duration(tokens.productiveDuration) }
                }
            }
        }
        Behavior on color {
            enabled: !root.reducedMotion
            ColorAnimation {
                duration: motion.duration(tokens.productiveDuration)
                easing.type: Easing.Bezier
                easing.bezierCurve: tokens.productiveEnterCurve
            }
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

    Rectangle {
        anchors.fill: parent
        color: tokens.background
        opacity: tokens.scrimOpacity
    }

    Rectangle {
        id: decisionCard
        anchors.horizontalCenter: parent.horizontalCenter
        width: Math.min(
            parent.width - Kirigami.Units.gridUnit * 3,
            Math.max(Kirigami.Units.gridUnit * 34, parent.width * 0.36)
        )
        height: actionColumn.implicitHeight + Kirigami.Units.gridUnit * 4
        y: (parent.height - height) / 2
            + (root.reducedMotion ? 0 : tokens.standardSpacing * (1 - root.entryProgress))
        opacity: root.entryProgress
        color: tokens.surfaceOverlay
        border.color: tokens.edgeHighlight
        border.width: tokens.borderWidth
        radius: tokens.overlayRadius
        Rectangle {
            width: Kirigami.Units.gridUnit * 3
            height: tokens.activeMarkerWidth
            color: tokens.accent
            anchors.left: parent.left
            anchors.top: parent.top
        }

        ColumnLayout {
            id: actionColumn
            anchors.centerIn: parent
            width: parent.width - Kirigami.Units.gridUnit * 4
            spacing: tokens.compactSpacing

            RowLayout {
                Layout.fillWidth: true
                Layout.bottomMargin: Kirigami.Units.largeSpacing
                Image {
                    source: "NoxForgeMark.svg"
                    Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                    Layout.preferredHeight: Kirigami.Units.gridUnit * 2.25
                    fillMode: Image.PreserveAspectFit
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text {
                        text: qsTr("Session actions")
                        color: tokens.textPrimary
                        font.pixelSize: tokens.surfaceTitleSize
                        font.weight: tokens.headingWeight
                    }
                    Text {
                        text: qsTr("Choose what should happen next")
                        color: tokens.textSecondary
                        font.pixelSize: tokens.metadataSize
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }
            }

            Text {
                text: qsTr("Session")
                color: tokens.textSecondary
                font.pixelSize: tokens.sectionTitleSize
                font.weight: tokens.headingWeight
                Layout.topMargin: tokens.compactSpacing
            }
            RowLayout {
                Layout.fillWidth: true
                ForgeButton {
                    id: lockButton
                    label: qsTr("Lock")
                    iconName: "security-high"
                    Layout.fillWidth: true
                    KeyNavigation.tab: logoutButton
                    KeyNavigation.backtab: cancelButton
                    onClicked: root.lockScreenRequested()
                }
                ForgeButton {
                    id: logoutButton
                    label: qsTr("Log out")
                    iconName: "application-exit"
                    Layout.fillWidth: true
                    KeyNavigation.tab: sleepButton
                    KeyNavigation.backtab: lockButton
                    onClicked: root.logoutRequested()
                }
            }

            Text {
                text: qsTr("Power")
                color: tokens.textSecondary
                font.pixelSize: tokens.sectionTitleSize
                font.weight: tokens.headingWeight
                Layout.topMargin: Kirigami.Units.largeSpacing
            }
            RowLayout {
                Layout.fillWidth: true
                ForgeButton {
                    id: sleepButton
                    label: qsTr("Sleep")
                    iconName: "preferences-system-power-management"
                    Layout.fillWidth: true
                    KeyNavigation.tab: restartButton
                    KeyNavigation.backtab: logoutButton
                    onClicked: root.suspendRequested(2)
                }
                ForgeButton {
                    id: restartButton
                    label: qsTr("Restart")
                    iconName: "view-refresh"
                    danger: true
                    Layout.fillWidth: true
                    KeyNavigation.tab: shutdownButton
                    KeyNavigation.backtab: sleepButton
                    onClicked: root.rebootRequested()
                }
                ForgeButton {
                    id: shutdownButton
                    label: qsTr("Shut down")
                    iconName: "preferences-system-power-management"
                    danger: true
                    Layout.fillWidth: true
                    KeyNavigation.tab: cancelButton
                    KeyNavigation.backtab: restartButton
                    onClicked: root.haltRequested()
                }
            }

            ForgeButton {
                id: cancelButton
                label: qsTr("Cancel")
                iconName: "dialog-cancel"
                Layout.fillWidth: true
                Layout.topMargin: Kirigami.Units.largeSpacing
                KeyNavigation.tab: lockButton
                KeyNavigation.backtab: shutdownButton
                onClicked: root.cancelRequested()
            }
        }
    }

    Behavior on entryProgress {
        enabled: root.testProgress < 0 && !root.reducedMotion
        NumberAnimation {
            duration: motion.duration(tokens.containerDuration)
            easing.type: Easing.Bezier
            easing.bezierCurve: tokens.productiveEnterCurve
        }
    }
    Component.onCompleted: entryReady = true
}
