import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: root
    property var anim: controller.animation

    function indexOfValue(items, value) {
        for (var i = 0; i < items.length; ++i) {
            if (items[i].value === value)
                return i
        }
        return 0
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        RowLayout {
            Layout.fillWidth: true

            PageHeader {
                Layout.fillWidth: true
                title: "Анимация"
                subtitle: "Ключевые кадры для скорости, яркости, направления и палитры"
            }

            Row {
                spacing: 8

                Text {
                    text: "Включена"
                    color: "#8F95A3"
                    font.pixelSize: 10
                    anchors.verticalCenter: parent.verticalCenter
                }

                CalmSwitch {
                    checked: root.anim.enabled || false
                    onToggled: controller.setAnimatorEnabled(checked)
                }
            }
        }

        Panel {
            Layout.fillWidth: true
            Layout.preferredHeight: 165

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 15
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true

                    Column {
                        spacing: 2

                        Text {
                            text: "Шкала времени"
                            color: "#E4E6EC"
                            font.pixelSize: 13
                            font.weight: Font.DemiBold
                        }

                        Text {
                            text: (root.anim.keyframes || []).length + " ключевых кадров"
                            color: "#747A87"
                            font.pixelSize: 9
                        }
                    }

                    Item { Layout.fillWidth: true }

                    AppButton {
                        text: "Сначала"
                        compact: true
                        onClicked: controller.restartAnimator()
                    }

                    AppButton {
                        text: "+ Записать текущие"
                        accent: true
                        compact: true
                        onClicked: controller.captureKeyframe()
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Rectangle {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        height: 4
                        radius: 2
                        color: "#2B2F38"
                    }

                    Repeater {
                        model: root.anim.keyframes || []

                        delegate: Rectangle {
                            required property var modelData
                            required property int index
                            width: 16
                            height: 16
                            radius: 8
                            color: modelData.palette && modelData.palette.length
                                ? modelData.palette[0]
                                : "#7772C9"
                            border.width: 2
                            border.color: "#E7E5F2"
                            x: (Number(modelData.time) / Math.max(0.5, Number(root.anim.duration || 8))) * (parent.width - width)
                            anchors.verticalCenter: parent.verticalCenter

                            MouseArea {
                                anchors.fill: parent
                                onDoubleClicked: controller.deleteKeyframe(index)
                            }
                        }
                    }

                    Rectangle {
                        width: 2
                        height: parent.height - 8
                        radius: 1
                        color: "#A69FDF"
                        x: (Number(root.anim.playhead || 0) / Math.max(0.5, Number(root.anim.duration || 8))) * (parent.width - width)
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }
        }

        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: root.width >= 850 ? 2 : 1
            columnSpacing: 14
            rowSpacing: 14

            Panel {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 10

                    Text {
                        text: "Воспроизведение"
                        color: "#E4E6EC"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Длительность"
                        from: 0.5
                        to: 60
                        stepSize: 0.5
                        decimals: 1
                        suffix: " с"
                        value: root.anim.duration || 8
                        onChanged: controller.setAnimatorDuration(value)
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: "Зациклить"
                            color: "#A2A7B3"
                            font.pixelSize: 11
                        }

                        Item { Layout.fillWidth: true }

                        CalmSwitch {
                            checked: root.anim.loop === undefined ? true : root.anim.loop
                            onToggled: controller.setAnimatorLoop(checked)
                        }
                    }

                    SectionLabel { text: "Плавность" }

                    CalmComboBox {
                        Layout.fillWidth: true
                        model: controller.easingItems
                        textRole: "label"
                        currentIndex: root.indexOfValue(controller.easingItems, root.anim.easing || "Smoothstep")
                        onActivated: controller.setAnimatorEasing(controller.easingItems[currentIndex].value)
                    }

                    Text {
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        text: "Кнопка «Записать текущие» сохраняет скорость, масштаб, яркость, направление и палитру в текущей позиции. Двойной клик по точке удаляет кадр."
                        color: "#777D8A"
                        font.pixelSize: 10
                        lineHeight: 1.4
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 9

                    Text {
                        text: "Ключевые кадры"
                        color: "#E4E6EC"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 6
                        clip: true
                        model: root.anim.keyframes || []

                        delegate: Rectangle {
                            required property var modelData
                            required property int index
                            width: ListView.view.width
                            height: 56
                            radius: 10
                            color: "#1B1E25"
                            border.width: 1
                            border.color: "#282C35"

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 9

                                Rectangle {
                                    width: 26
                                    height: 26
                                    radius: 7
                                    color: modelData.palette && modelData.palette.length
                                        ? modelData.palette[0]
                                        : "#7772C9"
                                }

                                Column {
                                    Layout.fillWidth: true
                                    spacing: 2

                                    Text {
                                        text: "Кадр " + (index + 1)
                                        color: "#E8E9EE"
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                    }

                                    Text {
                                        text: Number(modelData.time).toFixed(2) + " с · скорость " + Number(modelData.speed).toFixed(2)
                                        color: "#747A87"
                                        font.pixelSize: 9
                                    }
                                }

                                AppButton {
                                    text: "Удалить"
                                    danger: true
                                    compact: true
                                    onClicked: controller.deleteKeyframe(index)
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: controller
        function onAnimatorChanged() {
            root.anim = controller.animation
        }
    }
}
