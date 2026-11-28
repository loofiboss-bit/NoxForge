// SPDX-License-Identifier: MIT
// qmllint disable unqualified
pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.private.keyboardindicator as KeyboardIndicator

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
    property bool edgeFlash: false
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

    Timer {
        id: edgeFlashTimer
        interval: 220
        repeat: false
        onTriggered: root.edgeFlash = false
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
        if (statusDanger) {
            if (root.reducedMotion) {
                root.edgeFlash = true
                edgeFlashTimer.restart()
            } else {
                errorShakeAnim.restart()
            }
        } else {
            root.edgeFlash = false
            edgeFlashTimer.stop()
        }
    }

    onClearPassword: {
        passwordInput.text = ""
        authenticating = false
        statusMessage = ""
        passwordInput.forceActiveFocus()
    }

    property bool allowEmptyPassword: false

    function submitPassword() {
        root.cancelFaceAuthentication()
        const password = passwordInput.text
        if (!root.allowEmptyPassword && password.length === 0) {
            statusMessage = qsTr("Enter password")
            statusDanger = true
            if (root.reducedMotion) {
                root.edgeFlash = true
                edgeFlashTimer.restart()
            } else {
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

    // Top status pill (network, battery, pulse dot, caps lock)
    Rectangle {
        id: forgeStatusPill
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: tokens.standardSpacing * 3
        implicitHeight: 34
        implicitWidth: statusPillRow.implicitWidth + 20
        radius: tokens.radius
        color: tokens.surfaceRaised
        border.color: passwordInput.capsLockActive ? tokens.neutral : tokens.border
        border.width: tokens.borderWidth
        Accessible.role: Accessible.Indicator
        Accessible.name: qsTr("System status pill")

        RowLayout {
            id: statusPillRow
            anchors.centerIn: parent
            spacing: tokens.standardSpacing

            Rectangle {
                id: kineticPulseDot
                implicitWidth: 8
                implicitHeight: 8
                radius: 4
                color: tokens.accent

                SequentialAnimation on opacity {
                    running: root.viewVisible && !root.reducedMotion
                    loops: Animation.Infinite
                    NumberAnimation { to: 0.45; duration: tokens.busyCycleDuration; easing.type: Easing.InOutSine }
                    NumberAnimation { to: 1.0; duration: tokens.busyCycleDuration; easing.type: Easing.InOutSine }
                }
            }

            Kirigami.Icon {
                source: "network-wireless-100"
                implicitWidth: 18
                implicitHeight: 18
                opacity: 0.9
            }

            Kirigami.Icon {
                source: "battery-100"
                implicitWidth: 18
                implicitHeight: 18
                opacity: 0.9
            }

            Rectangle {
                id: capsWarning
                visible: passwordInput.capsLockActive
                implicitHeight: 24
                implicitWidth: capsLabel.implicitWidth + 14
                radius: tokens.compactRadius
                color: tokens.surface
                border.color: tokens.neutral
                border.width: tokens.borderWidth

                Text {
                    id: capsLabel
                    anchors.centerIn: parent
                    text: qsTr("CAPS LOCK")
                    color: tokens.neutral
                    font.pixelSize: 11
                    font.weight: Font.Bold
                }
            }
        }
    }

    KeyboardIndicator.KeyState {
        id: capsLockState
        key: Qt.Key_CapsLock
    }

    Connections {
        target: typeof authenticator !== "undefined" && authenticator ? authenticator : null
        ignoreUnknownSignals: true
        function onFailed() {
            root.authenticating = false
            root.statusMessage = qsTr("Unlocking failed")
            root.statusDanger = true
            passwordInput.text = ""
            passwordInput.forceActiveFocus()
        }
        function onSucceeded() {
            root.authenticating = false
            root.statusMessage = ""
            root.statusDanger = false
        }
        function onErrorMessage(msg) {
            root.authenticating = false
            root.statusMessage = msg && msg.length > 0 ? msg : qsTr("Authentication error")
            root.statusDanger = true
        }
    }

    // Center container
    ColumnLayout {
        anchors.centerIn: parent
        spacing: tokens.standardSpacing * 3
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

        // Password Input with Forge Notch & Kinetic Shake / Static Edge-Flash
        Rectangle {
            id: passwordBox
            property bool revealPassword: false
            Layout.fillWidth: true
            Layout.preferredHeight: tokens.largeControlHeight
            radius: tokens.radius
            color: passwordInput.activeFocus ? tokens.surface : tokens.surfaceRaised
            border.color: (root.statusDanger || root.edgeFlash)
                ? tokens.negative
                : (passwordInput.activeFocus ? tokens.accent : tokens.outlineMuted)
            border.width: (passwordInput.activeFocus || root.statusDanger || root.edgeFlash) ? tokens.focusWidth : tokens.borderWidth
            transform: Translate { x: root.reducedMotion ? 0 : root.shakeOffset }

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
                color: (root.statusDanger || root.edgeFlash) ? tokens.negative : tokens.accent
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: tokens.standardSpacing + 4
                anchors.rightMargin: 4
                spacing: tokens.compactSpacing

                Timer {
                    id: lockRevealTimer
                    interval: 5000
                    repeat: false
                    onTriggered: passwordBox.revealPassword = false
                }

                QQC2.TextField {
                    id: passwordInput
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    echoMode: passwordBox.revealPassword ? TextInput.Normal : TextInput.Password
                    placeholderText: qsTr("Password")
                    placeholderTextColor: tokens.textDisabled
                    color: tokens.textPrimary
                    selectionColor: tokens.accentPressed
                    selectedTextColor: tokens.accentInk
                    font.pixelSize: 13
                    font.family: "Noto Sans, Inter, sans-serif"
                    background: null
                    focus: true
                    Accessible.role: Accessible.EditableText
                    Accessible.name: qsTr("Password")
                    Accessible.description: qsTr("Enter password to unlock")
                    readonly property bool capsLockActive: capsLockState.locked

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

                // Password visibility toggle
                Rectangle {
                    id: lockRevealBtn
                    visible: passwordInput.text.length > 0
                    implicitWidth: 26
                    implicitHeight: 26
                    radius: tokens.compactRadius
                    activeFocusOnTab: true
                    color: lockRevealArea.containsMouse ? tokens.surfaceHover : "transparent"
                    border.color: lockRevealBtn.activeFocus ? tokens.accent : "transparent"
                    border.width: lockRevealBtn.activeFocus ? tokens.focusWidth : 0
                    Accessible.role: Accessible.Button
                    Accessible.name: passwordBox.revealPassword ? qsTr("Hide password") : qsTr("Show password")

                    function toggleReveal() {
                        passwordBox.revealPassword = !passwordBox.revealPassword
                        if (passwordBox.revealPassword) {
                            lockRevealTimer.restart()
                        } else {
                            lockRevealTimer.stop()
                        }
                    }

                    Kirigami.Icon {
                        anchors.centerIn: parent
                        implicitWidth: 16
                        implicitHeight: 16
                        source: passwordBox.revealPassword ? "password-show-off" : "password-show-on"
                        color: passwordBox.revealPassword ? tokens.accent : tokens.textSecondary
                    }

                    MouseArea {
                        id: lockRevealArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: lockRevealBtn.toggleReveal()
                    }
                    Keys.onReturnPressed: lockRevealBtn.toggleReveal()
                    Keys.onEnterPressed: lockRevealBtn.toggleReveal()
                    Keys.onSpacePressed: lockRevealBtn.toggleReveal()
                }

                // Unlock action button with micro-motion
                Rectangle {
                    id: submitButton
                    implicitWidth: 32
                    implicitHeight: 32
                    radius: tokens.compactRadius
                    activeFocusOnTab: true
                    scale: submitArea.pressed ? 0.94 : (submitArea.containsMouse ? 1.06 : 1.0)
                    color: submitArea.containsMouse
                        ? tokens.accentPressed
                        : (passwordInput.text.length > 0 ? tokens.accent : tokens.surfaceOverlay)
                    border.color: submitButton.activeFocus ? tokens.textPrimary : tokens.accent
                    border.width: submitButton.activeFocus ? tokens.focusWidth : (passwordInput.text.length > 0 ? 1 : 0)
                    Accessible.role: Accessible.Button
                    Accessible.name: qsTr("Unlock")
                    Accessible.description: qsTr("Submit password to unlock")

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
                        color: (passwordInput.text.length > 0 || submitArea.containsMouse) ? tokens.accentInk : tokens.textSecondary
                    }

                    MouseArea {
                        id: submitArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.submitPassword()
                    }
                    Keys.onReturnPressed: root.submitPassword()
                    Keys.onEnterPressed: root.submitPassword()
                    Keys.onSpacePressed: root.submitPassword()
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
            Accessible.role: root.statusDanger ? Accessible.AlertMessage : Accessible.StaticText
            Accessible.name: text
        }
    }
}
