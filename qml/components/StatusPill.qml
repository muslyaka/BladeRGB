import QtQuick
import QtQuick.Layouts
Rectangle {
    id: root
    property bool online: false
    property string label: ""
    implicitWidth: row.implicitWidth + 22
    implicitHeight: 34
    radius: 9
    color: Theme.input
    border.width: 1
    border.color: Theme.border
    Row {
        id: row
        anchors.centerIn: parent
        spacing: 8
        Rectangle { width: 7; height: 7; radius: 4; color: root.online ? Theme.success : Theme.textSubtle }
        Text { text: root.label; color: Theme.textSecondary; font.pixelSize: 9; font.weight: Font.DemiBold }
    }
}
