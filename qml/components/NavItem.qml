import QtQuick
import QtQuick.Controls
Button {
    id: root
    property bool selected: false
    property string glyph: "•"
    implicitHeight: 44
    background: Rectangle {
        radius: 9
        color: root.selected ? Theme.accentSoft : root.hovered ? Theme.hover : "transparent"
        Rectangle {
            visible: root.selected
            width: 3
            height: 20
            radius: 2
            color: Theme.accent
            anchors.left: parent.left
            anchors.leftMargin: 1
            anchors.verticalCenter: parent.verticalCenter
        }
    }
    contentItem: Row {
        spacing: 10
        leftPadding: 12
        Text { width: 20; text: root.glyph; color: root.selected ? Theme.accentLight : Theme.textSubtle; font.pixelSize: 14; anchors.verticalCenter: parent.verticalCenter; horizontalAlignment: Text.AlignHCenter }
        Text { text: root.text; color: root.selected ? Theme.text : Theme.textMuted; font.pixelSize: 12; font.weight: root.selected ? Font.DemiBold : Font.Normal; anchors.verticalCenter: parent.verticalCenter }
    }
}
