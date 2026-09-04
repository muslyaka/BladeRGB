import QtQuick
import QtQuick.Controls

ComboBox {
    id: root
    implicitHeight: 40
    leftPadding: 12
    rightPadding: 34
    font.pixelSize: 11

    delegate: ItemDelegate {
        width: root.width
        height: 36
        highlighted: root.highlightedIndex === index

        contentItem: Text {
            text: root.textRole.length > 0
                ? (modelData[root.textRole] || "")
                : String(modelData)
            color: "#DADCE3"
            font.pixelSize: 11
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }

        background: Rectangle {
            radius: 7
            color: highlighted ? "#252832" : "transparent"
        }
    }

    indicator: Text {
        text: "⌄"
        color: "#7F8593"
        font.pixelSize: 14
        anchors.right: parent.right
        anchors.rightMargin: 11
        anchors.verticalCenter: parent.verticalCenter
    }

    contentItem: Text {
        leftPadding: 0
        rightPadding: 0
        text: root.displayText
        color: "#E4E6EC"
        font.pixelSize: 11
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        radius: 9
        color: root.hovered || root.activeFocus ? "#1E2128" : "#191C22"
        border.width: 1
        border.color: root.activeFocus ? "#5F5A9E" : "#2A2E37"
    }

    popup: Popup {
        y: root.height + 4
        width: root.width
        implicitHeight: Math.min(contentItem.implicitHeight + 8, 280)
        padding: 4

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: root.popup.visible ? root.delegateModel : null
            currentIndex: root.highlightedIndex
            ScrollIndicator.vertical: ScrollIndicator {}
        }

        background: Rectangle {
            radius: 10
            color: "#171A20"
            border.width: 1
            border.color: "#2A2E37"
        }
    }
}
