// SPDX-License-Identifier: MIT
// qmllint disable unqualified
pragma ComponentBehavior: Bound
import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: 1600
    height: 900
    color: tokens.background
    focus: true

    Tokens { id: tokens }
    property string statusMessage: ""
    property bool statusDanger: false
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property bool sessionMenuOpen: false
    property bool freezeClock: false
    property date currentDateTime: new Date()

    LayoutMirroring.enabled: Qt.locale().textDirection === Qt.RightToLeft
    LayoutMirroring.childrenInherit: true

    function requestLogin() {
        if (usernameInput.text.trim().length === 0 || passwordInput.text.length === 0) {
            statusMessage = qsTr("Enter both username and password")
            statusDanger = true
            return
        }
        statusMessage = qsTr("Authenticating…")
        statusDanger = false
        sddm.login(usernameInput.text, passwordInput.text, sessionIndex)
    }

    function focusFirstAction() {
        usernameField.editor.forceActiveFocus()
    }

    component ForgeButton: Rectangle {
        id: button
        property string label: ""
        property bool primary: false
        property bool danger: false
        property bool interactive: true
        signal clicked()
        activeFocusOnTab: interactive
        implicitHeight: tokens.largeControlHeight
        implicitWidth: 112
        radius: tokens.radius
        color: !interactive ? tokens.surface : primary ? (mouse.pressed ? tokens.accentPressed : tokens.accent) : (mouse.containsMouse || activeFocus ? tokens.surfaceHover : tokens.surfaceRaised)
        border.color: activeFocus ? tokens.accent : mouse.containsMouse ? tokens.borderStrong : tokens.border
        border.width: activeFocus ? tokens.focusWidth : tokens.borderWidth
        opacity: interactive ? 1 : tokens.disabledOpacity
        Accessible.role: Accessible.Button
        Accessible.name: label
        Accessible.description: danger ? qsTr("System power action") : ""

        Text {
            anchors.centerIn: parent
            width: parent.width - tokens.standardSpacing * 2
            text: button.label
            color: button.primary ? tokens.accentInk : button.danger && (mouse.containsMouse || button.activeFocus) ? tokens.negative : tokens.textPrimary
            font.weight: button.primary ? Font.DemiBold : Font.Normal
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }
        MouseArea { id: mouse; anchors.fill: parent; hoverEnabled: true; enabled: button.interactive; onClicked: button.clicked() }
        Keys.onReturnPressed: if (interactive) clicked()
        Keys.onSpacePressed: if (interactive) clicked()
    }

    component ForgeField: ColumnLayout {
        id: field
        required property string label
        property alias editor: editor
        property bool password: false
        spacing: tokens.compactSpacing
        Text { text: field.label; color: tokens.textSecondary; font.pixelSize: 12; elide: Text.ElideRight; Layout.fillWidth: true }
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: tokens.largeControlHeight
            radius: tokens.radius
            color: tokens.background
            border.color: editor.activeFocus ? tokens.accent : tokens.border
            border.width: editor.activeFocus ? tokens.focusWidth : tokens.borderWidth
            TextInput {
                id: editor
                anchors.fill: parent
                anchors.margins: tokens.standardSpacing
                color: tokens.textPrimary
                selectionColor: tokens.surfaceSelected
                selectedTextColor: tokens.textPrimary
                echoMode: field.password ? TextInput.Password : TextInput.Normal
                passwordCharacter: "•"
                clip: true
                activeFocusOnTab: true
                Accessible.role: Accessible.EditableText
                Accessible.name: field.label
            }
        }
    }

    Image { anchors.fill: parent; source: config.background; fillMode: Image.PreserveAspectCrop; asynchronous: true }
    Rectangle { anchors.fill: parent; color: Qt.rgba(tokens.background.r, tokens.background.g, tokens.background.b, 0.4) }

    Row {
        width: 220
        height: 40
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 28
        spacing: tokens.standardSpacing
        Image { source: "NoxForgeMark.svg"; width: 48; height: 36; fillMode: Image.PreserveAspectFit }
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: "NOXFORGE"
            color: tokens.textPrimary
            font.pixelSize: 18
            font.weight: Font.DemiBold
            font.letterSpacing: tokens.brandTracking
        }
    }

    Column {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 32
        spacing: tokens.compactSpacing
        Text { id: clockText; anchors.right: parent.right; text: Qt.formatTime(root.currentDateTime, "HH:mm"); color: tokens.textPrimary; font.pixelSize: 30; font.weight: Font.DemiBold }
        Text { id: dateText; anchors.right: parent.right; text: Qt.formatDate(root.currentDateTime, "dddd d MMMM yyyy"); color: tokens.textSecondary; font.pixelSize: 13 }
        Timer {
            interval: 1000; running: true; repeat: true; triggeredOnStart: true
            onTriggered: if (!root.freezeClock) root.currentDateTime = new Date()
        }
    }

    Rectangle {
        id: loginCard
        anchors.centerIn: parent
        width: Math.min(root.width - 48, 440)
        height: form.implicitHeight + 64
        radius: tokens.radius
        color: tokens.surface
        border.color: tokens.border
        Rectangle { anchors.left: parent.left; anchors.top: parent.top; width: 64; height: tokens.activeMarkerWidth; color: tokens.accent }

        ColumnLayout {
            id: form
            anchors.centerIn: parent
            width: parent.width - 64
            spacing: tokens.standardSpacing + tokens.compactSpacing
            Text { text: qsTr("SIGN IN"); color: tokens.textPrimary; font.pixelSize: 22; font.weight: Font.DemiBold; font.letterSpacing: 2 }
            Text { text: qsTr("Industrial Precision session"); color: tokens.textSecondary; font.pixelSize: 13; Layout.bottomMargin: 4 }

            ForgeField {
                id: usernameField
                label: qsTr("Username")
                Layout.fillWidth: true
                editor.text: userModel.lastUser
                editor.focus: true
                editor.KeyNavigation.tab: passwordField.editor
                editor.KeyNavigation.backtab: powerOffButton
            }
            ForgeField {
                id: passwordField
                label: qsTr("Password")
                password: true
                Layout.fillWidth: true
                editor.KeyNavigation.tab: sessionButton
                editor.KeyNavigation.backtab: usernameField.editor
                editor.onAccepted: root.requestLogin()
            }

            ForgeButton {
                id: sessionButton
                label: qsTr("Choose session") + " · " + (root.sessionIndex + 1)
                Layout.fillWidth: true
                KeyNavigation.tab: loginButton
                KeyNavigation.backtab: passwordField.editor
                onClicked: root.sessionMenuOpen = !root.sessionMenuOpen
            }
            ColumnLayout {
                visible: root.sessionMenuOpen
                Layout.fillWidth: true
                spacing: tokens.compactSpacing
                Repeater {
                    model: sessionModel
                    ForgeButton {
                        required property int index
                        required property string name
                        label: name
                        primary: index === root.sessionIndex
                        Layout.fillWidth: true
                        onClicked: { root.sessionIndex = index; root.sessionMenuOpen = false; sessionButton.forceActiveFocus() }
                    }
                }
            }

            Text {
                Layout.fillWidth: true
                Layout.minimumHeight: 40
                Layout.maximumHeight: 40
                text: root.statusMessage
                color: root.statusDanger ? tokens.negative : tokens.textSecondary
                font.pixelSize: 12
                wrapMode: Text.Wrap
                maximumLineCount: 2
                elide: Text.ElideRight
                verticalAlignment: Text.AlignVCenter
                Accessible.role: Accessible.StaticText
                Accessible.name: text
            }
            ForgeButton {
                id: loginButton
                label: qsTr("Sign in")
                primary: true
                Layout.fillWidth: true
                KeyNavigation.tab: keyboardButton.visible ? keyboardButton : sleepButton
                KeyNavigation.backtab: sessionButton
                onClicked: root.requestLogin()
            }
        }
    }

    Row {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: tokens.standardSpacing
        ForgeButton { id: keyboardButton; label: keyboard.layouts[keyboard.currentLayout]?.longName ?? qsTr("Keyboard"); visible: keyboard.layouts.length > 1; KeyNavigation.tab: sleepButton; KeyNavigation.backtab: loginButton; onClicked: keyboard.currentLayout = (keyboard.currentLayout + 1) % keyboard.layouts.length }
        ForgeButton { id: sleepButton; label: qsTr("Sleep"); interactive: sddm.canSuspend; KeyNavigation.tab: rebootButton; KeyNavigation.backtab: keyboardButton.visible ? keyboardButton : loginButton; onClicked: sddm.suspend() }
        ForgeButton { id: rebootButton; label: qsTr("Restart"); danger: true; interactive: sddm.canReboot; KeyNavigation.tab: powerOffButton; KeyNavigation.backtab: sleepButton; onClicked: sddm.reboot() }
        ForgeButton { id: powerOffButton; label: qsTr("Shut down"); danger: true; interactive: sddm.canPowerOff; KeyNavigation.tab: usernameField.editor; KeyNavigation.backtab: rebootButton; onClicked: sddm.powerOff() }
    }

    Connections {
        target: sddm
        function onLoginFailed() { root.statusMessage = qsTr("Login failed"); root.statusDanger = true; passwordField.editor.text = ""; passwordField.editor.forceActiveFocus() }
        function onLoginSucceeded() { root.statusMessage = qsTr("Session ready"); root.statusDanger = false }
    }
}
