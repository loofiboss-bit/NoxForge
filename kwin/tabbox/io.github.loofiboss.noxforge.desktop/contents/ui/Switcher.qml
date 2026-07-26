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
    property bool reducedMotion: Kirigami.Units.longDuration <= 0
    readonly property int cardWidth: Math.min(screenGeometry.width * 0.72, Kirigami.Units.gridUnit * 54)
    readonly property int cardHeight: Math.min(
        Math.max(windowList.contentHeight, Kirigami.Units.gridUnit * 5),
        screenGeometry.height * 0.66
    )
    width: compositionMode ? screenGeometry.width : cardWidth
    height: compositionMode ? screenGeometry.height : cardHeight

    function focusFirstAction() {
        windowList.forceActiveFocus()
    }

    Tokens { id: tokens }

    Rectangle {
        anchors.fill: parent
        visible: root.compositionMode
        color: tokens.background
    }

    Rectangle {
        id: card
        anchors.centerIn: parent
        width: root.cardWidth
        height: root.cardHeight
        color: tokens.surface
        border.color: tokens.border
        border.width: tokens.borderWidth
        radius: tokens.radius

        Text {
            id: emptyState
            anchors.centerIn: parent
            width: parent.width - Kirigami.Units.gridUnit * 2
            visible: windowList.count === 0
            text: qsTr("No windows available")
            color: tokens.textSecondary
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }

        ListView {
            id: windowList
            anchors.fill: parent
            anchors.margins: tokens.standardSpacing
            model: root.windowModel
            currentIndex: root.currentIndex
            spacing: Kirigami.Units.smallSpacing
            clip: true
            focus: true
            boundsBehavior: Flickable.StopAtBounds
            highlightMoveDuration: root.reducedMotion
                ? tokens.reducedMotionDuration
                : Math.min(tokens.hoverDuration, Kirigami.Units.shortDuration)
            onCurrentIndexChanged: root.currentIndex = currentIndex
            LayoutMirroring.enabled: Qt.locale().textDirection === Qt.RightToLeft
            LayoutMirroring.childrenInherit: true

            delegate: Rectangle {
                id: windowDelegate
                required property int index
                required property string caption
                required property var icon
                required property bool minimized
                width: windowList.width
                height: Kirigami.Units.gridUnit * 3
                color: index === windowList.currentIndex ? tokens.surfaceSelected : tokens.surface
                border.color: index === windowList.currentIndex ? tokens.borderStrong : tokens.border
                border.width: tokens.borderWidth
                radius: tokens.radius

                Rectangle {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: tokens.activeMarkerWidth
                    height: parent.height - Kirigami.Units.gridUnit
                    color: tokens.accent
                    visible: windowDelegate.index === windowList.currentIndex
                }
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.smallSpacing * 2
                    spacing: Kirigami.Units.smallSpacing
                    Kirigami.Icon {
                        source: windowDelegate.icon
                        Layout.preferredWidth: 24
                        Layout.preferredHeight: 24
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 0
                        Text {
                            text: windowDelegate.caption
                            color: windowDelegate.minimized ? tokens.textSecondary : tokens.textPrimary
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                        Text {
                            text: qsTr("Minimized")
                            visible: windowDelegate.minimized
                            color: tokens.textDisabled
                            font.pixelSize: 11
                        }
                    }
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
}
