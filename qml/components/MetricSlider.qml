import QtQuick
import QtQuick.Controls

Item {
    id: root
    property string label: ""
    property real value: 0
    property real from: 0
    property real to: 1
    property real stepSize: 0.01
    property int decimals: 2
    property string suffix: ""
    signal changed(real value)

    implicitHeight: 52

    Text {
        text: root.label
        color: "#A2A7B3"
        font.pixelSize: 11
        anchors.left: parent.left
        anchors.top: parent.top
    }

    Text {
        text: Number(slider.value).toFixed(root.decimals) + root.suffix
        color: "#D9DBE2"
        font.pixelSize: 10
        font.weight: Font.DemiBold
        anchors.right: parent.right
        anchors.top: parent.top
    }

    Slider {
        id: slider
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        from: root.from
        to: root.to
        stepSize: root.stepSize
        value: root.value
        onMoved: root.changed(value)

        background: Rectangle {
            x: slider.leftPadding
            y: slider.topPadding + slider.availableHeight / 2 - height / 2
            width: slider.availableWidth
            height: 4
            radius: 2
            color: "#2A2E37"

            Rectangle {
                width: slider.visualPosition * parent.width
                height: parent.height
                radius: 2
                color: "#7772C9"
            }
        }

        handle: Rectangle {
            x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
            y: slider.topPadding + slider.availableHeight / 2 - height / 2
            width: 14
            height: 14
            radius: 7
            color: "#E8E6F5"
            border.width: 2
            border.color: "#625E9E"
        }
    }
}
