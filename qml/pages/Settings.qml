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

    ColumnLayout {
        id: body
        width: root.width
        spacing: 16

        PageHeader {
            title: "Настройки"
            subtitle: "Поведение приложения, автозапуск и диагностика"
        }

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
                    spacing: 13

                    Text {
                        text: "Поведение приложения"
                        color: "#E4E6EC"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        Column {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: "Сворачивать в трей при закрытии"
                                color: "#C4C7D0"
                                font.pixelSize: 11
                            }

                            Text {
                                text: "Крестик скрывает окно, подсветка продолжает работать"
                                color: "#707683"
                                font.pixelSize: 9
                            }
                        }

                        CalmSwitch {
                            checked: controller.closeToTray
                            onToggled: controller.setCloseToTray(checked)
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        Column {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: "Запускать вместе с Windows"
                                color: "#C4C7D0"
                                font.pixelSize: 11
                            }

                            Text {
                                text: "BladeRGB запускается скрыто в трее"
                                color: "#707683"
                                font.pixelSize: 9
                            }
                        }

                        CalmSwitch {
                            checked: controller.autostartEnabled
                            onToggled: controller.setAutostart(checked)
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        Column {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: "Глобальные горячие клавиши"
                                color: "#C4C7D0"
                                font.pixelSize: 11
                            }

                            Text {
                                text: "Работают даже когда окно BladeRGB скрыто"
                                color: "#707683"
                                font.pixelSize: 9
                            }
                        }

                        CalmSwitch {
                            checked: controller.hotkeysEnabled
                            onToggled: controller.setHotkeysEnabled(checked)
                        }
                    }

                    Text {
                        text: "Ctrl+Alt+F9 — запустить / остановить · Ctrl+Alt+F10 — погасить\nCtrl+Alt+F11/F12 — предыдущий / следующий профиль"
                        color: "#747A87"
                        font.pixelSize: 9
                        lineHeight: 1.35
                    }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 265

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 11

                    Text {
                        text: "Переключение сцен"
                        color: "#E4E6EC"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Плавный переход"
                        from: 0
                        to: 2500
                        stepSize: 50
                        decimals: 0
                        suffix: " мс"
                        value: controller.transitionMs
                        onChanged: controller.setTransitionMs(Math.round(value))
                    }

                    Text {
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        text: "При смене профиля или готовой сцены BladeRGB плавно смешивает предыдущий и новый RGB-кадр."
                        color: "#777D8A"
                        font.pixelSize: 10
                        lineHeight: 1.4
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 225

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    Text {
                        text: "Клавиатура"
                        color: "#E4E6EC"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                    }

                    Text {
                        text: "ARDOR GAMING BLADE"
                        color: "#D9DBE2"
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                    }

                    Text {
                        text: "VID 0416 · PID C345 · MI_02 · 104 клавиши"
                        color: "#777D8A"
                        font.pixelSize: 9
                    }

                    Item { Layout.fillHeight: true }

                    RowLayout {
                        Layout.fillWidth: true

                        AppButton {
                            Layout.fillWidth: true
                            text: "Переподключить"
                            onClicked: controller.connectDevice()
                        }

                        AppButton {
                            Layout.fillWidth: true
                            text: "Погасить подсветку"
                            danger: true
                            onClicked: controller.blackout()
                        }
                    }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.preferredHeight: 225

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 9

                    Text {
                        text: "Диагностика"
                        color: "#E4E6EC"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: controller.running ? "Подсветка работает" : "Подсветка остановлена"
                            color: controller.running ? "#79C8A4" : "#8B909D"
                            font.pixelSize: 11
                            font.weight: Font.DemiBold
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: controller.actualFps.toFixed(1) + " кад/с"
                            color: "#8F94A1"
                            font.pixelSize: 10
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 9
                        color: "#111318"
                        border.width: 1
                        border.color: "#252933"

                        Text {
                            anchors.fill: parent
                            anchors.margins: 11
                            text: controller.lastError !== "" ? controller.lastError : "Ошибок нет."
                            color: controller.lastError !== "" ? "#D98191" : "#74BA98"
                            font.family: "Consolas"
                            font.pixelSize: 9
                            wrapMode: Text.WrapAnywhere
                        }
                    }
                }
            }
        }
    }
}
