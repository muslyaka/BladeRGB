import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components"

Flickable {
    id: root
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
            spacing: 12

            PageHeader {
                Layout.fillWidth: true
                title: "Обзор подсветки"
                subtitle: "Управление подсветкой клавиатуры в реальном времени"
            }

            StatusPill {
                online: controller.connected
                label: controller.statusText
            }

            AppButton {
                accent: true
                text: !controller.connected
                    ? "Подключить"
                    : controller.running
                        ? "Остановить"
                        : "Запустить"

                onClicked: {
                    if (!controller.connected)
                        controller.connectDevice()
                    else
                        controller.toggleEngine()
                }
            }
        }

        Panel {
            Layout.fillWidth: true
            Layout.preferredHeight: 385

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true

                    Column {
                        spacing: 2

                        Text {
                            text: "Клавиатура"
                            color: "#E8E9EE"
                            font.pixelSize: 14
                            font.weight: Font.DemiBold
                        }

                        Text {
                            text: "Живой предпросмотр текущего RGB-кадра"
                            color: "#777D8A"
                            font.pixelSize: 9
                        }
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: controller.actualFps.toFixed(1) + " кад/с"
                        color: "#A5A1D9"
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                    }
                }

                KeyboardView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Text {
                        text: "0416:C345"
                        color: "#616774"
                        font.pixelSize: 8
                    }

                    Text {
                        text: "MI_02"
                        color: "#616774"
                        font.pixelSize: 8
                    }

                    Text {
                        text: "FF1B:0091"
                        color: "#616774"
                        font.pixelSize: 8
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: "104 клавиши · поклавишная RGB-подсветка"
                        color: "#616774"
                        font.pixelSize: 8
                    }
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
                Layout.preferredHeight: 305

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    Text {
                        text: "Основная подсветка"
                        color: "#E4E6EC"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                    }

                    SectionLabel { text: "Эффект" }

                    CalmComboBox {
                        id: effectBox
                        Layout.fillWidth: true
                        model: controller.effectItems
                        textRole: "label"
                        currentIndex: root.indexOfValue(controller.effectItems, controller.effectName)

                        onActivated: {
                            controller.setEffect(controller.effectItems[currentIndex].value)
                        }
                    }

                    SectionLabel { text: "Палитра" }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Repeater {
                            model: controller.palette

                            delegate: Rectangle {
                                required property string modelData
                                required property int index
                                Layout.fillWidth: true
                                height: 38
                                radius: 9
                                color: modelData
                                border.width: 1
                                border.color: "#3B3F48"

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: paletteDialog.open()
                                }

                                ColorDialog {
                                    id: paletteDialog
                                    title: "Цвет палитры"
                                    selectedColor: modelData
                                    onAccepted: controller.setPaletteColor(index, selectedColor.toString())
                                }
                            }
                        }
                    }

                    SectionLabel { text: "Готовая сцена" }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        CalmComboBox {
                            id: presetBox
                            Layout.fillWidth: true
                            model: controller.presetItems
                            textRole: "label"
                        }

                        AppButton {
                            text: "Применить"
                            accent: true
                            onClicked: {
                                if (presetBox.currentIndex >= 0)
                                    controller.applyPreset(controller.presetItems[presetBox.currentIndex].value)
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 305

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 5

                    Text {
                        text: "Движение и яркость"
                        color: "#E4E6EC"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Скорость"
                        from: 0.05
                        to: 3
                        stepSize: 0.05
                        value: controller.params.speed || 1
                        onChanged: controller.setParam("speed", value)
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Масштаб"
                        from: 0.2
                        to: 4
                        stepSize: 0.05
                        value: controller.params.scale || 1
                        onChanged: controller.setParam("scale", value)
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Яркость"
                        from: 0
                        to: 1
                        stepSize: 0.01
                        value: controller.params.brightness || 0.72
                        onChanged: controller.setParam("brightness", value)
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Направление"
                        from: 0
                        to: 360
                        stepSize: 1
                        decimals: 0
                        suffix: "°"
                        value: controller.params.angle || 0
                        onChanged: controller.setParam("angle", value)
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Частота обновления"
                        from: 15
                        to: 60
                        stepSize: 1
                        decimals: 0
                        suffix: " кад/с"
                        value: controller.params.fps || 30
                        onChanged: controller.setParam("fps", value)
                    }
                }
            }
        }
    }
}
