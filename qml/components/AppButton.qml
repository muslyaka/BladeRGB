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
            ? (root.down ? "#625EAE" : root.hovered ? "#7F79D6" : "#736EC5")
            : root.danger
                ? (root.hovered ? "#2A1D23" : "#211A1E")
                : (root.hovered ? "#22252D" : "#1D2027")
        border.width: 1
        border.color: root.accent
            ? "#8781D8"
            : root.danger
                ? "#55303A"
                : "#2B2F39"

        Behavior on color {
            ColorAnimation { duration: 110 }
        }
    }

    contentItem: Text {
        text: root.text
        color: root.danger ? "#E68A9B" : "#E7E9EF"
        font.pixelSize: 11
        font.weight: Font.DemiBold
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
}
