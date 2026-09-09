import QtQuick
import QtQuick.Layouts
Column {
    id: root
    property string title: ""
    property string subtitle: ""
    spacing: 5
    Text { text: root.title; color: Theme.text; font.pixelSize: 27; font.weight: Font.DemiBold }
    Text { text: root.subtitle; color: Theme.textMuted; font.pixelSize: 11 }
}
