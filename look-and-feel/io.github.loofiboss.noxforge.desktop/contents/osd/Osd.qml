// GENERATED from qml/shared/osd/Osd.qml — do not edit directly
// SPDX-License-Identifier: MIT
// qmllint disable unqualified
import QtQuick

Item {
    id: root
    implicitWidth: Math.max(260, contentItem.implicitWidth + tokens.standardSpacing * 4)
    implicitHeight: Math.max(48, contentItem.implicitHeight + tokens.standardSpacing * 3)

    Tokens { id: tokens }
    MotionPolicy { id: motion }

    property string icon: ""
    property var osdValue: 0
    property int osdMaxValue: 100
    property string osdAdditionalText: ""
    property bool showingProgress: false
    property bool mute: false
    property bool reducedMotion: motion.reducedMotion

    Accessible.role: Accessible.StatusBar
    Accessible.name: qsTr("On-screen display")

    Rectangle {
        id: card
        anchors.fill: parent
        radius: tokens.overlayRadius
        color: tokens.surfaceOverlay
        border.color: root.mute ? tokens.negative : tokens.edgeHighlight
        border.width: tokens.borderWidth

        // Forge 4px precision accent rail
        Rectangle {
            id: forgeRail
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: tokens.borderWidth
            width: tokens.activeMarkerWidth
            height: Math.max(12, parent.height - tokens.standardSpacing * 3)
            radius: 1.5
            color: root.mute ? tokens.negative : tokens.accent
        }

        OsdItem {
            id: contentItem
            anchors.centerIn: parent
            width: parent.width - tokens.standardSpacing * 4
            icon: root.icon
            value: typeof root.osdValue === "number" ? root.osdValue : 0
            maxValue: root.osdMaxValue
            label: root.osdAdditionalText
            showingProgress: root.showingProgress
            mute: root.mute
            reducedMotion: root.reducedMotion
        }
    }
}
