// SPDX-License-Identifier: MIT
pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: root
    property var windowModel
    property int currentIndex: 0
    property rect screenGeometry: Qt.rect(0, 0, 1280, 720)
    property bool compositionMode: false
    property bool reducedMotion: motion.reducedMotion
    property real testProgress: -1
    property bool entryReady: false
    property real entryProgress: testProgress >= 0 ? testProgress : entryReady ? 1 : 0
    readonly property bool horizontalMode: screenGeometry.width >= 1000
    readonly property int horizontalCardWidth: Kirigami.Units.gridUnit * 13
    readonly property int horizontalCardHeight: Kirigami.Units.gridUnit * 8
    readonly property int cardWidth: horizontalMode
        ? Math.min(
            screenGeometry.width * 0.88,
            Math.max(Kirigami.Units.gridUnit * 26, windowList.count * (horizontalCardWidth + tokens.compactSpacing))
        )
        : Math.min(screenGeometry.width * 0.82, Kirigami.Units.gridUnit * 34)
    readonly property int cardHeight: horizontalMode
        ? horizontalCardHeight + Kirigami.Units.gridUnit * 4
        : Math.min(
            Math.max(windowList.contentHeight, Kirigami.Units.gridUnit * 5) + Kirigami.Units.gridUnit * 2,
            screenGeometry.height * 0.7
        )
    width: compositionMode ? screenGeometry.width : cardWidth
    height: compositionMode ? screenGeometry.height : cardHeight

    Tokens { id: tokens }
    MotionPolicy { id: motion }

    function focusFirstAction() {
        windowList.forceActiveFocus()
    }

    Rectangle {
        anchors.fill: parent
        visible: root.compositionMode
        color: tokens.background
        opacity: tokens.scrimOpacity
    }

    Rectangle {
        id: card
        anchors.horizontalCenter: parent.horizontalCenter
        width: root.cardWidth
        height: root.cardHeight
        y: (parent.height - height) / 2
            + (root.reducedMotion ? 0 : tokens.standardSpacing * (1 - root.entryProgress))
        opacity: root.entryProgress
        color: tokens.surfaceOverlay
        border.color: tokens.edgeHighlight
        border.width: tokens.borderWidth
        radius: tokens.overlayRadius

        Text {
            id: emptyState
            anchors.centerIn: parent
            width: parent.width - Kirigami.Units.gridUnit * 2
            visible: windowList.count === 0
            text: qsTr("No windows available")
            color: tokens.textSecondary
            font.pixelSize: tokens.bodySize
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }

        ListView {
            id: windowList
            anchors.fill: parent
            anchors.margins: Kirigami.Units.gridUnit
            model: root.windowModel
            currentIndex: root.currentIndex
            orientation: root.horizontalMode ? ListView.Horizontal : ListView.Vertical
            spacing: tokens.compactSpacing
            clip: true
            focus: true
            boundsBehavior: Flickable.StopAtBounds
            highlightRangeMode: ListView.ApplyRange
            preferredHighlightBegin: 0
            preferredHighlightEnd: root.horizontalMode
                ? width - root.horizontalCardWidth
                : height - Kirigami.Units.gridUnit * 4
            highlightMoveDuration: root.reducedMotion
                ? tokens.reducedMotionDuration
                : motion.duration(tokens.selectionDuration)
            highlightMoveVelocity: -1
            onCurrentIndexChanged: root.currentIndex = currentIndex
            LayoutMirroring.enabled: Qt.locale().textDirection === Qt.RightToLeft
            LayoutMirroring.childrenInherit: true

            highlight: Rectangle {
                color: "transparent"
                border.color: tokens.accent
                border.width: tokens.focusWidth
                radius: tokens.radius
            }

            delegate: Rectangle {
                id: windowDelegate
                required property int index
                required property string caption
                required property var icon
                required property bool minimized
                width: root.horizontalMode ? root.horizontalCardWidth : windowList.width
                height: root.horizontalMode
                    ? root.horizontalCardHeight
                    : Kirigami.Units.gridUnit * 4
                color: tokens.surfaceRaised
                border.color: tokens.outlineMuted
                border.width: tokens.borderWidth
                radius: tokens.radius
                state: index === windowList.currentIndex ? "selected" : "normal"
                states: [
                    State {
                        name: "normal"
                        PropertyChanges {
                            windowDelegate.color: tokens.surfaceRaised
                        }
                    },
                    State {
                        name: "selected"
                        PropertyChanges {
                            windowDelegate.color: tokens.surfaceSelected
                        }
                    }
                ]
                transitions: Transition {
                    ColorAnimation {
                        target: windowDelegate
                        property: "color"
                        duration: root.reducedMotion
                            ? tokens.reducedMotionDuration
                            : motion.duration(tokens.selectionDuration)
                    }
                }

                Rectangle {
                    anchors.left: root.horizontalMode ? parent.left : parent.left
                    anchors.right: root.horizontalMode ? parent.right : undefined
                    anchors.bottom: root.horizontalMode ? parent.bottom : undefined
                    anchors.verticalCenter: root.horizontalMode ? undefined : parent.verticalCenter
                    width: root.horizontalMode ? parent.width - tokens.standardSpacing * 2 : tokens.activeMarkerWidth
                    height: root.horizontalMode ? tokens.activeMarkerWidth : parent.height - tokens.standardSpacing * 2
                    color: tokens.accent
                    opacity: windowDelegate.index === windowList.currentIndex ? 1 : 0
                    Behavior on opacity {
                        enabled: !root.reducedMotion
                        NumberAnimation { duration: motion.duration(tokens.productiveDuration) }
                    }
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: tokens.standardSpacing
                    spacing: tokens.compactSpacing
                    Kirigami.Icon {
                        source: windowDelegate.icon
                        Layout.preferredWidth: root.horizontalMode
                            ? Kirigami.Units.iconSizes.large
                            : Kirigami.Units.iconSizes.medium
                        Layout.preferredHeight: Layout.preferredWidth
                        Layout.alignment: root.horizontalMode ? Qt.AlignHCenter : Qt.AlignVCenter
                    }
                    Text {
                        text: windowDelegate.caption
                        color: windowDelegate.minimized ? tokens.textSecondary : tokens.textPrimary
                        font.pixelSize: tokens.controlLabelSize
                        font.weight: windowDelegate.index === windowList.currentIndex
                            ? tokens.headingWeight
                            : tokens.bodyWeight
                        horizontalAlignment: root.horizontalMode ? Text.AlignHCenter : Text.AlignLeft
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                    Text {
                        text: qsTr("Minimized")
                        visible: windowDelegate.minimized
                        color: tokens.textDisabled
                        font.pixelSize: tokens.microLabelSize
                        horizontalAlignment: root.horizontalMode ? Text.AlignHCenter : Text.AlignLeft
                        Layout.fillWidth: true
                    }
                    Item { Layout.fillHeight: true; visible: root.horizontalMode }
                }
                TapHandler {
                    onTapped: {
                        windowList.currentIndex = windowDelegate.index
                        windowList.model.activate(windowDelegate.index)
                    }
                }
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
