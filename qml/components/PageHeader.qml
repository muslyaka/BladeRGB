import QtQuick
import QtQuick.Layouts

Column {
    id: root
    property string title: ""
    property string subtitle: ""
    spacing: 5

    Text {
        text: root.title
        color: "#F0F1F5"
        font.pixelSize: 27
        font.weight: Font.DemiBold
    }

    Text {
        text: root.subtitle
        color: "#7F8593"
        font.pixelSize: 11
    }
}
