import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components"

Flickable {
    id: root
    property string tool: "Brush"
    property string brush: "#C77DFF"
    property var selected: ({})

    contentWidth: width
    contentHeight: body.implicitHeight + 24
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    function indexOfValue(items, value) {
        for (var i = 0; i < items.length; ++i) {
            if (items[i].value === value)
                return i
        }
        return 0
    }

    ColumnLayout {
        id: body
        width: root.width
        spacing: 16

        RowLayout {
            Layout.fillWidth: true

            PageHeader {
                Layout.fillWidth: true
                title: "Покраска клавиш"
                subtitle: "Назначайте любой цвет отдельным клавишам или группам"
            }

            StatusPill {
                online: controller.paintedCount > 0
                label: "Раскрашено: " + controller.paintedCount
            }
        }

        Panel {
            Layout.fillWidth: true
            Layout.preferredHeight: 62

            RowLayout {
                anchors.fill: parent
                anchors.margins: 11
                spacing: 7

                AppButton {
                    text: "Кисть"
                    accent: root.tool === "Brush"
                    compact: true
                    onClicked: root.tool = "Brush"
                }

                AppButton {
                    text: "Ластик"
                    accent: root.tool === "Eraser"
                    compact: true
                    onClicked: root.tool = "Eraser"
                }

                AppButton {
                    text: "Выбор"
                    accent: root.tool === "Select"
                    compact: true
                    onClicked: root.tool = "Select"
                }

                Rectangle {
                    width: 1
                    height: 26
                    color: "#2C3039"
                    Layout.leftMargin: 4
                    Layout.rightMargin: 4
                }

                Rectangle {
                    width: 32
                    height: 32
                    radius: 8
                    color: root.brush
                    border.width: 1
                    border.color: "#484C56"

                    MouseArea {
                        anchors.fill: parent
                        onClicked: brushDialog.open()
                    }

                    ColorDialog {
                        id: brushDialog
                        title: "Цвет кисти"
                        selectedColor: root.brush
                        onAccepted: root.brush = selectedColor.toString()
                    }
                }

                Text {
                    text: root.brush.toUpperCase()
                    color: "#BFC2CB"
                    font.pixelSize: 10
                    font.weight: Font.DemiBold
                }

                Item { Layout.fillWidth: true }

                AppButton {
                    text: "WASD"
                    compact: true
                    onClicked: controller.paintGroup("WASD", root.brush)
                }

                AppButton {
                    text: "Стрелки"
                    compact: true
                    onClicked: controller.paintGroup("Arrows", root.brush)
                }

                AppButton {
                    text: "Цифровой блок"
                    compact: true
                    onClicked: controller.paintGroup("Numpad", root.brush)
                }

                AppButton {
                    text: "Очистить"
                    danger: true
                    compact: true
                    onClicked: controller.clearPaint()
                }
            }
        }

        Panel {
            Layout.fillWidth: true
            Layout.preferredHeight: 385

            KeyboardView {
                anchors.fill: parent
                anchors.margins: 18
                interactive: true
                tool: root.tool
                paintColor: root.brush
                selectedKeys: root.selected
                onSelectionChanged: function(keys) {
                    root.selected = keys
                }
            }
        }

        GridLayout {
            Layout.fillWidth: true
            columns: root.width >= 900 ? 2 : 1
            columnSpacing: 14
            rowSpacing: 14

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 275

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 9

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: "Реакция на нажатия"
                            color: "#E4E6EC"
                            font.pixelSize: 14
                            font.weight: Font.DemiBold
                        }

                        Item { Layout.fillWidth: true }

                        CalmSwitch {
                            checked: controller.reactiveEnabled
                            onToggled: controller.setReactiveEnabled(checked)
                        }
                    }

                    SectionLabel { text: "Режим" }

                    CalmComboBox {
                        Layout.fillWidth: true
                        model: controller.reactiveItems
                        textRole: "label"
                        currentIndex: root.indexOfValue(controller.reactiveItems, controller.reactiveMode)
                        onActivated: controller.setReactiveMode(controller.reactiveItems[currentIndex].value)
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        SectionLabel { text: "Цвет реакции" }
                        Item { Layout.fillWidth: true }

                        Rectangle {
                            width: 32
                            height: 28
                            radius: 8
                            color: controller.reactiveColor
                            border.width: 1
                            border.color: "#40444D"

                            MouseArea {
                                anchors.fill: parent
                                onClicked: reactiveDialog.open()
                            }

                            ColorDialog {
                                id: reactiveDialog
                                title: "Цвет реакции"
                                selectedColor: controller.reactiveColor
                                onAccepted: controller.setReactiveColor(selectedColor.toString())
                            }
                        }
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Интенсивность"
                        from: 0
                        to: 1
                        stepSize: 0.01
                        value: controller.params.reactive_strength || 0.9
                        onChanged: controller.setParam("reactive_strength", value)
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Затухание"
                        from: 0.15
                        to: 2
                        stepSize: 0.01
                        suffix: " с"
                        value: controller.params.reactive_decay || 0.85
                        onChanged: controller.setParam("reactive_decay", value)
                    }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 275

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 9

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: "Реакция на звук"
                            color: "#E4E6EC"
                            font.pixelSize: 14
                            font.weight: Font.DemiBold
                        }

                        Item { Layout.fillWidth: true }

                        CalmSwitch {
                            checked: controller.audioEnabled
                            onToggled: controller.setAudioEnabled(checked)
                        }
                    }

                    SectionLabel { text: "Режим" }

                    CalmComboBox {
                        Layout.fillWidth: true
                        model: controller.audioItems
                        textRole: "label"
                        currentIndex: root.indexOfValue(controller.audioItems, controller.audioMode)
                        onActivated: controller.setAudioMode(controller.audioItems[currentIndex].value)
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Чувствительность"
                        from: 0.1
                        to: 4
                        stepSize: 0.05
                        value: controller.params.audio_gain || 1.25
                        onChanged: controller.setParam("audio_gain", value)
                    }

                    Text {
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        text: "Подсветка реагирует на системный звук Windows через WASAPI."
                        color: "#777D8A"
                        font.pixelSize: 10
                        lineHeight: 1.35
                    }

                    Item { Layout.fillHeight: true }
                }
            }
        }
    }
}
