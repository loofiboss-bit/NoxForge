// SPDX-License-Identifier: MIT
// qmllint disable unqualified
pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.plasma.core as PlasmaCore

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: tokens.background
    focus: true

    Tokens { id: tokens }
    MotionPolicy { id: motion }

    property bool viewVisible: false
    property string notification: ""
    property string statusMessage: ""
    property bool statusDanger: false
    property bool authenticating: false
    property bool reducedMotion: motion.reducedMotion
    property date currentDateTime: new Date()

    signal clearPassword()
    signal notificationRepeated()
    signal unlockRequested(string password)

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: root.currentDateTime = new Date()
    }

    onClearPassword: {
        passwordInput.text = ""
        authenticating = false
        statusMessage = ""
        passwordInput.forceActiveFocus()
    }

    function submitPassword() {
        const password = passwordInput.text
        if (password.length === 0) {
            statusMessage = qsTr("Enter password")
            statusDanger = true
            return
        }
        statusMessage = qsTr("Authenticating…")
        statusDanger = false
        authenticating = true
        root.unlockRequested(password)
        if (typeof authenticator !== "undefined" && authenticator && typeof authenticator.respond === "function") {
            authenticator.respond(password)
        } else if (typeof authenticator !== "undefined" && authenticator && typeof authenticator.tryUnlock === "function") {
            authenticator.tryUnlock(password)
        }
    }

    // Top status row (caps lock, battery, indicators)
    RowLayout {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: tokens.largeSpacing ?? 24
        spacing: tokens.standardSpacing

        Rectangle {
            id: capsWarning
            visible: passwordInput.capsLockActive
            implicitHeight: 26
            implicitWidth: capsLabel.implicitWidth + 16
            radius: tokens.compactRadius
            color: tokens.surfaceRaised
            border.color: tokens.neutral
            border.width: tokens.borderWidth

            RowLayout {
                anchors.centerIn: parent
                spacing: 4
                Text {
                    id: capsLabel
                    text: qsTr("CAPS LOCK")
                    color: tokens.neutral
                    font.pixelSize: 11
                    font.weight: Font.Bold
                }
            }
        }
    }

    // Center container
    ColumnLayout {
        anchors.centerIn: parent
        spacing: tokens.largeSpacing ?? 24
        width: Math.min(parent.width * 0.85, 420)

        // Brand Lockup
        Image {
            Layout.alignment: Qt.AlignHCenter
            source: "NoxForgeLockup.svg"
            sourceSize.width: 140
            sourceSize.height: 36
            smooth: true
        }

        Item { Layout.preferredHeight: 12 }

        // Clock & Date
        ColumnLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 4

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: Qt.formatTime(root.currentDateTime, "hh:mm")
                font.pixelSize: 64
                font.weight: Font.Light
                font.family: "Noto Sans, Inter, sans-serif"
                color: tokens.textPrimary
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: Qt.formatDate(root.currentDateTime, "dddd, d MMMM yyyy")
                font.pixelSize: 14
                font.weight: Font.Normal
                font.family: "Noto Sans, Inter, sans-serif"
                color: tokens.textSecondary
            }
        }

        Item { Layout.preferredHeight: 16 }

        // Password Input with Forge Notch
        Rectangle {
            id: passwordBox
            Layout.fillWidth: true
            Layout.preferredHeight: tokens.largeControlHeight
            radius: tokens.radius
            color: passwordInput.activeFocus ? tokens.surface : tokens.surfaceRaised
            border.color: passwordInput.activeFocus ? tokens.accent : tokens.outlineMuted
            border.width: passwordInput.activeFocus ? tokens.focusWidth : tokens.borderWidth

            // Forge Notch Accent
            Rectangle {
                visible: passwordInput.activeFocus
                width: tokens.notch
                height: tokens.notch
                x: 0
                y: 0
                color: tokens.accent
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: tokens.standardSpacing + 4
                anchors.rightMargin: 4
                spacing: tokens.compactSpacing

                QQC2.TextField {
                    id: passwordInput
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    echoMode: TextInput.Password
                    placeholderText: qsTr("Password")
                    placeholderTextColor: tokens.textDisabled
                    color: tokens.textPrimary
                    font.pixelSize: 13
                    font.family: "Noto Sans, Inter, sans-serif"
                    background: null
                    focus: true
                    readonly property bool capsLockActive: (passwordInput.inputMethodHints & Qt.ImhNoPredictiveText) !== 0

                    Keys.onReturnPressed: root.submitPassword()
                    Keys.onEnterPressed: root.submitPassword()
                }

                // Unlock action button
                Rectangle {
                    id: submitButton
                    implicitWidth: 32
                    implicitHeight: 32
                    radius: tokens.compactRadius
                    color: submitArea.containsMouse
                        ? tokens.accentPressed
                        : (passwordInput.text.length > 0 ? tokens.accent : tokens.surfaceOverlay)
                    border.color: tokens.accent
                    border.width: passwordInput.text.length > 0 ? 1 : 0

                    Text {
                        anchors.centerIn: parent
                        text: "→"
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        color: passwordInput.text.length > 0 ? tokens.accentInk : tokens.textDisabled
                    }

                    MouseArea {
                        id: submitArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.submitPassword()
                    }
                }
            }
        }

        // Status or error message
        Text {
            id: statusText
            Layout.alignment: Qt.AlignHCenter
            visible: root.statusMessage.length > 0 || root.notification.length > 0
            text: root.statusMessage.length > 0 ? root.statusMessage : root.notification
            color: root.statusDanger ? tokens.negative : tokens.textSecondary
            font.pixelSize: 12
        }
    }
}
