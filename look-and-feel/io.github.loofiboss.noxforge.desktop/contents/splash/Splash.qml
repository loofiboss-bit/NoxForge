// SPDX-License-Identifier: MIT
import QtQuick
import org.kde.kirigami as Kirigami

Rectangle {
    id: root
    color: tokens.background
    property int stage: 0
    property real testProgress: -1
    property bool entryReady: false
    property real entryProgress: testProgress >= 0 ? testProgress : entryReady ? 1 : 0
    property bool reducedMotion: motion.reducedMotion
    readonly property real stageProgress: Math.max(0, Math.min(1, stage / 5))

    Tokens { id: tokens }
    MotionPolicy { id: motion }

    function focusFirstAction() {}

    Component.onCompleted: entryReady = true

    Behavior on entryProgress {
        enabled: root.testProgress < 0 && !root.reducedMotion
        NumberAnimation {
            duration: motion.duration(tokens.expressiveDuration + tokens.staggerDuration * 2)
            easing.type: Easing.Bezier
            easing.bezierCurve: tokens.expressiveCurve
        }
    }

    Column {
        anchors.centerIn: parent
        spacing: tokens.standardSpacing
        transform: Translate {
            y: root.reducedMotion ? 0 : tokens.standardSpacing * (1 - root.entryProgress)
        }

        Image {
            anchors.horizontalCenter: parent.horizontalCenter
            source: "NoxForgeMark.svg"
            width: Kirigami.Units.gridUnit * 5
            height: Kirigami.Units.gridUnit * 4
            opacity: motion.segment(root.entryProgress, 0, 0.5)
            fillMode: Image.PreserveAspectFit
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "NOXFORGE"
            color: tokens.textPrimary
            opacity: motion.segment(root.entryProgress, 0.34, 0.84)
            font.pixelSize: tokens.surfaceTitleSize
            font.weight: tokens.headingWeight
            font.letterSpacing: tokens.brandTracking
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: Kirigami.Units.gridUnit * 12
            height: tokens.borderWidth
            color: tokens.surfaceRaised

            Rectangle {
                width: parent.width * root.stageProgress
                height: parent.height
                color: tokens.accent
                Behavior on width {
                    enabled: !root.reducedMotion && root.testProgress < 0
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
