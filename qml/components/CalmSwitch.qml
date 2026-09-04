import QtQuick
import QtQuick.Controls

Switch {
    id: root
    implicitWidth: 42
    implicitHeight: 24

    indicator: Rectangle {
        implicitWidth: 38
        implicitHeight: 22
        radius: 11
        color: root.checked ? "#6964B4" : "#2B2F38"
        border.width: 1
        border.color: root.checked ? "#7772C9" : "#373B45"

        Rectangle {
            width: 16
            height: 16
            radius: 8
            x: root.checked ? parent.width - width - 3 : 3
            anchors.verticalCenter: parent.verticalCenter
            color: root.checked ? "#F2F1FA" : "#A0A5B0"

            Behavior on x {
                NumberAnimation { duration: 120; easing.type: Easing.OutCubic }
            }
        }
    }

    contentItem: Item {}
}
