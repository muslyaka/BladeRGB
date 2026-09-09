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
        for (var i = 0; i < items.length; ++i) if (items[i].value === value) return i
        return 0
    }

    ColumnLayout {
        id: body
        width: root.width
        spacing: 16

        PageHeader { title: "Настройки"; subtitle: "Оформление, поведение приложения и диагностика" }

        GridLayout {
            Layout.fillWidth: true
            columns: root.width >= 900 ? 2 : 1
            columnSpacing: 14
            rowSpacing: 14

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 265
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12
                    Text { text: "Оформление"; color: Theme.text; font.pixelSize: 14; font.weight: Font.DemiBold }
                    SectionLabel { text: "Тема приложения" }
                    CalmComboBox {
                        Layout.fillWidth: true
                        model: [{"value":"dark","label":"Тёмная"},{"value":"light","label":"Светлая"}]
                        textRole: "label"
                        currentIndex: root.indexOfValue(model, controller.theme)
                        onActivated: controller.setTheme(model[currentIndex].value)
                    }
                    SectionLabel { text: "Акцентный цвет" }
                    RowLayout {
                        Layout.fillWidth: true
                        Rectangle { width: 36; height: 32; radius: 9; color: controller.accentColor; border.width: 1; border.color: Theme.borderStrong }
                        Text { text: controller.accentColor.toUpperCase(); color: Theme.textSecondary; font.pixelSize: 10; font.weight: Font.DemiBold }
                        Item { Layout.fillWidth: true }
                        AppButton { text: "Изменить"; accent: true; compact: true; onClicked: accentPicker.openFor(controller.accentColor) }
                        RGBWPicker { id: accentPicker; onColorEdited: function(hex) { controller.setAccentColor(hex) } }
                    }
                    Text { Layout.fillWidth: true; wrapMode: Text.WordWrap; text: "Акцент применяется к кнопкам, переключателям, ползункам и активным пунктам меню сразу."; color: Theme.textMuted; font.pixelSize: 9; lineHeight: 1.35 }
                    Item { Layout.fillHeight: true }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 265
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 13
                    Text { text: "Поведение приложения"; color: Theme.text; font.pixelSize: 14; font.weight: Font.DemiBold }
                    RowLayout {
                        Layout.fillWidth: true
                        Column { Layout.fillWidth: true; spacing: 2; Text { text: "Сворачивать в трей при закрытии"; color: Theme.textSecondary; font.pixelSize: 11 }
Text { text: "Подсветка продолжает работать"; color: Theme.textMuted; font.pixelSize: 9 } }
                        CalmSwitch { checked: controller.closeToTray; onToggled: controller.setCloseToTray(checked) }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Column { Layout.fillWidth: true; spacing: 2; Text { text: "Запускать вместе с Windows"; color: Theme.textSecondary; font.pixelSize: 11 }
Text { text: "Стартует скрыто в трее"; color: Theme.textMuted; font.pixelSize: 9 } }
                        CalmSwitch { checked: controller.autostartEnabled; onToggled: controller.setAutostart(checked) }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Column { Layout.fillWidth: true; spacing: 2; Text { text: "Глобальные горячие клавиши"; color: Theme.textSecondary; font.pixelSize: 11 }
Text { text: "Работают при скрытом окне"; color: Theme.textMuted; font.pixelSize: 9 } }
                        CalmSwitch { checked: controller.hotkeysEnabled; onToggled: controller.setHotkeysEnabled(checked) }
                    }
                    Text { text: "Ctrl+Alt+F9/F10 — RGB · Ctrl+Alt+F11/F12 — профили"; color: Theme.textSubtle; font.pixelSize: 9 }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 225
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10
                    Text { text: "Переключение сцен"; color: Theme.text; font.pixelSize: 14; font.weight: Font.DemiBold }
                    MetricSlider { Layout.fillWidth: true; label: "Плавный переход"; from: 0; to: 2500; stepSize: 50; decimals: 0; suffix: " мс"; value: controller.transitionMs; onChanged: controller.setTransitionMs(Math.round(value)) }
                    Text { Layout.fillWidth: true; wrapMode: Text.WordWrap; text: "При смене профиля BladeRGB плавно смешивает предыдущий и новый RGB-кадр."; color: Theme.textMuted; font.pixelSize: 10; lineHeight: 1.4 }
                    Item { Layout.fillHeight: true }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 225
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 9
                    Text { text: "Клавиатура и диагностика"; color: Theme.text; font.pixelSize: 14; font.weight: Font.DemiBold }
                    Text { text: "ARDOR GAMING BLADE · 0416:C345 · MI_02"; color: Theme.textSecondary; font.pixelSize: 10 }
                    Text { text: controller.running ? "Подсветка работает · " + controller.actualFps.toFixed(1) + " кад/с" : "Подсветка остановлена"; color: controller.running ? Theme.success : Theme.textMuted; font.pixelSize: 10; font.weight: Font.DemiBold }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 9
                        color: Theme.input
                        border.width: 1
                        border.color: Theme.border
                        Text { anchors.fill: parent; anchors.margins: 10; text: controller.lastError !== "" ? controller.lastError : "Ошибок нет."; color: controller.lastError !== "" ? Theme.danger : Theme.success; font.family: "Consolas"; font.pixelSize: 9; wrapMode: Text.WrapAnywhere }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        AppButton { Layout.fillWidth: true; text: "Переподключить"; onClicked: controller.connectDevice() }
                        AppButton { Layout.fillWidth: true; text: "Погасить"; danger: true; onClicked: controller.blackout() }
                    }
                }
            }
        }
    }
}
