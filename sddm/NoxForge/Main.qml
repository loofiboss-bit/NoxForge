// SPDX-License-Identifier: MIT
pragma ComponentBehavior: Bound
import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: 1600
    height: 900
    color: "#0E1318"
    focus: true

    property string statusMessage: ""
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property bool sessionMenuOpen: false

    LayoutMirroring.enabled: Qt.locale().textDirection === Qt.RightToLeft
    LayoutMirroring.childrenInherit: true

    function requestLogin() {
        statusMessage = "Authenticating…"
        sddm.login(usernameInput.text, passwordInput.text, sessionIndex)
    }

    component ForgeButton: Rectangle {
        id: button
        property string label: ""
        property bool primary: false
        property bool interactive: true
        signal clicked()
        implicitHeight: 36
        implicitWidth: 112
        radius: 6
        color: !interactive ? "#141B21" : primary ? (mouse.pressed ? "#82D936" : "#A3FF47") : (mouse.containsMouse ? "#202C34" : "#1A232B")
        border.color: primary ? "#A3FF47" : mouse.containsMouse ? "#3B4B55" : "#2B3942"
        opacity: interactive ? 1 : 0.55
        Text { anchors.centerIn: parent; text: button.label; color: button.primary ? "#0E1318" : "#E8F0F2"; font.weight: button.primary ? Font.DemiBold : Font.Normal }
        MouseArea { id: mouse; anchors.fill: parent; hoverEnabled: true; enabled: button.interactive; onClicked: button.clicked() }
    }

    Image {
        anchors.fill: parent
        source: config.background
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }
    Rectangle { anchors.fill: parent; color: "#990E1318" }

    Item {
        anchors.fill: parent
        clip: true
        Rectangle { x: -120; y: root.height * 0.22; width: root.width * 0.54; height: 74; color: "#141B21"; rotation: 12 }
        Rectangle { x: -40; y: root.height * 0.42; width: root.width * 0.42; height: 7; color: "#A3FF47"; rotation: -11 }
        Rectangle { x: root.width * 0.26; y: root.height * 0.40; width: 7; height: root.height * 0.28; color: "#A3FF47"; rotation: -42 }
    }

    Text {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 32
        text: "NOXFORGE"
        color: "#E8F0F2"
        font.pixelSize: 18
        font.weight: Font.DemiBold
        font.letterSpacing: 3
    }

    Column {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 32
        spacing: 2
        Text { id: clockText; anchors.right: parent.right; color: "#E8F0F2"; font.pixelSize: 30; font.weight: Font.DemiBold }
        Text { id: dateText; anchors.right: parent.right; color: "#A6B4B9"; font.pixelSize: 13 }
        Timer {
            interval: 1000
            running: true
            repeat: true
            triggeredOnStart: true
            onTriggered: {
                const now = new Date()
                clockText.text = Qt.formatTime(now, "HH:mm")
                dateText.text = Qt.formatDate(now, "dddd d MMMM yyyy")
            }
        }
    }

    Rectangle {
        id: loginCard
        anchors.centerIn: parent
        width: Math.min(root.width - 48, 420)
        height: form.implicitHeight + 64
        radius: 6
        color: "#F2141B21"
        border.color: "#2B3942"

        Rectangle { anchors.left: parent.left; anchors.top: parent.top; width: 64; height: 3; color: "#A3FF47" }

        ColumnLayout {
            id: form
            anchors.centerIn: parent
            width: parent.width - 64
            spacing: 12

            Text { text: "SIGN IN"; color: "#E8F0F2"; font.pixelSize: 22; font.weight: Font.DemiBold; font.letterSpacing: 2 }
            Text { text: "Industrial Precision session"; color: "#A6B4B9"; font.pixelSize: 13; Layout.bottomMargin: 8 }

            Rectangle {
                Layout.fillWidth: true; implicitHeight: 36; radius: 6; color: "#0E1318"; border.color: usernameInput.activeFocus ? "#A3FF47" : "#2B3942"
                TextInput { id: usernameInput; anchors.fill: parent; anchors.margins: 9; color: "#E8F0F2"; selectionColor: "#26361D"; selectedTextColor: "#E8F0F2"; text: userModel.lastUser; focus: true; clip: true; KeyNavigation.tab: passwordInput }
            }
            Rectangle {
                Layout.fillWidth: true; implicitHeight: 36; radius: 6; color: "#0E1318"; border.color: passwordInput.activeFocus ? "#A3FF47" : "#2B3942"
                TextInput { id: passwordInput; anchors.fill: parent; anchors.margins: 9; color: "#E8F0F2"; selectionColor: "#26361D"; selectedTextColor: "#E8F0F2"; echoMode: TextInput.Password; passwordCharacter: "•"; clip: true; onAccepted: root.requestLogin() }
            }

            ForgeButton { label: "Session"; Layout.fillWidth: true; onClicked: root.sessionMenuOpen = !root.sessionMenuOpen }
            ColumnLayout {
                visible: root.sessionMenuOpen
                Layout.fillWidth: true
                spacing: 4
                Repeater {
                    model: sessionModel
                    ForgeButton {
                        required property int index
                        required property string name
                        label: name
                        primary: index === root.sessionIndex
                        Layout.fillWidth: true
                        onClicked: { root.sessionIndex = index; root.sessionMenuOpen = false }
                    }
                }
            }

            Text { text: root.statusMessage; color: root.statusMessage === "Login failed" ? "#FF6B7A" : "#A6B4B9"; font.pixelSize: 12; visible: text.length > 0 }
            ForgeButton { label: "Sign in"; primary: true; Layout.fillWidth: true; onClicked: root.requestLogin() }
        }
    }

    Row {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: 8
        ForgeButton { label: keyboard.layouts[keyboard.currentLayout]?.longName ?? "Keyboard"; visible: keyboard.layouts.length > 1; onClicked: keyboard.currentLayout = (keyboard.currentLayout + 1) % keyboard.layouts.length }
        ForgeButton { label: "Sleep"; interactive: sddm.canSuspend; onClicked: sddm.suspend() }
        ForgeButton { label: "Restart"; interactive: sddm.canReboot; onClicked: sddm.reboot() }
        ForgeButton { label: "Shut down"; interactive: sddm.canPowerOff; onClicked: sddm.powerOff() }
    }

    Connections {
        target: sddm
        function onLoginFailed() { root.statusMessage = "Login failed"; passwordInput.text = ""; passwordInput.forceActiveFocus() }
        function onLoginSucceeded() { root.statusMessage = "Session ready" }
    }
}
