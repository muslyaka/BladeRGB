import QtQuick

Item {
    id: root
    property bool interactive: false
    property string tool: "Select"
    property string paintColor: "#C77DFF"
    property var selectedKeys: ({})
    signal selectionChanged(var keys)

    readonly property real logicalWidth: 23.0
    readonly property real logicalHeight: 6.35

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
        color: Theme.keyBackground
        border.width: 1
        border.color: Theme.border

        Item {
            id: viewport
            anchors.fill: parent
            anchors.margins: 18

            readonly property real scaleFactor: Math.min(
                width / root.logicalWidth,
                height / root.logicalHeight
            )

            readonly property real boardWidth:
                root.logicalWidth * scaleFactor
            readonly property real boardHeight:
                root.logicalHeight * scaleFactor

            Item {
                id: keys
                width: viewport.boardWidth
                height: viewport.boardHeight
                anchors.centerIn: parent

                Repeater {
                    model: controller.keyboardLayout

                    delegate: Rectangle {
                        required property var modelData
                        property string keyName: modelData.name
                        property bool selected:
                            root.selectedKeys[keyName] === true
                        property bool painted:
                            controller.paintedColors[keyName] !== undefined

                        readonly property real unit:
                            viewport.scaleFactor
                        readonly property real gap:
                            Math.max(2.0, Math.min(4.0, unit * 0.10))

                        x: Number(modelData.x) * unit
                        y: Number(modelData.y) * unit
                        width: Math.max(
                            6,
                            Number(modelData.w) * unit - gap
                        )
                        height: Math.max(
                            6,
                            Number(modelData.h) * unit - gap
                        )
                        radius: Math.max(
                            4,
                            Math.min(8, height * 0.16)
                        )
                        color: controller.frameColors[keyName] || Theme.panelAlt
                        border.width: selected ? 2 : 1
                        border.color: selected
                            ? Theme.accentLight
                            : Theme.borderStrong

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
                            width: 4
                            height: 4
                            radius: 2
                            color: Theme.text
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.margins: 4
                        }

                        Text {
                            anchors.centerIn: parent
                            text: root.pretty(keyName)
                            color: Theme.text
                            font.pixelSize: Math.max(
                                6,
                                Math.min(10, parent.height * 0.24)
                            )
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
                                    controller.paintKey(
                                        keyName,
                                        root.paintColor
                                    )
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
}
