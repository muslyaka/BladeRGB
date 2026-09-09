import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "pages"

ApplicationWindow {
    id: win
    visible: true
    width: 1360
    height: 840
    minimumWidth: 1080
    minimumHeight: 700
    title: "BladeRGB"
    color: Theme.background

    property string page: "dashboard"
    property string toastTitle: ""
    property string toastText: ""

    onClosing: function(close) {
        close.accepted = false
        if (controller.closeToTray) controller.hideWindow()
        else controller.quitApp()
    }

    Rectangle { anchors.fill: parent; color: Theme.background }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 204
            Layout.fillHeight: true
            color: Theme.sidebar
            Rectangle { width: 1; color: Theme.border; anchors.top: parent.top; anchors.bottom: parent.bottom; anchors.right: parent.right }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 5
                RowLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: 5
                    Layout.rightMargin: 5
                    Layout.topMargin: 5
                    Layout.bottomMargin: 21
                    spacing: 10
                    Rectangle {
                        width: 36; height: 36; radius: 10; color: Theme.accent
                        Text { anchors.centerIn: parent; text: "B"; color: "white"; font.pixelSize: 16; font.weight: Font.DemiBold }
                    }
                    Column {
                        spacing: 1
                        Text { text: "BladeRGB"; color: Theme.text; font.pixelSize: 15; font.weight: Font.DemiBold }
                        Text { text: "ARDOR BLADE"; color: Theme.textSubtle; font.pixelSize: 8; font.weight: Font.Medium }
                    }
                }

                NavItem { Layout.fillWidth: true; text: "Обзор"; glyph: "○"; selected: win.page === "dashboard"; onClicked: win.page = "dashboard" }
                NavItem { Layout.fillWidth: true; text: "Покраска"; glyph: "✦"; selected: win.page === "studio"; onClicked: win.page = "studio" }
                NavItem { Layout.fillWidth: true; text: "Слои"; glyph: "≡"; selected: win.page === "layers"; onClicked: win.page = "layers" }
                NavItem { Layout.fillWidth: true; text: "Анимация"; glyph: "◇"; selected: win.page === "animator"; onClicked: win.page = "animator" }
                NavItem { Layout.fillWidth: true; text: "Профили"; glyph: "◎"; selected: win.page === "profiles"; onClicked: win.page = "profiles" }
                NavItem { Layout.fillWidth: true; text: "Настройки"; glyph: "⚙"; selected: win.page === "settings"; onClicked: win.page = "settings" }
                Item { Layout.fillHeight: true }

                Rectangle {
                    Layout.fillWidth: true
                    height: 58
                    radius: 11
                    color: Theme.panelAlt
                    border.width: 1
                    border.color: Theme.border
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 8
                        Rectangle { width: 7; height: 7; radius: 4; color: controller.connected ? Theme.success : Theme.textSubtle }
                        Column {
                            Layout.fillWidth: true
                            spacing: 2
                            Text { text: "ARDOR BLADE"; color: Theme.text; font.pixelSize: 10; font.weight: Font.DemiBold }
                            Text { text: controller.statusText; color: Theme.textMuted; font.pixelSize: 8; font.weight: Font.Medium }
                        }
                        Text { text: controller.running ? controller.actualFps.toFixed(0) : "—"; color: Theme.accentLight; font.pixelSize: 10; font.weight: Font.DemiBold }
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Loader {
                anchors.fill: parent
                anchors.leftMargin: 28
                anchors.rightMargin: 28
                anchors.topMargin: 24
                anchors.bottomMargin: 24
                sourceComponent: win.page === "dashboard" ? dashboard : win.page === "studio" ? studio : win.page === "layers" ? layers : win.page === "animator" ? animator : win.page === "profiles" ? profiles : settings
            }
        }
    }

    Component { id: dashboard; Dashboard {} }
    Component { id: studio; Studio {} }
    Component { id: layers; Layers {} }
    Component { id: animator; Animator {} }
    Component { id: profiles; Profiles {} }
    Component { id: settings; Settings {} }

    Rectangle {
        id: toast
        width: Math.min(400, parent.width - 40)
        height: toastColumn.implicitHeight + 26
        radius: 12
        color: Theme.panel
        border.width: 1
        border.color: Theme.border
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 18
        opacity: 0
        visible: opacity > 0
        Column {
            id: toastColumn
            anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 13; spacing: 4
            Text { text: win.toastTitle; color: Theme.text; font.pixelSize: 12; font.weight: Font.DemiBold }
            Text { width: parent.width; text: win.toastText; color: Theme.textMuted; font.pixelSize: 10; wrapMode: Text.WordWrap }
        }
        Behavior on opacity { NumberAnimation { duration: 140 } }
        Timer { id: hideToast; interval: 3000; onTriggered: toast.opacity = 0 }
    }

    Connections {
        target: controller
        function onToast(title, message) { win.toastTitle = title; win.toastText = message; toast.opacity = 1; hideToast.restart() }
    }
}
