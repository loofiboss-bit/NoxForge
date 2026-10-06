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
    property real shakeOffset: 0
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

    SequentialAnimation {
        id: errorShakeAnim
        running: false
        loops: 1
        alwaysRunToEnd: true
        NumberAnimation { target: root; property: "shakeOffset"; to: -8; duration: 40; easing.type: Easing.OutQuad }
        NumberAnimation { target: root; property: "shakeOffset"; to: 8; duration: 40; easing.type: Easing.InOutQuad }
        NumberAnimation { target: root; property: "shakeOffset"; to: -4; duration: 40; easing.type: Easing.InOutQuad }
        NumberAnimation { target: root; property: "shakeOffset"; to: 4; duration: 40; easing.type: Easing.InOutQuad }
        NumberAnimation { target: root; property: "shakeOffset"; to: 0; duration: 60; easing.type: Easing.InOutQuad }
    }

    onStatusDangerChanged: {
        if (statusDanger && !root.reducedMotion) {
            errorShakeAnim.restart()
        }
    }

    onClearPassword: {
        passwordInput.text = ""
        authenticating = false
        statusMessage = ""
        passwordInput.forceActiveFocus()
    }

    function submitPassword() {
        root.cancelFaceAuthentication()
        const password = passwordInput.text
        if (password.length === 0) {
            statusMessage = qsTr("Enter password")
            statusDanger = true
            if (!root.reducedMotion) {
                errorShakeAnim.restart()
            }
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

    function hasFaceAuthenticationApi() {
        return typeof faceAuthenticator !== "undefined"
            && faceAuthenticator
            && typeof faceAuthenticator.registerThemeComponent === "function"
    }

    function faceAuthenticationBusy() {
        return root.hasFaceAuthenticationApi() && faceAuthenticator.busy
    }

    function cancelFaceAuthentication() {
        if (root.hasFaceAuthenticationApi()) {
            faceAuthenticator.cancel()
        }
    }

    // Top status row (caps lock, network, battery, indicators)
    RowLayout {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: tokens.largeSpacing ?? 24
        spacing: tokens.standardSpacing

        Kirigami.Icon {
            source: "network-wireless"
            implicitWidth: 18
            implicitHeight: 18
            opacity: 0.85
        }

        Kirigami.Icon {
            source: "battery-good"
            implicitWidth: 18
            implicitHeight: 18
            opacity: 0.85
        }

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

        // Password Input with Forge Notch & Kinetic Shake
        Rectangle {
            id: passwordBox
            Layout.fillWidth: true
            Layout.preferredHeight: tokens.largeControlHeight
            radius: tokens.radius
            color: passwordInput.activeFocus ? tokens.surface : tokens.surfaceRaised
            border.color: root.statusDanger
                ? tokens.negative
                : (passwordInput.activeFocus ? tokens.accent : tokens.outlineMuted)
            border.width: (passwordInput.activeFocus || root.statusDanger) ? tokens.focusWidth : tokens.borderWidth
            transform: Translate { x: root.shakeOffset }

            Behavior on color {
                enabled: !root.reducedMotion
                ColorAnimation {
                    duration: motion.duration(tokens.productiveDuration)
                    easing.type: Easing.Bezier
                    easing.bezierCurve: tokens.productiveEnterCurve
                }
            }
            Behavior on border.color {
                enabled: !root.reducedMotion
                ColorAnimation {
                    duration: motion.duration(tokens.productiveDuration)
                    easing.type: Easing.Bezier
                    easing.bezierCurve: tokens.productiveEnterCurve
                }
            }

            // Forge Notch Accent
            Rectangle {
                visible: passwordInput.activeFocus
                width: tokens.notch
                height: tokens.notch
                x: 0
                y: 0
                color: root.statusDanger ? tokens.negative : tokens.accent
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

                    onTextEdited: root.cancelFaceAuthentication()
                    Keys.onReturnPressed: root.submitPassword()
                    Keys.onEnterPressed: root.submitPassword()
                    Keys.onEscapePressed: {
                        const faceAttemptWasActive = root.faceAuthenticationBusy()
                        root.cancelFaceAuthentication()
                        if (!faceAttemptWasActive) {
                            passwordInput.text = ""
                        }
                    }
                }

                // Unlock action button with micro-motion
                Rectangle {
                    id: submitButton
                    implicitWidth: 32
                    implicitHeight: 32
                    radius: tokens.compactRadius
                    scale: submitArea.pressed ? 0.94 : (submitArea.containsMouse ? 1.06 : 1.0)
                    color: submitArea.containsMouse
                        ? tokens.accentPressed
                        : (passwordInput.text.length > 0 ? tokens.accent : tokens.surfaceOverlay)
                    border.color: tokens.accent
                    border.width: passwordInput.text.length > 0 ? 1 : 0

                    Behavior on scale {
                        enabled: !root.reducedMotion
                        NumberAnimation { duration: motion.duration(tokens.pressDuration); easing.type: Easing.OutQuad }
                    }
                    Behavior on color {
                        enabled: !root.reducedMotion
                        ColorAnimation {
                            duration: motion.duration(tokens.pressDuration)
                            easing.type: Easing.Bezier
                            easing.bezierCurve: tokens.productiveEnterCurve
                        }
                    }

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

        Loader {
            id: faceAuthenticationControl
            property var loadedControl: item
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            Layout.preferredHeight: loadedControl && loadedControl.visible ? loadedControl.implicitHeight : 0
            active: root.hasFaceAuthenticationApi()
            source: active ? "qrc:/fallbacktheme/FaceAuthenticationControl.qml" : ""
        }

        Connections {
            target: faceAuthenticationControl.loadedControl
            function onUsePasswordRequested() {
                passwordInput.forceActiveFocus()
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
