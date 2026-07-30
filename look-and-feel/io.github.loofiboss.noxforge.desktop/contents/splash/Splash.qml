// SPDX-License-Identifier: MIT
import QtQuick
import org.kde.kirigami as Kirigami

Rectangle {
    id: root
    color: tokens.background
    property int stage: 0
    property bool reducedMotion: Kirigami.Units.longDuration <= 0
    readonly property int animationDuration: reducedMotion
        ? tokens.reducedMotionDuration
        : Math.min(tokens.hoverDuration, Kirigami.Units.shortDuration)
    Tokens { id: tokens }

    function focusFirstAction() {}

    Column {
        anchors.centerIn: parent
        spacing: Kirigami.Units.largeSpacing
        opacity: root.stage >= 1 ? 1 : 0
        Image {
            source: "NoxForgeLockup.svg"
            width: Kirigami.Units.gridUnit * 22
            height: Kirigami.Units.gridUnit * 5.3
            fillMode: Image.PreserveAspectFit
        }
        Behavior on opacity {
            enabled: root.animationDuration > 0
            NumberAnimation { duration: root.animationDuration }
        }
    }

    Rectangle {
        width: Math.max(Kirigami.Units.gridUnit * 2, parent.width * Math.min(root.stage, 5) / 5)
        height: tokens.focusWidth
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        color: tokens.accent
        Behavior on width {
            enabled: root.animationDuration > 0
            NumberAnimation { duration: root.animationDuration; easing.type: Easing.OutCubic }
        }
    }
}
