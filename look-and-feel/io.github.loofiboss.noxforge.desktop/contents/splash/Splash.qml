// SPDX-License-Identifier: MIT
import QtQuick
import org.kde.kirigami as Kirigami

Rectangle {
    id: root
    color: tokens.background
    property int stage: 0
    readonly property int animationDuration: Kirigami.Units.shortDuration
    Tokens { id: tokens }

    Column {
        anchors.centerIn: parent
        spacing: Kirigami.Units.largeSpacing
        opacity: root.stage >= 1 ? 1 : 0
        Image { source: "NoxForgeMark.svg"; width: Kirigami.Units.gridUnit * 10; height: Kirigami.Units.gridUnit * 7.5; fillMode: Image.PreserveAspectFit }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            color: tokens.textPrimary
            font.pixelSize: Kirigami.Units.gridUnit
            font.weight: Font.DemiBold
            font.letterSpacing: tokens.brandTracking
            text: "NOXFORGE"
        }
        Behavior on opacity { NumberAnimation { duration: root.animationDuration } }
    }

    Rectangle {
        width: Math.max(Kirigami.Units.gridUnit * 2, parent.width * Math.min(root.stage, 5) / 5)
        height: tokens.focusWidth
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        color: tokens.accent
        Behavior on width { NumberAnimation { duration: root.animationDuration; easing.type: Easing.OutCubic } }
    }
}
