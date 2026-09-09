import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: root
    property string nameInput: ""
    property string exeInput: ""

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            PageHeader {
                Layout.fillWidth: true
                title: "Профили"
                subtitle: "Сохраняйте всю сцену подсветки и переключайте её по приложениям"
            }

            AppButton {
                text: "Импорт .brgb"
                compact: true
                onClicked: controller.importProfile()
            }

            AppButton {
                text: "Экспорт текущего"
                compact: true
                onClicked: controller.exportCurrentProfile()
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14

            Panel {
                Layout.preferredWidth: Math.max(430, root.width * 0.52)
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 10

                    Text {
                        text: "Сохранённые профили"
                        color: Theme.text
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        CalmTextField {
                            Layout.fillWidth: true
                            placeholderText: "Название профиля"
                            text: root.nameInput
                            onTextChanged: root.nameInput = text
                        }

                        AppButton {
                            text: "Сохранить"
                            accent: true
                            onClicked: {
                                if (root.nameInput.trim() !== "") {
                                    controller.saveProfile(root.nameInput)
                                    root.nameInput = ""
                                }
                            }
                        }
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 7
                        clip: true
                        model: controller.profileNames

                        delegate: Rectangle {
                            required property string modelData
                            width: ListView.view.width
                            height: 62
                            radius: 10
                            color: controller.currentProfile === modelData ? "#22252E" : Theme.panelAlt
                            border.width: 1
                            border.color: controller.currentProfile === modelData ? "#57538B" : Theme.border

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 9
                                spacing: 9

                                Rectangle {
                                    width: 30
                                    height: 30
                                    radius: 8
                                    color: Theme.accent

                                    Text {
                                        anchors.centerIn: parent
                                        text: "P"
                                        color: "white"
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                    }
                                }

                                Column {
                                    Layout.fillWidth: true
                                    spacing: 2

                                    Text {
                                        text: modelData
                                        color: Theme.text
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        elide: Text.ElideRight
                                    }

                                    Text {
                                        text: controller.currentProfile === modelData ? "Текущий профиль" : "Пользовательский профиль"
                                        color: Theme.textSubtle
                                        font.pixelSize: 8
                                    }
                                }

                                AppButton {
                                    text: "Загрузить"
                                    accent: true
                                    compact: true
                                    onClicked: controller.loadProfile(modelData)
                                }

                                AppButton {
                                    text: "Удалить"
                                    danger: true
                                    compact: true
                                    onClicked: controller.deleteProfile(modelData)
                                }
                            }
                        }
                    }
                }
            }

            Panel {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 10

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: "Автопереключение"
                            color: Theme.text
                            font.pixelSize: 14
                            font.weight: Font.DemiBold
                        }

                        Item { Layout.fillWidth: true }

                        CalmSwitch {
                            checked: controller.autoProfilesEnabled
                            onToggled: controller.setAutoProfilesEnabled(checked)
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 58
                        radius: 10
                        color: Theme.panelAlt
                        border.width: 1
                        border.color: Theme.border

                        Column {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: 11
                            spacing: 2

                            Text {
                                text: "Активное приложение"
                                color: Theme.textSubtle
                                font.pixelSize: 8
                            }

                            Text {
                                text: controller.foregroundExe
                                color: Theme.text
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                            }
                        }
                    }

                    SectionLabel { text: "Исполняемый файл" }

                    CalmTextField {
                        Layout.fillWidth: true
                        placeholderText: "Например: gta5.exe"
                        text: root.exeInput
                        onTextChanged: root.exeInput = text
                    }

                    SectionLabel { text: "Профиль" }

                    CalmComboBox {
                        id: profileBox
                        Layout.fillWidth: true
                        model: controller.profileNames
                    }

                    AppButton {
                        Layout.fillWidth: true
                        text: "Привязать приложение к профилю"
                        accent: true
                        enabled: root.exeInput.trim() !== "" && profileBox.currentText !== ""

                        onClicked: {
                            controller.bindApp(root.exeInput, profileBox.currentText)
                            root.exeInput = ""
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: Theme.border
                        Layout.topMargin: 2
                        Layout.bottomMargin: 2
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 6
                        clip: true
                        model: controller.appBindings

                        delegate: Rectangle {
                            required property var modelData
                            width: ListView.view.width
                            height: 54
                            radius: 10
                            color: Theme.panelAlt
                            border.width: 1
                            border.color: Theme.border

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 9

                                Column {
                                    Layout.fillWidth: true
                                    spacing: 2

                                    Text {
                                        text: modelData.exe
                                        color: Theme.text
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                    }

                                    Text {
                                        text: "Профиль: " + modelData.profile
                                        color: Theme.textSubtle
                                        font.pixelSize: 9
                                    }
                                }

                                AppButton {
                                    text: "Убрать"
                                    danger: true
                                    compact: true
                                    onClicked: controller.unbindApp(modelData.exe)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
