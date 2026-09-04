import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    property bool online: false
    property string label: ""

    implicitWidth: row.implicitWidth + 22
    implicitHeight: 34
    radius: 9
    color: "#191C22"
    border.width: 1
    border.color: "#292D36"

    Row {
        id: row
        anchors.centerIn: parent
        spacing: 8

        Rectangle {
            width: 7
            height: 7
            radius: 4
            color: root.online ? "#67C49C" : "#606572"
        }

        Text {
            text: root.label
            color: "#B9BDC7"
            font.pixelSize: 9
            font.weight: Font.DemiBold
        }
    }
}
