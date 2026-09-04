import QtQuick
import QtQuick.Controls

TextField {
    id: root
    implicitHeight: 40
    color: "#E8E9EE"
    placeholderTextColor: "#646A77"
    selectionColor: "#5E5A9E"
    selectedTextColor: "white"
    font.pixelSize: 11
    leftPadding: 12
    rightPadding: 12

    background: Rectangle {
        radius: 9
        color: root.activeFocus ? "#1D2027" : "#191C22"
        border.width: 1
        border.color: root.activeFocus ? "#5F5A9E" : "#2A2E37"
    }
}
