import QtQuick
import QtQuick.Controls

Button {
    id: root
    property bool accent: false
    property bool danger: false
    property bool compact: false

    implicitHeight: compact ? 34 : 38
    leftPadding: compact ? 12 : 15
    rightPadding: compact ? 12 : 15

    background: Rectangle {
        radius: 9
        color: root.accent
            ? (root.down ? Theme.accentPressed : root.hovered ? Theme.accentHover : Theme.accent)
            : root.danger
                ? (root.hovered ? (Theme.light ? "#FCE8EC" : "#2A1D23") : (Theme.light ? "#FFF3F5" : "#211A1E"))
                : (root.hovered ? Theme.hover : Theme.input)
        border.width: 1
        border.color: root.accent
            ? Theme.accentHover
            : root.danger
                ? (Theme.light ? "#E8BAC5" : "#55303A")
                : Theme.border

        Behavior on color { ColorAnimation { duration: 110 } }
    }

    contentItem: Text {
        text: root.text
        color: root.danger ? Theme.danger : root.accent ? "#FFFFFF" : Theme.text
        font.pixelSize: 11
        font.weight: Font.DemiBold
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
}
