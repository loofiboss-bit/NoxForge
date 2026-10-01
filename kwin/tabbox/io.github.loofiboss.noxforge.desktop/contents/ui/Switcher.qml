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
    readonly property bool isRtl: Qt.locale().textDirection === Qt.RightToLeft
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

    function selectPrevious() {
        if (windowList.count <= 0) return
        if (windowList.currentIndex <= 0) {
            windowList.currentIndex = windowList.count - 1
        } else {
            windowList.decrementCurrentIndex()
        }
        windowList.positionViewAtIndex(windowList.currentIndex, ListView.Contain)
        root.currentIndex = windowList.currentIndex
    }

    function selectNext() {
        if (windowList.count <= 0) return
        if (windowList.currentIndex >= windowList.count - 1) {
            windowList.currentIndex = 0
        } else {
            windowList.incrementCurrentIndex()
        }
        windowList.positionViewAtIndex(windowList.currentIndex, ListView.Contain)
        root.currentIndex = windowList.currentIndex
    }

    function activateCurrent() {
        if (windowList.currentIndex >= 0 && windowList.currentIndex < windowList.count) {
            if (windowList.model && typeof windowList.model.activate === "function") {
                windowList.model.activate(windowList.currentIndex)
            }
        }
    }

    function syncFromTabBox(index) {
        if (index >= 0 && index !== windowList.currentIndex) {
            windowList.currentIndex = index
            windowList.positionViewAtIndex(index, ListView.Contain)
            root.currentIndex = index
        }
    }

    onCurrentIndexChanged: {
        if (windowList.currentIndex !== root.currentIndex && root.currentIndex >= 0) {
            windowList.currentIndex = root.currentIndex
            windowList.positionViewAtIndex(root.currentIndex, ListView.Contain)
        }
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
            objectName: "windowList"
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
            preferredHighlightBegin: root.horizontalMode
                ? Math.round((width - root.horizontalCardWidth) / 2)
                : Math.round((height - Kirigami.Units.gridUnit * 4) / 2)
            preferredHighlightEnd: preferredHighlightBegin
            highlightMoveDuration: root.reducedMotion
                ? tokens.reducedMotionDuration
                : motion.duration(tokens.selectionDuration)
            highlightMoveVelocity: -1
            highlightFollowsCurrentItem: true
            onCurrentIndexChanged: {
                if (root.currentIndex !== currentIndex) {
                    root.currentIndex = currentIndex
                }
            }
            Keys.onReturnPressed: if (currentIndex >= 0 && model) model.activate(currentIndex)
            Keys.onSpacePressed: if (currentIndex >= 0 && model) model.activate(currentIndex)
            Keys.onLeftPressed: root.isRtl && root.horizontalMode ? root.selectNext() : root.selectPrevious()
            Keys.onRightPressed: root.isRtl && root.horizontalMode ? root.selectPrevious() : root.selectNext()
            Keys.onUpPressed: root.selectPrevious()
            Keys.onDownPressed: root.selectNext()
            Keys.onTabPressed: root.selectNext()
            Keys.onBacktabPressed: root.selectPrevious()
            Accessible.role: Accessible.List
            Accessible.name: qsTr("Open windows")
            LayoutMirroring.enabled: Qt.locale().textDirection === Qt.RightToLeft
            LayoutMirroring.childrenInherit: true

            WheelHandler {
                id: wheelHandler
                target: null
                acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                onWheel: event => {
                    const delta = event.angleDelta.y !== 0 ? event.angleDelta.y : event.angleDelta.x
                    if (delta > 0) {
                        root.selectPrevious()
                    } else if (delta < 0) {
                        root.selectNext()
                    }
                    event.accepted = true
                }
            }

            highlight: Rectangle {
                objectName: "selectionHighlight"
                z: 2
                color: "transparent"
                border.color: tokens.accent
                border.width: tokens.focusWidth
                radius: tokens.radius
            }

            delegate: Rectangle {
                id: windowDelegate
                objectName: "windowDelegate"
                required property int index
                required property string caption
                required property var icon
                required property bool minimized
                readonly property var resolvedIcon: icon === undefined || icon === null || icon === ""
                    ? "application-x-executable"
                    : icon
                readonly property bool isCurrent: index === windowList.currentIndex
                width: root.horizontalMode ? root.horizontalCardWidth : windowList.width
                height: root.horizontalMode
                    ? root.horizontalCardHeight
                    : Math.max(Kirigami.Units.gridUnit * 4, delegateContent.implicitHeight + tokens.standardSpacing * 2)
                color: isCurrent
                    ? tokens.surfaceSelected
                    : (hoverHandler.hovered ? tokens.surfaceHover : tokens.surfaceRaised)
                border.color: isCurrent
                    ? tokens.accentMuted
                    : (hoverHandler.hovered ? tokens.edgeHighlight : tokens.outlineMuted)
                border.width: tokens.borderWidth
                radius: tokens.radius
                scale: (isCurrent && !root.reducedMotion) ? 1.03 : 1.0

                Behavior on scale {
                    enabled: !root.reducedMotion
                    NumberAnimation {
                        duration: motion.duration(tokens.selectionDuration)
                        easing.type: Easing.OutQuad
                    }
                }

                HoverHandler {
                    id: hoverHandler
                }

                state: isCurrent ? "selected" : (hoverHandler.hovered ? "hovered" : "normal")
                states: [
                    State {
                        name: "normal"
                        PropertyChanges {
                            windowDelegate.color: tokens.surfaceRaised
                            windowDelegate.border.color: tokens.outlineMuted
                        }
                    },
                    State {
                        name: "hovered"
                        PropertyChanges {
                            windowDelegate.color: tokens.surfaceHover
                            windowDelegate.border.color: tokens.edgeHighlight
                        }
                    },
                    State {
                        name: "selected"
                        PropertyChanges {
                            windowDelegate.color: tokens.surfaceSelected
                            windowDelegate.border.color: tokens.accentMuted
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
                    ColorAnimation {
                        target: windowDelegate
                        property: "border.color"
                        duration: root.reducedMotion
                            ? tokens.reducedMotionDuration
                            : motion.duration(tokens.selectionDuration)
                    }
                }

                Rectangle {
                    anchors.horizontalCenter: root.horizontalMode ? parent.horizontalCenter : undefined
                    anchors.left: root.horizontalMode ? undefined : parent.left
                    anchors.bottom: root.horizontalMode ? parent.bottom : undefined
                    anchors.bottomMargin: root.horizontalMode ? tokens.compactSpacing : 0
                    anchors.verticalCenter: root.horizontalMode ? undefined : parent.verticalCenter
                    width: windowDelegate.index === windowList.currentIndex
                        ? (root.horizontalMode ? parent.width - tokens.standardSpacing * 2 : tokens.activeMarkerWidth)
                        : (root.horizontalMode ? parent.width / 3 : tokens.activeMarkerWidth)
                    height: windowDelegate.index === windowList.currentIndex
                        ? (root.horizontalMode ? tokens.activeMarkerWidth : parent.height - tokens.standardSpacing * 2)
                        : (root.horizontalMode ? tokens.activeMarkerWidth : parent.height / 3)
                    radius: tokens.activeMarkerWidth / 2
                    color: tokens.accent
                    opacity: windowDelegate.index === windowList.currentIndex ? 1 : 0
                    Behavior on opacity {
                        enabled: !root.reducedMotion
                        NumberAnimation { duration: motion.duration(tokens.productiveDuration) }
                    }
                    Behavior on width {
                        enabled: !root.reducedMotion && root.horizontalMode
                        NumberAnimation {
                            duration: motion.duration(tokens.selectionDuration)
                            easing.type: Easing.OutCubic
                        }
                    }
                    Behavior on height {
                        enabled: !root.reducedMotion && !root.horizontalMode
                        NumberAnimation {
                            duration: motion.duration(tokens.selectionDuration)
                            easing.type: Easing.OutCubic
                        }
                    }
                }

                ColumnLayout {
                    id: delegateContent
                    objectName: "delegateContent"
                    anchors.fill: parent
                    anchors.margins: tokens.standardSpacing
                    spacing: tokens.compactSpacing
                    Kirigami.Icon {
                        source: windowDelegate.resolvedIcon
                        Layout.preferredWidth: root.horizontalMode
                            ? Kirigami.Units.iconSizes.large
                            : Kirigami.Units.iconSizes.medium
                        Layout.preferredHeight: Layout.preferredWidth
                        Layout.alignment: root.horizontalMode ? Qt.AlignHCenter : Qt.AlignVCenter
                        scale: (windowDelegate.index === windowList.currentIndex && !root.reducedMotion) ? 1.08 : 1.0
                        Behavior on scale {
                            enabled: !root.reducedMotion
                            NumberAnimation {
                                duration: motion.duration(tokens.selectionDuration)
                                easing.type: Easing.OutQuad
                            }
                        }
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
                Accessible.role: Accessible.ListItem
                Accessible.name: caption
                Accessible.description: minimized ? qsTr("Minimized window") : qsTr("Window")
                TapHandler {
                    onTapped: {
                        windowList.currentIndex = windowDelegate.index
                        root.currentIndex = windowDelegate.index
                        if (windowList.model && typeof windowList.model.activate === "function") {
                            windowList.model.activate(windowDelegate.index)
                        }
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
    Component.onCompleted: {
        entryReady = true
        Qt.callLater(focusFirstAction)
    }
}
