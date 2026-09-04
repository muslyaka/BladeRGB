import QtQuick

Item {
    id: root
    property bool interactive: false
    property string tool: "Select"
    property string paintColor: "#C77DFF"
    property var selectedKeys: ({})
    signal selectionChanged(var keys)

    function pretty(n) {
        var a = {
            "BACKSPACE":"BKSP",
            "LSHIFT":"SHIFT",
            "RSHIFT":"SHIFT",
            "LCTRL":"CTRL",
            "RCTRL":"CTRL",
            "LALT":"ALT",
            "RALT":"ALT",
            "NUMLOCK":"NUM",
            "NUM_DIV":"/",
            "NUM_MUL":"×",
            "NUM_MINUS":"−",
            "NUM_PLUS":"+",
            "NUM_ENTER":"ENT",
            "NUM_DOT":".",
            "PRINT":"MENU",
            "PGUP":"PG↑",
            "PGDN":"PG↓",
            "PAUSE":"PAU"
        }
        if (a[n] !== undefined)
            return a[n]
        if (n.indexOf("NUM") === 0 && n.length === 4)
            return n.substring(3)
        return n
    }

    Rectangle {
        anchors.fill: parent
        radius: 16
        color: "#101217"
        border.width: 1
        border.color: "#262A33"

        Item {
            id: keys
            anchors.fill: parent
            anchors.margins: 18

            Repeater {
                model: controller.keyboardLayout

                delegate: Rectangle {
                    required property var modelData
                    property string keyName: modelData.name
                    property bool selected: root.selectedKeys[keyName] === true
                    property bool painted: controller.paintedColors[keyName] !== undefined

                    x: Number(modelData.x) / 23.0 * keys.width
                    y: Number(modelData.y) / 6.35 * keys.height
                    width: Number(modelData.w) / 23.0 * keys.width - 3
                    height: Number(modelData.h) / 6.35 * keys.height - 3
                    radius: Math.max(4, Math.min(7, height * 0.15))
                    color: controller.frameColors[keyName] || "#171A20"
                    border.width: selected ? 2 : 1
                    border.color: selected ? "#DCD9F2" : "#343843"

                    Behavior on color {
                        ColorAnimation { duration: 80 }
                    }

                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        color: "#0BFFFFFF"
                    }

                    Rectangle {
                        visible: painted
                        width: 3
                        height: 3
                        radius: 2
                        color: "#EDEEF3"
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 4
                    }

                    Text {
                        anchors.centerIn: parent
                        text: root.pretty(keyName)
                        color: "#E8E9EE"
                        font.pixelSize: Math.max(6, Math.min(10, parent.height * 0.22))
                        font.weight: Font.Medium
                    }

                    MouseArea {
                        anchors.fill: parent
                        enabled: root.interactive
                        hoverEnabled: true
                        cursorShape: root.tool === "Brush"
                            ? Qt.CrossCursor
                            : root.tool === "Eraser"
                                ? Qt.ForbiddenCursor
                                : Qt.PointingHandCursor

                        onClicked: {
                            if (root.tool === "Brush") {
                                controller.paintKey(keyName, root.paintColor)
                            } else if (root.tool === "Eraser") {
                                controller.eraseKey(keyName)
                            } else {
                                var next = {}
                                for (var k in root.selectedKeys)
                                    next[k] = root.selectedKeys[k]
                                if (next[keyName] === true)
                                    delete next[keyName]
                                else
                                    next[keyName] = true
                                root.selectedKeys = next
                                root.selectionChanged(next)
                            }
                        }
                    }
                }
            }
        }
    }
}
