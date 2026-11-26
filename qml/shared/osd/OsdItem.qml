// SPDX-License-Identifier: MIT
// qmllint disable unqualified
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

RowLayout {
    id: root
    spacing: tokens.standardSpacing * 1.5

    Tokens { id: tokens }
    MotionPolicy { id: motion }

    property string icon: ""
    property int value: 0
    property int maxValue: 100
    property string label: ""
    property bool showingProgress: true
    property bool mute: false
    property bool reducedMotion: motion.reducedMotion

    readonly property real normalizedProgress: maxValue > 0
        ? Math.max(0.0, Math.min(1.0, value / maxValue))
        : 0.0

    Kirigami.Icon {
        source: root.icon !== "" ? root.icon : "audio-volume-high"
        Layout.preferredWidth: Kirigami.Units.iconSizes.medium
        Layout.preferredHeight: Kirigami.Units.iconSizes.medium
        Accessible.role: Accessible.Graphic
        Accessible.name: qsTr("OSD status icon")
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: tokens.compactSpacing

        RowLayout {
            Layout.fillWidth: true
            spacing: tokens.standardSpacing

            Text {
                Layout.fillWidth: true
                visible: root.label.length > 0
                text: root.label
                color: tokens.textPrimary
                font.pixelSize: tokens.controlLabelSize
                elide: Text.ElideRight
            }

            Text {
                visible: root.showingProgress
                text: root.mute ? qsTr("Muted") : Math.round(root.normalizedProgress * 100) + "%"
                color: root.mute ? tokens.negative : tokens.textPrimary
                font.pixelSize: tokens.metadataSize
                font.weight: tokens.headingWeight
                font.features: ({ "tnum": 1 })
                Accessible.name: qsTr("OSD level readout")
            }
        }

        Rectangle {
            id: track
            visible: root.showingProgress
            Layout.fillWidth: true
            Layout.minimumWidth: 160
            implicitHeight: 6
            radius: 3
            color: tokens.surfaceSunken
            border.color: tokens.border
            border.width: tokens.borderWidth

            Rectangle {
                height: parent.height
                width: root.mute ? 0 : Math.round(parent.width * root.normalizedProgress)
                radius: 3
                color: root.normalizedProgress > 1.0 ? tokens.neutral : tokens.accent
                Behavior on width {
                    enabled: !root.reducedMotion
                    NumberAnimation {
                        duration: motion.duration(tokens.productiveDuration)
                        easing.type: Easing.Bezier
                        easing.bezierCurve: tokens.productiveEnterCurve
                    }
                }
            }
        }
    }
}
