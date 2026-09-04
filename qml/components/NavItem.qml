import QtQuick
import QtQuick.Controls

Button {
    id: root
    property bool selected: false
    property string glyph: "•"

    implicitHeight: 44

    background: Rectangle {
        radius: 9
        color: root.selected
            ? "#20232B"
            : root.hovered
                ? "#191C22"
                : "transparent"

        Rectangle {
            visible: root.selected
            width: 3
            height: 20
            radius: 2
            color: "#817BD0"
            anchors.left: parent.left
            anchors.leftMargin: 1
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    contentItem: Row {
        spacing: 10
        leftPadding: 12

        Text {
            width: 20
            text: root.glyph
            color: root.selected ? "#A7A2E0" : "#6F7584"
            font.pixelSize: 14
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            text: root.text
            color: root.selected ? "#F0F1F5" : "#9297A5"
            font.pixelSize: 12
            font.weight: root.selected ? Font.DemiBold : Font.Normal
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
