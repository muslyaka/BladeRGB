import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Flickable {
    id: root
    contentWidth: width
    contentHeight: body.implicitHeight + 24
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    function indexOfValue(items, value) {
        for (var i = 0; i < items.length; ++i)
            if (items[i].value === value) return i
        return 0
    }

    ColumnLayout {
        id: body
        width: root.width
        spacing: 14

        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            PageHeader {
                Layout.fillWidth: true
                title: "Обзор подсветки"
                subtitle: "Клавиатура и ключевые параметры — на одном экране"
            }
            StatusPill { online: controller.connected; label: controller.statusText }
            AppButton {
                accent: true
                text: !controller.connected ? "Подключить" : controller.running ? "Остановить" : "Запустить"
                onClicked: { if (!controller.connected) controller.connectDevice(); else controller.toggleEngine() }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 14

            Panel {
                Layout.fillWidth: true
                Layout.preferredWidth: 760
                Layout.preferredHeight: 305
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 8
                    RowLayout {
                        Layout.fillWidth: true
                        Column {
                            spacing: 2
                            Text { text: "Клавиатура"; color: Theme.text; font.pixelSize: 13; font.weight: Font.DemiBold }
                            Text { text: "Живой RGB-кадр"; color: Theme.textMuted; font.pixelSize: 9 }
                        }
                        Item { Layout.fillWidth: true }
                        Text { text: controller.actualFps.toFixed(1) + " кад/с"; color: Theme.accentLight; font.pixelSize: 10; font.weight: Font.DemiBold }
                    }
                    KeyboardView { Layout.fillWidth: true; Layout.fillHeight: true }
                }
            }

            Panel {
                Layout.preferredWidth: 330
                Layout.preferredHeight: 305
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 2
                    Text { text: "Основные параметры"; color: Theme.text; font.pixelSize: 13; font.weight: Font.DemiBold }
                    MetricSlider { Layout.fillWidth: true; label: "Скорость"; from: 0.05; to: 3; stepSize: 0.05; value: controller.params.speed || 1; onChanged: controller.setParam("speed", value) }
                    MetricSlider { Layout.fillWidth: true; label: "Масштаб"; from: 0.2; to: 4; stepSize: 0.05; value: controller.params.scale || 1; onChanged: controller.setParam("scale", value) }
                    MetricSlider { Layout.fillWidth: true; label: "Яркость"; from: 0; to: 1; stepSize: 0.01; value: controller.params.brightness === undefined ? 0.72 : controller.params.brightness; onChanged: controller.setParam("brightness", value) }
                    MetricSlider { Layout.fillWidth: true; label: "Направление"; from: 0; to: 360; stepSize: 1; decimals: 0; suffix: "°"; value: controller.params.angle || 0; onChanged: controller.setParam("angle", value) }
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
                Layout.preferredHeight: 365
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 8
                    Text { text: "Основная подсветка"; color: Theme.text; font.pixelSize: 13; font.weight: Font.DemiBold }
                    SectionLabel { text: "Эффект" }
                    CalmComboBox {
                        Layout.fillWidth: true
                        model: controller.effectItems
                        textRole: "label"
                        currentIndex: root.indexOfValue(controller.effectItems, controller.effectName)
                        onActivated: controller.setEffect(controller.effectItems[currentIndex].value)
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        SectionLabel { text: "Палитра · 8 цветов" }
                        Item { Layout.fillWidth: true }
                        Text { text: "цвет меняется сразу"; color: Theme.textSubtle; font.pixelSize: 8 }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        Repeater {
                            model: controller.palette
                            delegate: Rectangle {
                                required property string modelData
                                required property int index
                                Layout.fillWidth: true
                                Layout.minimumWidth: 28
                                height: 34
                                radius: 8
                                color: modelData
                                border.width: 1
                                border.color: Theme.borderStrong
                                MouseArea { anchors.fill: parent; onClicked: picker.openFor(modelData) }
                                RGBWPicker {
                                    id: picker
                                    onColorEdited: function(hex) { controller.setPaletteColor(index, hex) }
                                }
                            }
                        }
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Задержка между цветами"
                        from: 0
                        to: 8
                        stepSize: 0.1
                        decimals: 1
                        suffix: " с"
                        value: controller.params.palette_delay || 0
                        onChanged: controller.setParam("palette_delay", value)
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        CalmComboBox { id: palettePresetBox; Layout.fillWidth: true; model: controller.palettePresetItems; textRole: "label" }
                        AppButton {
                            text: "Гамма"
                            compact: true
                            onClicked: if (palettePresetBox.currentIndex >= 0) controller.applyPalettePreset(controller.palettePresetItems[palettePresetBox.currentIndex].value)
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        CalmComboBox { id: presetBox; Layout.fillWidth: true; model: controller.presetItems; textRole: "label" }
                        AppButton {
                            text: "Сцена"
                            accent: true
                            compact: true
                            onClicked: if (presetBox.currentIndex >= 0) controller.applyPreset(controller.presetItems[presetBox.currentIndex].value)
                        }
                    }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 365
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 8
                    RowLayout {
                        Layout.fillWidth: true
                        Column {
                            spacing: 2
                            Text { text: "Тонкая настройка эффекта"; color: Theme.text; font.pixelSize: 13; font.weight: Font.DemiBold }
                            Text { text: controller.effectParameterItems.length > 0 ? "Индивидуальные параметры выбранного эффекта" : "Дополнительных параметров нет"; color: Theme.textMuted; font.pixelSize: 9 }
                        }
                        Item { Layout.fillWidth: true }
                        AppButton { visible: controller.effectParameterItems.length > 0; text: "Сбросить"; compact: true; onClicked: controller.resetEffectParameters() }
                    }
                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 1
                        rowSpacing: 2
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
                                value: controller.params[modelData.key] === undefined ? modelData.default : controller.params[modelData.key]
                                onChanged: controller.setParam(modelData.key, value)
                            }
                        }
                    }
                    Item { visible: controller.effectParameterItems.length === 0; Layout.fillHeight: true }
                }
            }
        }
    }
}
