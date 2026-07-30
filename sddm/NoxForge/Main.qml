// SPDX-License-Identifier: MIT
// qmllint disable unqualified
pragma ComponentBehavior: Bound
import QtQuick 2.15
import QtQuick.Layouts 1.15
import org.kde.kirigami.platform as Platform

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
    property bool authenticating: false
    property bool reducedMotion: motion.reducedMotion
    property real testProgress: -1
    property bool entryReady: false
    property real entryProgress: testProgress >= 0 ? testProgress : entryReady ? 1 : 0

    QtObject {
        id: motion
        readonly property real durationScale: Platform.Units.shortDuration <= 0
            ? 0
            : Platform.Units.shortDuration / 100.0
        readonly property bool reducedMotion: durationScale <= 0
        function duration(baseDuration) {
            return reducedMotion ? 0 : Math.max(1, Math.round(baseDuration * durationScale))
        }
    }

    Component {
        id: busyGlyph
        Text {
            text: "↻"
            color: tokens.detailCyan
            font.pixelSize: tokens.controlLabelSize
            rotation: root.testProgress >= 0 ? root.testProgress * 360 : 0
            RotationAnimation on rotation {
                running: !root.reducedMotion && root.testProgress < 0
                loops: Animation.Infinite
                from: 0
                to: 360
                duration: motion.duration(tokens.busyCycleDuration)
            }
        }
    }

    LayoutMirroring.enabled: Qt.locale().textDirection === Qt.RightToLeft
    LayoutMirroring.childrenInherit: true

    function requestLogin() {
        if (usernameField.editor.text.trim().length === 0 || passwordField.editor.text.length === 0) {
            statusMessage = qsTr("Enter both username and password")
            statusDanger = true
            return
        }
        statusMessage = qsTr("Authenticating…")
        statusDanger = false
        authenticating = true
        sddm.login(usernameField.editor.text, passwordField.editor.text, sessionIndex)
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
        property bool busy: false
        signal clicked()
        activeFocusOnTab: interactive
        implicitHeight: tokens.largeControlHeight
        implicitWidth: 112
        radius: tokens.radius
        color: busy
            ? tokens.surfaceRaised
            : !interactive
            ? tokens.surface
            : primary
            ? (mouse.pressed ? tokens.accentPressed : tokens.accent)
            : (mouse.containsMouse || activeFocus ? tokens.surfaceHover : tokens.surfaceRaised)
        border.color: activeFocus ? tokens.accent : mouse.containsMouse ? tokens.borderStrong : tokens.border
        border.width: activeFocus ? tokens.focusWidth : tokens.borderWidth
        opacity: interactive || busy ? 1 : tokens.disabledOpacity
        Accessible.role: Accessible.Button
        Accessible.name: label
        Accessible.description: danger ? qsTr("System power action") : ""

        Text {
            anchors.centerIn: parent
            width: parent.width - tokens.standardSpacing * 2
            text: button.busy ? qsTr("Authenticating…") : button.label
            color: button.busy
                ? tokens.detailCyan
                : button.primary
                ? tokens.accentInk
                : button.danger && (mouse.containsMouse || button.activeFocus)
                ? tokens.negative
                : tokens.textPrimary
            font.weight: button.primary ? Font.DemiBold : Font.Normal
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }
        Loader {
            anchors.right: parent.right
            anchors.rightMargin: tokens.standardSpacing
            anchors.verticalCenter: parent.verticalCenter
            active: button.busy
            sourceComponent: busyGlyph
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
        Text { text: field.label; color: tokens.textSecondary; font.pixelSize: tokens.metadataSize; elide: Text.ElideRight; Layout.fillWidth: true }
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: tokens.largeControlHeight
            radius: tokens.radius
            color: tokens.background
            border.color: editor.activeFocus ? tokens.accent : tokens.border
            border.width: editor.activeFocus ? tokens.focusWidth : tokens.borderWidth
            Behavior on border.color {
                enabled: !root.reducedMotion
                ColorAnimation { duration: motion.duration(tokens.productiveDuration) }
            }
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
    Rectangle { anchors.fill: parent; color: tokens.background; opacity: tokens.scrimOpacity }

    Image {
        width: Platform.Units.gridUnit * 14
        height: Platform.Units.gridUnit * 4
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: Platform.Units.gridUnit * 2
        source: "NoxForgeLockup.svg"
        fillMode: Image.PreserveAspectFit
    }

    Column {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: Platform.Units.gridUnit * 2
        spacing: tokens.compactSpacing
        Text { id: clockText; anchors.right: parent.right; text: Qt.formatTime(root.currentDateTime, "HH:mm"); color: tokens.textPrimary; font.pixelSize: tokens.displayClockSize; font.weight: tokens.headingWeight }
        Text { id: dateText; anchors.right: parent.right; text: Qt.formatDate(root.currentDateTime, "dddd d MMMM yyyy"); color: tokens.textSecondary; font.pixelSize: tokens.metadataSize }
        Timer {
            interval: 1000; running: true; repeat: true; triggeredOnStart: true
            onTriggered: if (!root.freezeClock) root.currentDateTime = new Date()
        }
    }

    Rectangle {
        id: loginCard
        width: Math.min(root.width - 48, 440)
        height: form.implicitHeight + 64
        x: root.width >= 1600
            ? Math.min(root.width - width - Platform.Units.gridUnit * 4, root.width * 0.62)
            : (root.width - width) / 2
        y: (root.height - height) / 2 + (root.reducedMotion ? 0 : tokens.standardSpacing * (1 - root.entryProgress))
        opacity: root.entryProgress
        radius: tokens.overlayRadius
        color: tokens.surfaceOverlay
        border.color: tokens.edgeHighlight
        border.width: tokens.borderWidth
        Rectangle { anchors.left: parent.left; anchors.top: parent.top; width: 64; height: tokens.activeMarkerWidth; color: tokens.accent }

        ColumnLayout {
            id: form
            anchors.centerIn: parent
            width: parent.width - 64
            spacing: tokens.standardSpacing + tokens.compactSpacing
            Text { text: qsTr("Sign in"); color: tokens.textPrimary; font.pixelSize: tokens.surfaceTitleSize; font.weight: tokens.headingWeight }
            Text { text: qsTr("Kinetic Precision session"); color: tokens.textSecondary; font.pixelSize: tokens.metadataSize; Layout.bottomMargin: tokens.compactSpacing }

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
                KeyNavigation.tab: root.sessionMenuOpen && sessionChoices.count > 0
                    ? sessionChoices.itemAt(0)
                    : loginButton
                KeyNavigation.backtab: passwordField.editor
                onClicked: {
                    root.sessionMenuOpen = !root.sessionMenuOpen
                    if (root.sessionMenuOpen && sessionChoices.count > 0) {
                        sessionChoices.itemAt(0).forceActiveFocus()
                    }
                }
            }
            Item {
                Layout.fillWidth: true
                implicitHeight: root.sessionMenuOpen ? sessionChoiceColumn.implicitHeight : 0
                Layout.preferredHeight: implicitHeight
                clip: true
                opacity: root.sessionMenuOpen ? 1 : 0
                Behavior on implicitHeight {
                    enabled: !root.reducedMotion
                    NumberAnimation {
                        duration: motion.duration(tokens.containerDuration)
                        easing.type: Easing.Bezier
                        easing.bezierCurve: tokens.productiveEnterCurve
                    }
                }
                Behavior on opacity {
                    enabled: !root.reducedMotion
                    NumberAnimation { duration: motion.duration(tokens.productiveDuration) }
                }
                ColumnLayout {
                    id: sessionChoiceColumn
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: tokens.compactSpacing
                    Repeater {
                        id: sessionChoices
                        model: sessionModel
                        ForgeButton {
                            required property int index
                            required property string name
                            label: name
                            primary: index === root.sessionIndex
                            Layout.fillWidth: true
                            KeyNavigation.tab: index + 1 < sessionChoices.count
                                ? sessionChoices.itemAt(index + 1)
                                : loginButton
                            KeyNavigation.backtab: index > 0
                                ? sessionChoices.itemAt(index - 1)
                                : sessionButton
                            onClicked: { root.sessionIndex = index; root.sessionMenuOpen = false; sessionButton.forceActiveFocus() }
                        }
                    }
                }
            }

            Text {
                id: statusText
                Layout.fillWidth: true
                Layout.minimumHeight: 40
                Layout.maximumHeight: 40
                text: root.statusMessage
                color: root.statusDanger ? tokens.negative : tokens.textSecondary
                font.pixelSize: tokens.metadataSize
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
                busy: root.authenticating
                interactive: !root.authenticating
                Layout.fillWidth: true
                KeyNavigation.tab: keyboardButton.visible ? keyboardButton : sleepButton
                KeyNavigation.backtab: root.sessionMenuOpen && sessionChoices.count > 0
                    ? sessionChoices.itemAt(sessionChoices.count - 1)
                    : sessionButton
                onClicked: root.requestLogin()
            }
        }
    }

    ForgeButton {
        id: keyboardButton
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: Platform.Units.gridUnit * 1.5
        label: keyboard.layouts[keyboard.currentLayout]?.longName ?? qsTr("Keyboard")
        visible: keyboard.layouts.length > 1
        KeyNavigation.tab: sleepButton
        KeyNavigation.backtab: loginButton
        onClicked: keyboard.currentLayout = (keyboard.currentLayout + 1) % keyboard.layouts.length
    }

    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: Platform.Units.gridUnit * 1.5
        spacing: tokens.compactSpacing
        ForgeButton { id: sleepButton; label: qsTr("Sleep"); interactive: sddm.canSuspend; KeyNavigation.tab: rebootButton; KeyNavigation.backtab: keyboardButton.visible ? keyboardButton : loginButton; onClicked: sddm.suspend() }
        ForgeButton { id: rebootButton; label: qsTr("Restart"); danger: true; interactive: sddm.canReboot; KeyNavigation.tab: powerOffButton; KeyNavigation.backtab: sleepButton; onClicked: sddm.reboot() }
        ForgeButton { id: powerOffButton; label: qsTr("Shut down"); danger: true; interactive: sddm.canPowerOff; KeyNavigation.tab: usernameField.editor; KeyNavigation.backtab: rebootButton; onClicked: sddm.powerOff() }
    }

    Connections {
        target: sddm
        function onLoginFailed() { root.authenticating = false; root.statusMessage = qsTr("Login failed"); root.statusDanger = true; passwordField.editor.text = ""; passwordField.editor.forceActiveFocus() }
        function onLoginSucceeded() { root.authenticating = false; root.statusMessage = qsTr("Session ready"); root.statusDanger = false }
    }

    onStatusMessageChanged: statusReplacement.restart()
    NumberAnimation {
        id: statusReplacement
        target: statusText
        property: "opacity"
        from: tokens.inactiveOpacity
        to: tokens.enabledOpacity
        duration: motion.duration(tokens.productiveDuration)
    }

    Behavior on entryProgress {
        enabled: root.testProgress < 0 && !root.reducedMotion
        NumberAnimation {
            duration: motion.duration(tokens.containerDuration)
            easing.type: Easing.Bezier
            easing.bezierCurve: tokens.productiveEnterCurve
        }
    }
    Timer {
        interval: motion.duration(tokens.staggerDuration)
        running: !root.reducedMotion && root.testProgress < 0
        repeat: false
        onTriggered: root.entryReady = true
    }
    Component.onCompleted: if (root.reducedMotion) entryReady = true
}
