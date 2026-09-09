import QtQuick
import QtQuick.Controls
TextField {
    id: root
    implicitHeight: 40
    color: Theme.text
    placeholderTextColor: Theme.textSubtle
    selectionColor: Theme.accent
    selectedTextColor: "white"
    font.pixelSize: 11
    leftPadding: 12
    rightPadding: 12
    background: Rectangle {
        radius: 9
        color: root.activeFocus ? Theme.hover : Theme.input
        border.width: 1
        border.color: root.activeFocus ? Theme.accent : Theme.border
    }
}
