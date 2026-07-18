// SPDX-License-Identifier: MIT
import QtQuick
import org.kde.kirigami as Kirigami

Rectangle {
    id: root
    color: "#0E1318"
    property int stage: 0

    Item {
        id: mark
        width: Kirigami.Units.gridUnit * 9
        height: Kirigami.Units.gridUnit * 7
        anchors.centerIn: parent
        opacity: root.stage >= 1 ? 1 : 0

        Behavior on opacity { NumberAnimation { duration: 180 } }

        Rectangle {
            width: parent.width
            height: Kirigami.Units.smallSpacing
            y: parent.height * 0.42
            color: "#A3FF47"
            rotation: -11
            transformOrigin: Item.Left
        }
        Rectangle {
            width: parent.width * 0.62
            height: Kirigami.Units.smallSpacing
            x: parent.width * 0.19
            y: parent.height * 0.56
            color: "#A3FF47"
            rotation: 46
            transformOrigin: Item.Left
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.bottom
            anchors.topMargin: Kirigami.Units.largeSpacing
            color: "#E8F0F2"
            font.pixelSize: Kirigami.Units.gridUnit
            font.weight: Font.DemiBold
            font.letterSpacing: 2
            text: "NOXFORGE"
        }
    }

    Rectangle {
        width: Math.max(Kirigami.Units.gridUnit * 2, parent.width * Math.min(root.stage, 5) / 5)
        height: 2
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        color: "#A3FF47"
        Behavior on width { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
    }
}
