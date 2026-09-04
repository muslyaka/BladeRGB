import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components"

Item {
    id: root
    property string selectedId: ""
    property var selectedLayer: null

    function indexOfValue(items, value) {
        for (var i = 0; i < items.length; ++i) {
            if (items[i].value === value)
                return i
        }
        return 0
    }

    function refreshSelected() {
        if (!selectedId) {
            selectedLayer = null
            return
        }
        var list = controller.layers
        for (var i = 0; i < list.length; ++i) {
            if (list[i].id === selectedId) {
                selectedLayer = list[i]
                return
            }
        }
        selectedLayer = null
        selectedId = ""
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            PageHeader {
                Layout.fillWidth: true
                title: "Слои"
                subtitle: "Собирайте подсветку из нескольких эффектов и масок"
            }

            AppButton {
                text: "+ Эффект"
                compact: true
                onClicked: controller.addLayer("Effect")
            }

            AppButton {
                text: "+ Цвет"
                compact: true
                onClicked: controller.addLayer("Static")
            }

            AppButton {
                text: "+ Аудио"
                compact: true
                onClicked: controller.addLayer("Audio")
            }

            AppButton {
                text: "+ Нажатия"
                compact: true
                onClicked: controller.addLayer("Reactive")
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14

            Panel {
                Layout.preferredWidth: Math.max(430, root.width * 0.56)
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 9

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: "Стек слоёв"
                            color: "#E4E6EC"
                            font.pixelSize: 13
                            font.weight: Font.DemiBold
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: "снизу → вверх"
                            color: "#6F7582"
                            font.pixelSize: 9
                        }
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 7
                        clip: true
                        model: controller.layers

                        delegate: Rectangle {
                            required property var modelData
                            width: ListView.view.width
                            height: 70
                            radius: 10
                            color: root.selectedId === modelData.id ? "#22252E" : "#1B1E25"
                            border.width: 1
                            border.color: root.selectedId === modelData.id ? "#57538B" : "#282C35"

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    root.selectedId = modelData.id
                                    root.selectedLayer = modelData
                                }
                            }

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 9
                                spacing: 9

                                CalmSwitch {
                                    checked: modelData.enabled
                                    onToggled: controller.setLayerField(modelData.id, "enabled", checked)
                                }

                                Column {
                                    Layout.fillWidth: true
                                    spacing: 3

                                    Text {
                                        text: modelData.name
                                        color: "#E8E9EE"
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        elide: Text.ElideRight
                                    }

                                    Text {
                                        text: controller.uiLabel("layer_type", modelData.type)
                                            + " · "
                                            + controller.uiLabel(
                                                modelData.type === "Effect"
                                                    ? "effect"
                                                    : modelData.type === "Audio"
                                                        ? "audio"
                                                        : modelData.type === "Reactive"
                                                            ? "reactive"
                                                            : "effect",
                                                modelData.source
                                            )
                                            + " · "
                                            + controller.uiLabel("blend", modelData.blend_mode)
                                        color: "#747A87"
                                        font.pixelSize: 9
                                        elide: Text.ElideRight
                                    }
                                }

                                Text {
                                    text: Math.round(modelData.opacity * 100) + "%"
                                    color: "#9B9FAC"
                                    font.pixelSize: 9
                                    font.weight: Font.DemiBold
                                }

                                AppButton {
                                    text: "↑"
                                    compact: true
                                    onClicked: controller.moveLayer(modelData.id, -1)
                                }

                                AppButton {
                                    text: "↓"
                                    compact: true
                                    onClicked: controller.moveLayer(modelData.id, 1)
                                }

                                AppButton {
                                    text: "×"
                                    danger: true
                                    compact: true
                                    onClicked: controller.removeLayer(modelData.id)
                                }
                            }
                        }
                    }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 14
                    clip: true

                    ColumnLayout {
                        width: parent.width
                        spacing: 10

                        Text {
                            text: root.selectedLayer ? "Параметры слоя" : "Выберите слой"
                            color: "#E4E6EC"
                            font.pixelSize: 14
                            font.weight: Font.DemiBold
                        }

                        Text {
                            visible: !root.selectedLayer
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            text: "Нажмите на слой слева, чтобы изменить его источник, наложение, маску и параметры движения."
                            color: "#777D8A"
                            font.pixelSize: 10
                            lineHeight: 1.35
                        }

                        ColumnLayout {
                            visible: root.selectedLayer !== null
                            Layout.fillWidth: true
                            spacing: 9

                            SectionLabel { text: "Название" }

                            CalmTextField {
                                Layout.fillWidth: true
                                text: root.selectedLayer ? root.selectedLayer.name : ""
                                placeholderText: "Название слоя"
                                onEditingFinished: controller.setLayerField(root.selectedId, "name", text)
                            }

                            SectionLabel { text: "Источник" }

                            CalmComboBox {
                                id: sourceBox
                                Layout.fillWidth: true
                                model: !root.selectedLayer
                                    ? []
                                    : root.selectedLayer.type === "Effect"
                                        ? controller.effectItems
                                        : root.selectedLayer.type === "Audio"
                                            ? controller.audioItems
                                            : root.selectedLayer.type === "Reactive"
                                                ? controller.reactiveItems
                                                : [{"value":"Static", "label":"Статичный цвет"}]
                                textRole: "label"
                                currentIndex: root.selectedLayer
                                    ? root.indexOfValue(model, root.selectedLayer.source)
                                    : 0
                                onActivated: controller.setLayerField(root.selectedId, "source", model[currentIndex].value)
                            }

                            SectionLabel { text: "Режим наложения" }

                            CalmComboBox {
                                Layout.fillWidth: true
                                model: controller.blendItems
                                textRole: "label"
                                currentIndex: root.selectedLayer
                                    ? root.indexOfValue(controller.blendItems, root.selectedLayer.blend_mode)
                                    : 0
                                onActivated: controller.setLayerField(root.selectedId, "blend_mode", controller.blendItems[currentIndex].value)
                            }

                            SectionLabel { text: "Маска клавиш" }

                            CalmComboBox {
                                Layout.fillWidth: true
                                model: controller.maskItems
                                textRole: "label"
                                currentIndex: root.selectedLayer
                                    ? root.indexOfValue(controller.maskItems, root.selectedLayer.mask)
                                    : 0
                                onActivated: controller.setLayerField(root.selectedId, "mask", controller.maskItems[currentIndex].value)
                            }

                            MetricSlider {
                                Layout.fillWidth: true
                                label: "Прозрачность"
                                from: 0
                                to: 1
                                stepSize: 0.01
                                value: root.selectedLayer ? root.selectedLayer.opacity : 1
                                onChanged: controller.setLayerField(root.selectedId, "opacity", value)
                            }

                            MetricSlider {
                                Layout.fillWidth: true
                                label: "Скорость"
                                from: 0.05
                                to: 3
                                stepSize: 0.05
                                value: root.selectedLayer ? (root.selectedLayer.params.speed || 1) : 1
                                onChanged: controller.setLayerField(root.selectedId, "speed", value)
                            }

                            MetricSlider {
                                Layout.fillWidth: true
                                label: "Масштаб"
                                from: 0.2
                                to: 4
                                stepSize: 0.05
                                value: root.selectedLayer ? (root.selectedLayer.params.scale || 1) : 1
                                onChanged: controller.setLayerField(root.selectedId, "scale", value)
                            }

                            MetricSlider {
                                Layout.fillWidth: true
                                label: "Направление"
                                from: 0
                                to: 360
                                stepSize: 1
                                decimals: 0
                                suffix: "°"
                                value: root.selectedLayer ? (root.selectedLayer.params.angle || 0) : 0
                                onChanged: controller.setLayerField(root.selectedId, "angle", value)
                            }

                            AppButton {
                                Layout.fillWidth: true
                                text: "Выбрать цвет слоя"
                                onClicked: layerColorDialog.open()
                            }

                            ColorDialog {
                                id: layerColorDialog
                                title: "Цвет слоя"
                                onAccepted: controller.setLayerField(root.selectedId, "color", selectedColor.toString())
                            }
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: controller
        function onLayersChanged() {
            root.refreshSelected()
        }
    }
}
