import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Flickable {
    id: root
    contentWidth: width
    contentHeight: body.implicitHeight + 30
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    readonly property bool wide: width >= 1080
    readonly property real contentMaxWidth: 1480

    function indexOfValue(items, value) {
        for (var i = 0; i < items.length; ++i) {
            if (items[i].value === value)
                return i
        }
        return 0
    }

    ColumnLayout {
        id: body
        width: Math.min(root.width, root.contentMaxWidth)
        x: Math.max(0, (root.width - width) / 2)
        spacing: 18

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            PageHeader {
                Layout.fillWidth: true
                title: "Обзор подсветки"
                subtitle: "Управление клавиатурой и эффектами в реальном времени"
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

        GridLayout {
            Layout.fillWidth: true
            columns: root.wide ? 2 : 1
            columnSpacing: 18
            rowSpacing: 18

            Panel {
                Layout.fillWidth: true
                Layout.minimumWidth: root.wide ? 650 : 0
                Layout.preferredWidth: root.wide ? 900 : -1
                Layout.preferredHeight: 372

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true

                        Column {
                            spacing: 3

                            Text {
                                text: "Клавиатура"
                                color: Theme.text
                                font.pixelSize: 14
                                font.weight: Font.DemiBold
                            }

                            Text {
                                text: "Живой предпросмотр текущего RGB-кадра"
                                color: Theme.textMuted
                                font.pixelSize: 9
                            }
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: controller.actualFps.toFixed(1) + " кад/с"
                            color: Theme.accentLight
                            font.pixelSize: 10
                            font.weight: Font.DemiBold
                        }
                    }

                    KeyboardView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        Text {
                            text: "ARDOR GAMING BLADE"
                            color: Theme.textSubtle
                            font.pixelSize: 8
                            font.weight: Font.DemiBold
                        }

                        Text {
                            text: "0416:C345 · MI_02"
                            color: Theme.textSubtle
                            font.pixelSize: 8
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: "104 клавиши · поклавишная RGB"
                            color: Theme.textSubtle
                            font.pixelSize: 8
                        }
                    }
                }
            }

            Panel {
                Layout.fillWidth: !root.wide
                Layout.preferredWidth: root.wide ? 355 : -1
                Layout.minimumWidth: root.wide ? 330 : 0
                Layout.maximumWidth: root.wide ? 390 : 16777215
                Layout.preferredHeight: 372

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 2

                    Text {
                        text: "Основные параметры"
                        color: Theme.text
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                        Layout.bottomMargin: 6
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
                        value: controller.params.brightness === undefined
                            ? 0.72
                            : controller.params.brightness
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
                        label: "FPS (лимит)"
                        from: 10
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

        GridLayout {
            Layout.fillWidth: true
            columns: root.wide ? 2 : 1
            columnSpacing: 18
            rowSpacing: 18

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 475

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 11

                    Column {
                        spacing: 3

                        Text {
                            text: "Основная подсветка"
                            color: Theme.text
                            font.pixelSize: 14
                            font.weight: Font.DemiBold
                        }

                        Text {
                            text: "Эффект, палитра и готовые цветовые сцены"
                            color: Theme.textMuted
                            font.pixelSize: 9
                        }
                    }

                    SectionLabel { text: "Эффект" }

                    CalmComboBox {
                        Layout.fillWidth: true
                        model: controller.effectItems
                        textRole: "label"
                        currentIndex: root.indexOfValue(
                            controller.effectItems,
                            controller.effectName
                        )
                        onActivated: controller.setEffect(
                            controller.effectItems[currentIndex].value
                        )
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        SectionLabel { text: "Палитра · 8 цветов" }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: "изменения применяются сразу"
                            color: Theme.textSubtle
                            font.pixelSize: 8
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Repeater {
                            model: controller.palette

                            delegate: Rectangle {
                                required property string modelData
                                required property int index

                                Layout.fillWidth: true
                                Layout.minimumWidth: 34
                                height: 42
                                radius: 10
                                color: modelData
                                border.width: 1
                                border.color: Theme.borderStrong

                                Rectangle {
                                    anchors.fill: parent
                                    anchors.margins: 1
                                    radius: 9
                                    color: "transparent"
                                    border.width: 1
                                    border.color: "#16FFFFFF"
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: picker.openFor(modelData)
                                }

                                RGBWPicker {
                                    id: picker
                                    onColorEdited: function(hex) {
                                        controller.setPaletteColor(index, hex)
                                    }
                                }
                            }
                        }
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Пауза на каждом цвете"
                        from: 0
                        to: 8
                        stepSize: 0.1
                        decimals: 1
                        suffix: " с"
                        value: controller.params.palette_delay || 0
                        onChanged: controller.setParam("palette_delay", value)
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Длительность перехода"
                        from: 0.1
                        to: 3
                        stepSize: 0.05
                        decimals: 2
                        suffix: " с"
                        value: controller.params.palette_transition === undefined
                            ? 0.6
                            : controller.params.palette_transition
                        onChanged: controller.setParam("palette_transition", value)
                    }

                    Text {
                        Layout.fillWidth: true
                        text: controller.params.palette_delay > 0
                            ? "Цикл: пауза → плавный переход → следующий цвет"
                            : "0 с — дополнительная задержка палитры отключена"
                        color: Theme.textSubtle
                        font.pixelSize: 8
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 9

                        CalmComboBox {
                            id: palettePresetBox
                            Layout.fillWidth: true
                            model: controller.palettePresetItems
                            textRole: "label"
                        }

                        AppButton {
                            text: "Применить гамму"
                            compact: true
                            onClicked: {
                                if (palettePresetBox.currentIndex >= 0) {
                                    controller.applyPalettePreset(
                                        controller.palettePresetItems[
                                            palettePresetBox.currentIndex
                                        ].value
                                    )
                                }
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 9

                        CalmComboBox {
                            id: presetBox
                            Layout.fillWidth: true
                            model: controller.presetItems
                            textRole: "label"
                        }

                        AppButton {
                            text: "Применить сцену"
                            accent: true
                            compact: true
                            onClicked: {
                                if (presetBox.currentIndex >= 0) {
                                    controller.applyPreset(
                                        controller.presetItems[
                                            presetBox.currentIndex
                                        ].value
                                    )
                                }
                            }
                        }
                    }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 475

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true

                        Column {
                            spacing: 3

                            Text {
                                text: "Тонкая настройка эффекта"
                                color: Theme.text
                                font.pixelSize: 14
                                font.weight: Font.DemiBold
                            }

                            Text {
                                text: controller.effectParameterItems.length > 0
                                    ? "Индивидуальные параметры выбранного эффекта"
                                    : "У выбранного эффекта нет дополнительных параметров"
                                color: Theme.textMuted
                                font.pixelSize: 9
                            }
                        }

                        Item { Layout.fillWidth: true }

                        AppButton {
                            visible: controller.effectParameterItems.length > 0
                            text: "Сбросить"
                            compact: true
                            onClicked: controller.resetEffectParameters()
                        }
                    }

                    GridLayout {
                        id: fineGrid
                        Layout.fillWidth: true
                        columns: width >= 590 ? 2 : 1
                        columnSpacing: 22
                        rowSpacing: 8
                        visible: controller.effectParameterItems.length > 0

                        Repeater {
                            model: controller.effectParameterItems

                            delegate: MetricSlider {
                                required property var modelData
                                Layout.fillWidth: true
                                label: modelData.label
                                from: modelData.min
                                to: modelData.max
                                stepSize: modelData.step
                                decimals: modelData.decimals
                                suffix: modelData.suffix
                                value: controller.params[modelData.key] === undefined
                                    ? modelData.default
                                    : controller.params[modelData.key]
                                onChanged: controller.setParam(
                                    modelData.key,
                                    value
                                )
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    Rectangle {
                        visible: controller.effectParameterItems.length === 0
                        Layout.fillWidth: true
                        Layout.preferredHeight: 110
                        radius: 12
                        color: Theme.panelAlt
                        border.width: 1
                        border.color: Theme.border

                        Column {
                            anchors.centerIn: parent
                            spacing: 5

                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "Дополнительных настроек нет"
                                color: Theme.textSecondary
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                            }

                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "Используйте основные параметры справа от клавиатуры"
                                color: Theme.textMuted
                                font.pixelSize: 9
                            }
                        }
                    }
                }
            }
        }
    }
}
