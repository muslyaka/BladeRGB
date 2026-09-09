pragma Singleton
import QtQuick

QtObject {
    readonly property bool light: controller.theme === "light"
    readonly property color accent: controller.accentColor
    readonly property color accentHover: Qt.lighter(accent, light ? 1.03 : 1.14)
    readonly property color accentPressed: Qt.darker(accent, 1.12)
    readonly property color accentSoft: Qt.rgba(accent.r, accent.g, accent.b, light ? 0.12 : 0.20)
    readonly property color accentLight: light ? Qt.darker(accent, 1.05) : Qt.lighter(accent, 1.28)

    readonly property color background: light ? "#F3F5F8" : "#0E1014"
    readonly property color sidebar: light ? "#FFFFFF" : "#121419"
    readonly property color panel: light ? "#FFFFFF" : "#171A20"
    readonly property color panelAlt: light ? "#F8F9FB" : "#1B1E25"
    readonly property color input: light ? "#F4F5F7" : "#191C22"
    readonly property color hover: light ? "#ECEFF3" : "#22252D"
    readonly property color border: light ? "#DDE1E8" : "#252933"
    readonly property color borderStrong: light ? "#C9CED8" : "#343843"

    readonly property color text: light ? "#20242B" : "#F0F1F5"
    readonly property color textSecondary: light ? "#4D5562" : "#B9BDC7"
    readonly property color textMuted: light ? "#69717E" : "#8F95A3"
    readonly property color textSubtle: light ? "#7D8592" : "#747A87"
    readonly property color keyBackground: light ? "#E9ECF1" : "#101217"
    readonly property color success: light ? "#268A62" : "#67C49C"
    readonly property color danger: light ? "#B84B63" : "#E68A9B"
}
