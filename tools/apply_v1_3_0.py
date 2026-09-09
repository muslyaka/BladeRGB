from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"Patch point not found: {label}")
    return text.replace(old, new, 1)


def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.lstrip("\n"), encoding="utf-8")


# -----------------------------------------------------------------------------
# Backend: app appearance + generic palette transition delay.
# -----------------------------------------------------------------------------

p = ROOT / "app/controller.py"
s = p.read_text(encoding="utf-8")

s = replace_once(
    s,
    '''    @Property(int, notify=stateChanged)\n    def transitionMs(self): return int(self.settings.get("transition_ms", 650))\n''',
    '''    @Property(int, notify=stateChanged)\n    def transitionMs(self): return int(self.settings.get("transition_ms", 650))\n    @Property(str, notify=stateChanged)\n    def theme(self): return str(self.settings.get("theme", "dark"))\n    @Property(str, notify=stateChanged)\n    def accentColor(self): return str(self.settings.get("accent_color", "#7772C9"))\n''',
    "controller appearance properties",
)

s = replace_once(
    s,
    '''    @Slot(int)\n    def setTransitionMs(self, value):\n        value=max(0,min(2500,int(value))); self.settings.set("transition_ms",value); self.renderer.transition_duration=value/1000.0; self.stateChanged.emit()\n''',
    '''    @Slot(int)\n    def setTransitionMs(self, value):\n        value=max(0,min(2500,int(value))); self.settings.set("transition_ms",value); self.renderer.transition_duration=value/1000.0; self.stateChanged.emit()\n    @Slot(str)\n    def setTheme(self, value):\n        value = str(value).lower()\n        if value not in {"dark", "light"}: return\n        self.settings.set("theme", value); self.stateChanged.emit()\n    @Slot(str)\n    def setAccentColor(self, value):\n        try: color = rgb_to_hex(hex_to_rgb(str(value)))\n        except Exception: return\n        self.settings.set("accent_color", color); self.stateChanged.emit()\n    @Slot(str, result=str)\n    def layerColor(self, layer_id):\n        layer = next((x for x in self.renderer.get_layers() if x.id == layer_id), None)\n        if layer is None: return "#ffffff"\n        try: return rgb_to_hex(tuple(layer.color))\n        except Exception: return "#ffffff"\n''',
    "controller appearance setters",
)

p.write_text(s, encoding="utf-8")

p = ROOT / "engine/renderer.py"
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    "'overlay_opacity': 1.0}",
    "'overlay_opacity': 1.0, 'palette_delay': 0.0}",
    "renderer palette_delay default",
)

s = replace_once(
    s,
    '''    def _render_custom_layer(self, layer, now, base_params, audio_levels):\n''',
    '''    def _palette_with_delay(self, palette, now, delay):\n        if len(palette) < 2:\n            return palette\n        try: delay = float(delay)\n        except Exception: return palette\n        if delay <= 0.0:\n            return palette\n        delay = max(0.10, delay)\n        phase = now / delay\n        whole = math.floor(phase)\n        index = int(whole) % len(palette)\n        fraction = phase - whole\n        hold = 0.72\n        if fraction <= hold:\n            blend = 0.0\n        else:\n            blend = (fraction - hold) / (1.0 - hold)\n            blend = blend * blend * (3.0 - 2.0 * blend)\n        current = palette[index:] + palette[:index]\n        next_index = (index + 1) % len(palette)\n        following = palette[next_index:] + palette[:next_index]\n        return [mix(a, b, blend) for a, b in zip(current, following)]\n\n    def _render_custom_layer(self, layer, now, base_params, audio_levels):\n''',
    "renderer palette delay helper",
)

s = replace_once(
    s,
    '''            palette=[hex_to_rgb(x) for x in layer.palette] if layer.palette else [(255,255,255)]\n            return (obj.render(now,palette,p),keys)\n''',
    '''            palette=[hex_to_rgb(x) for x in layer.palette] if layer.palette else [(255,255,255)]\n            palette=self._palette_with_delay(palette,now,p.get('palette_delay',0.0))\n            return (obj.render(now,palette,p),keys)\n''',
    "renderer layer palette delay",
)

s = replace_once(
    s,
    '''                if start-last_audio_sync>1.0:\n                    need_audio=audio_enabled or any((x.enabled and x.type=='Audio' for x in layers)); self.audio.start() if need_audio else self.audio.stop(); last_audio_sync=start\n                audio_levels=self.audio.levels(); colors=effect.render(start,palette,p)\n''',
    '''                palette=self._palette_with_delay(palette,start,p.get('palette_delay',0.0))\n                if start-last_audio_sync>1.0:\n                    need_audio=audio_enabled or any((x.enabled and x.type=='Audio' for x in layers)); self.audio.start() if need_audio else self.audio.stop(); last_audio_sync=start\n                audio_levels=self.audio.levels(); colors=effect.render(start,palette,p)\n''',
    "renderer main palette delay",
)

p.write_text(s, encoding="utf-8")

# settings defaults in repository template
p = ROOT / "config/settings.json"
data = json.loads(p.read_text(encoding="utf-8"))
data.setdefault("theme", "dark")
data.setdefault("accent_color", "#7772C9")
p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# -----------------------------------------------------------------------------
# Theme singleton.
# -----------------------------------------------------------------------------

write("qml/components/qmldir", '''module BladeRGB.Components\nsingleton Theme 1.0 Theme.qml\n''')

write("qml/components/Theme.qml", r'''
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
''')

# -----------------------------------------------------------------------------
# RGBW picker: hue around the outside, white in the centre, brightness below.
# It never has an Apply button; every pointer movement emits colorEdited().
# -----------------------------------------------------------------------------

write("qml/components/RGBWPicker.qml", r'''
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: root
    width: 348
    height: 438
    modal: true
    focus: true
    padding: 16
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    property real hue: 0.0
    property real saturation: 0.0
    property real brightness: 1.0
    property string currentHex: "#ffffff"
    signal colorEdited(string colorHex)

    function clamp01(v) { return Math.max(0, Math.min(1, v)) }

    function hsvRgb(h, s, v) {
        h = ((h % 1) + 1) % 1
        s = clamp01(s)
        v = clamp01(v)
        var i = Math.floor(h * 6)
        var f = h * 6 - i
        var p = v * (1 - s)
        var q = v * (1 - f * s)
        var t = v * (1 - (1 - f) * s)
        switch (i % 6) {
        case 0: return [v, t, p]
        case 1: return [q, v, p]
        case 2: return [p, v, t]
        case 3: return [p, q, v]
        case 4: return [t, p, v]
        default: return [v, p, q]
        }
    }

    function byteHex(v) {
        var s = Math.round(clamp01(v) * 255).toString(16).toUpperCase()
        return s.length < 2 ? "0" + s : s
    }

    function hsvHex(h, s, v) {
        var rgb = hsvRgb(h, s, v)
        return "#" + byteHex(rgb[0]) + byteHex(rgb[1]) + byteHex(rgb[2])
    }

    function rgbHsv(r, g, b) {
        r /= 255; g /= 255; b /= 255
        var maxv = Math.max(r, g, b)
        var minv = Math.min(r, g, b)
        var d = maxv - minv
        var h = 0
        if (d > 0.0001) {
            if (maxv === r) h = ((g - b) / d) % 6
            else if (maxv === g) h = (b - r) / d + 2
            else h = (r - g) / d + 4
            h /= 6
            if (h < 0) h += 1
        }
        var s = maxv <= 0.0001 ? 0 : d / maxv
        return [h, s, maxv]
    }

    function openFor(hex) {
        var value = String(hex || "#ffffff")
        if (value.length === 9) value = "#" + value.slice(3)
        if (value.length !== 7) value = "#ffffff"
        var r = parseInt(value.slice(1, 3), 16)
        var g = parseInt(value.slice(3, 5), 16)
        var b = parseInt(value.slice(5, 7), 16)
        var hsv = rgbHsv(r, g, b)
        hue = hsv[0]
        saturation = hsv[1]
        brightness = hsv[2]
        currentHex = hsvHex(hue, saturation, brightness)
        open()
        wheel.requestPaint()
    }

    function emitCurrent() {
        currentHex = hsvHex(hue, saturation, brightness)
        colorEdited(currentHex)
    }

    background: Rectangle {
        radius: 18
        color: Theme.panel
        border.width: 1
        border.color: Theme.border
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 11

        RowLayout {
            Layout.fillWidth: true

            Column {
                spacing: 2
                Text {
                    text: "RGBW"
                    color: Theme.text
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                }
                Text {
                    text: "цвет по краю · белый в центре"
                    color: Theme.textMuted
                    font.pixelSize: 9
                }
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                width: 42
                height: 30
                radius: 9
                color: root.currentHex
                border.width: 1
                border.color: Theme.borderStrong
            }
        }

        Item {
            id: wheelBox
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 286
            Layout.preferredHeight: 286

            Canvas {
                id: wheel
                anchors.fill: parent
                antialiasing: true

                onPaint: {
                    var ctx = getContext("2d")
                    ctx.reset()
                    ctx.clearRect(0, 0, width, height)
                    var cx = width / 2
                    var cy = height / 2
                    var radius = Math.min(width, height) / 2 - 5
                    var pieces = 120
                    for (var i = 0; i < pieces; ++i) {
                        var a0 = (i / pieces) * Math.PI * 2 - Math.PI / 2
                        var a1 = ((i + 1.15) / pieces) * Math.PI * 2 - Math.PI / 2
                        var edge = root.hsvHex(i / pieces, 1, 1)
                        var gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius)
                        gradient.addColorStop(0, "#FFFFFF")
                        gradient.addColorStop(0.18, "#FFFFFF")
                        gradient.addColorStop(1, edge)
                        ctx.beginPath()
                        ctx.moveTo(cx, cy)
                        ctx.arc(cx, cy, radius, a0, a1, false)
                        ctx.closePath()
                        ctx.fillStyle = gradient
                        ctx.fill()
                    }
                }
            }

            Rectangle {
                width: 16
                height: 16
                radius: 8
                color: "transparent"
                border.width: 3
                border.color: Theme.light ? "#22252B" : "#FFFFFF"
                x: wheelBox.width / 2
                    + root.saturation * (wheelBox.width / 2 - 13) * Math.cos(root.hue * Math.PI * 2 - Math.PI / 2)
                    - width / 2
                y: wheelBox.height / 2
                    + root.saturation * (wheelBox.height / 2 - 13) * Math.sin(root.hue * Math.PI * 2 - Math.PI / 2)
                    - height / 2
            }

            MouseArea {
                anchors.fill: parent

                function updateAt(px, py) {
                    var cx = width / 2
                    var cy = height / 2
                    var dx = px - cx
                    var dy = py - cy
                    var radius = Math.min(width, height) / 2 - 5
                    var distance = Math.sqrt(dx * dx + dy * dy)
                    root.saturation = root.clamp01(distance / radius)
                    if (distance > 1) {
                        var angle = Math.atan2(dy, dx) + Math.PI / 2
                        if (angle < 0) angle += Math.PI * 2
                        root.hue = angle / (Math.PI * 2)
                    }
                    root.emitCurrent()
                }

                onPressed: function(mouse) { updateAt(mouse.x, mouse.y) }
                onPositionChanged: function(mouse) {
                    if (pressed) updateAt(mouse.x, mouse.y)
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Text {
                text: "Яркость"
                color: Theme.textSecondary
                font.pixelSize: 10
            }
            Slider {
                id: brightnessSlider
                Layout.fillWidth: true
                from: 0
                to: 1
                value: root.brightness
                onMoved: {
                    root.brightness = value
                    root.emitCurrent()
                }
                background: Rectangle {
                    x: brightnessSlider.leftPadding
                    y: brightnessSlider.topPadding + brightnessSlider.availableHeight / 2 - height / 2
                    width: brightnessSlider.availableWidth
                    height: 5
                    radius: 3
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0; color: "#000000" }
                        GradientStop { position: 1; color: root.hsvHex(root.hue, root.saturation, 1) }
                    }
                }
                handle: Rectangle {
                    x: brightnessSlider.leftPadding + brightnessSlider.visualPosition * (brightnessSlider.availableWidth - width)
                    y: brightnessSlider.topPadding + brightnessSlider.availableHeight / 2 - height / 2
                    width: 15
                    height: 15
                    radius: 8
                    color: Theme.text
                    border.width: 2
                    border.color: Theme.borderStrong
                }
            }
            Text {
                text: Math.round(root.brightness * 100) + "%"
                color: Theme.textMuted
                font.pixelSize: 10
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Text {
                text: root.currentHex
                color: Theme.textMuted
                font.pixelSize: 10
                font.weight: Font.DemiBold
            }
            Item { Layout.fillWidth: true }
            AppButton {
                text: "Белый"
                compact: true
                onClicked: {
                    root.saturation = 0
                    root.brightness = 1
                    root.emitCurrent()
                }
            }
            AppButton {
                text: "Закрыть"
                compact: true
                onClicked: root.close()
            }
        }
    }
}
''')

# -----------------------------------------------------------------------------
# Core controls now follow Theme + accent color.
# -----------------------------------------------------------------------------

write("qml/components/Panel.qml", r'''
import QtQuick
Rectangle {
    radius: 14
    color: Theme.panel
    border.width: 1
    border.color: Theme.border
}
''')

write("qml/components/AppButton.qml", r'''
import QtQuick
import QtQuick.Controls

Button {
    id: root
    property bool accent: false
    property bool danger: false
    property bool compact: false

    implicitHeight: compact ? 34 : 38
    leftPadding: compact ? 12 : 15
    rightPadding: compact ? 12 : 15

    background: Rectangle {
        radius: 9
        color: root.accent
            ? (root.down ? Theme.accentPressed : root.hovered ? Theme.accentHover : Theme.accent)
            : root.danger
                ? (root.hovered ? (Theme.light ? "#FCE8EC" : "#2A1D23") : (Theme.light ? "#FFF3F5" : "#211A1E"))
                : (root.hovered ? Theme.hover : Theme.input)
        border.width: 1
        border.color: root.accent
            ? Theme.accentHover
            : root.danger
                ? (Theme.light ? "#E8BAC5" : "#55303A")
                : Theme.border

        Behavior on color { ColorAnimation { duration: 110 } }
    }

    contentItem: Text {
        text: root.text
        color: root.danger ? Theme.danger : root.accent ? "#FFFFFF" : Theme.text
        font.pixelSize: 11
        font.weight: Font.DemiBold
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
}
''')

write("qml/components/MetricSlider.qml", r'''
import QtQuick
import QtQuick.Controls

Item {
    id: root
    property string label: ""
    property real value: 0
    property real from: 0
    property real to: 1
    property real stepSize: 0.01
    property int decimals: 2
    property string suffix: ""
    signal changed(real value)
    implicitHeight: 52

    Text { text: root.label; color: Theme.textSecondary; font.pixelSize: 11; anchors.left: parent.left; anchors.top: parent.top }
    Text {
        text: Number(slider.value).toFixed(root.decimals) + root.suffix
        color: Theme.text
        font.pixelSize: 10
        font.weight: Font.DemiBold
        anchors.right: parent.right
        anchors.top: parent.top
    }

    Slider {
        id: slider
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        from: root.from
        to: root.to
        stepSize: root.stepSize
        value: root.value
        onMoved: root.changed(value)

        background: Rectangle {
            x: slider.leftPadding
            y: slider.topPadding + slider.availableHeight / 2 - height / 2
            width: slider.availableWidth
            height: 4
            radius: 2
            color: Theme.border
            Rectangle {
                width: slider.visualPosition * parent.width
                height: parent.height
                radius: 2
                color: Theme.accent
            }
        }
        handle: Rectangle {
            x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
            y: slider.topPadding + slider.availableHeight / 2 - height / 2
            width: 14
            height: 14
            radius: 7
            color: Theme.light ? "#FFFFFF" : "#E8E6F5"
            border.width: 2
            border.color: Theme.accent
        }
    }
}
''')

write("qml/components/CalmSwitch.qml", r'''
import QtQuick
import QtQuick.Controls
Switch {
    id: root
    implicitWidth: 42
    implicitHeight: 24
    indicator: Rectangle {
        implicitWidth: 38
        implicitHeight: 22
        radius: 11
        color: root.checked ? Theme.accent : Theme.border
        border.width: 1
        border.color: root.checked ? Theme.accentHover : Theme.borderStrong
        Rectangle {
            width: 16
            height: 16
            radius: 8
            x: root.checked ? parent.width - width - 3 : 3
            anchors.verticalCenter: parent.verticalCenter
            color: root.checked ? "#FFFFFF" : Theme.textMuted
            Behavior on x { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }
        }
    }
    contentItem: Item {}
}
''')

write("qml/components/CalmTextField.qml", r'''
import QtQuick
import QtQuick.Controls
TextField {
    id: root
    implicitHeight: 40
    color: Theme.text
    placeholderTextColor: Theme.textSubtle
    selectionColor: Theme.accent
    selectedTextColor: "white"
    font.pixelSize: 11
    leftPadding: 12
    rightPadding: 12
    background: Rectangle {
        radius: 9
        color: root.activeFocus ? Theme.hover : Theme.input
        border.width: 1
        border.color: root.activeFocus ? Theme.accent : Theme.border
    }
}
''')

write("qml/components/CalmComboBox.qml", r'''
import QtQuick
import QtQuick.Controls
ComboBox {
    id: root
    implicitHeight: 40
    leftPadding: 12
    rightPadding: 34
    font.pixelSize: 11
    delegate: ItemDelegate {
        width: root.width
        height: 36
        highlighted: root.highlightedIndex === index
        contentItem: Text {
            text: root.textRole.length > 0 ? (modelData[root.textRole] || "") : String(modelData)
            color: Theme.text
            font.pixelSize: 11
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
        background: Rectangle { radius: 7; color: highlighted ? Theme.hover : "transparent" }
    }
    indicator: Text {
        text: "⌄"
        color: Theme.textMuted
        font.pixelSize: 14
        anchors.right: parent.right
        anchors.rightMargin: 11
        anchors.verticalCenter: parent.verticalCenter
    }
    contentItem: Text {
        text: root.displayText
        color: Theme.text
        font.pixelSize: 11
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
    background: Rectangle {
        radius: 9
        color: root.hovered || root.activeFocus ? Theme.hover : Theme.input
        border.width: 1
        border.color: root.activeFocus ? Theme.accent : Theme.border
    }
    popup: Popup {
        y: root.height + 4
        width: root.width
        implicitHeight: Math.min(contentItem.implicitHeight + 8, 280)
        padding: 4
        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: root.popup.visible ? root.delegateModel : null
            currentIndex: root.highlightedIndex
            ScrollIndicator.vertical: ScrollIndicator {}
        }
        background: Rectangle { radius: 10; color: Theme.panel; border.width: 1; border.color: Theme.border }
    }
}
''')

write("qml/components/PageHeader.qml", r'''
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
''')

write("qml/components/SectionLabel.qml", r'''
import QtQuick
Text { color: Theme.textMuted; font.pixelSize: 10; font.weight: Font.DemiBold; font.letterSpacing: 0.3 }
''')

write("qml/components/StatusPill.qml", r'''
import QtQuick
import QtQuick.Layouts
Rectangle {
    id: root
    property bool online: false
    property string label: ""
    implicitWidth: row.implicitWidth + 22
    implicitHeight: 34
    radius: 9
    color: Theme.input
    border.width: 1
    border.color: Theme.border
    Row {
        id: row
        anchors.centerIn: parent
        spacing: 8
        Rectangle { width: 7; height: 7; radius: 4; color: root.online ? Theme.success : Theme.textSubtle }
        Text { text: root.label; color: Theme.textSecondary; font.pixelSize: 9; font.weight: Font.DemiBold }
    }
}
''')

write("qml/components/NavItem.qml", r'''
import QtQuick
import QtQuick.Controls
Button {
    id: root
    property bool selected: false
    property string glyph: "•"
    implicitHeight: 44
    background: Rectangle {
        radius: 9
        color: root.selected ? Theme.accentSoft : root.hovered ? Theme.hover : "transparent"
        Rectangle {
            visible: root.selected
            width: 3
            height: 20
            radius: 2
            color: Theme.accent
            anchors.left: parent.left
            anchors.leftMargin: 1
            anchors.verticalCenter: parent.verticalCenter
        }
    }
    contentItem: Row {
        spacing: 10
        leftPadding: 12
        Text { width: 20; text: root.glyph; color: root.selected ? Theme.accentLight : Theme.textSubtle; font.pixelSize: 14; anchors.verticalCenter: parent.verticalCenter; horizontalAlignment: Text.AlignHCenter }
        Text { text: root.text; color: root.selected ? Theme.text : Theme.textMuted; font.pixelSize: 12; font.weight: root.selected ? Font.DemiBold : Font.Normal; anchors.verticalCenter: parent.verticalCenter }
    }
}
''')

# Keyboard background and labels follow theme, while actual LED key colors stay intact.
p = ROOT / "qml/components/KeyboardView.qml"
s = p.read_text(encoding="utf-8")
for old, new in {
    'color: "#101217"': 'color: Theme.keyBackground',
    'border.color: "#262A33"': 'border.color: Theme.border',
    'border.color: selected ? "#DCD9F2" : "#343843"': 'border.color: selected ? Theme.accentLight : Theme.borderStrong',
    'color: "#EDEEF3"': 'color: Theme.text',
    'color: "#E8E9EE"': 'color: Theme.text',
}.items():
    s = s.replace(old, new)
p.write_text(s, encoding="utf-8")

# -----------------------------------------------------------------------------
# Compact Dashboard.
# -----------------------------------------------------------------------------

write("qml/pages/Dashboard.qml", r'''
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
''')

# -----------------------------------------------------------------------------
# Studio: custom RGBW picker and immediate updates for brush/reactive colors.
# -----------------------------------------------------------------------------

p = ROOT / "qml/pages/Studio.qml"
s = p.read_text(encoding="utf-8")
s = s.replace('import QtQuick.Dialogs\n', '')

old = '''                    MouseArea {\n                        anchors.fill: parent\n                        onClicked: brushDialog.open()\n                    }\n\n                    ColorDialog {\n                        id: brushDialog\n                        title: "Цвет кисти"\n                        selectedColor: root.brush\n                        onAccepted: root.brush = selectedColor.toString()\n                    }\n'''
new = '''                    MouseArea {\n                        anchors.fill: parent\n                        onClicked: brushPicker.openFor(root.brush)\n                    }\n\n                    RGBWPicker {\n                        id: brushPicker\n                        onColorEdited: function(hex) {\n                            root.brush = hex\n                            for (var key in root.selected)\n                                if (root.selected[key] === true) controller.paintKey(key, hex)\n                        }\n                    }\n'''
s = replace_once(s, old, new, "studio brush picker")

old = '''                            MouseArea {\n                                anchors.fill: parent\n                                onClicked: {\n                                    reactiveDialog.selectedColor = controller.reactiveColor\n                                    reactiveDialog.open()\n                                }\n                            }\n\n                            ColorDialog {\n                                id: reactiveDialog\n                                title: "Цвет реакции"\n                                selectedColor: "#ffffff"\n                                onAccepted: controller.setReactiveColor(selectedColor.toString())\n                            }\n'''
new = '''                            MouseArea {\n                                anchors.fill: parent\n                                onClicked: reactivePicker.openFor(controller.reactiveColor)\n                            }\n\n                            RGBWPicker {\n                                id: reactivePicker\n                                onColorEdited: function(hex) { controller.setReactiveColor(hex) }\n                            }\n'''
s = replace_once(s, old, new, "studio reactive picker")
p.write_text(s, encoding="utf-8")

# Layers: custom picker and live application.
p = ROOT / "qml/pages/Layers.qml"
s = p.read_text(encoding="utf-8").replace('import QtQuick.Dialogs\n', '')
old = '''                            AppButton {\n                                Layout.fillWidth: true\n                                text: "Выбрать цвет слоя"\n                                onClicked: layerColorDialog.open()\n                            }\n\n                            ColorDialog {\n                                id: layerColorDialog\n                                title: "Цвет слоя"\n                                onAccepted: controller.setLayerField(root.selectedId, "color", selectedColor.toString())\n                            }\n'''
new = '''                            AppButton {\n                                Layout.fillWidth: true\n                                text: "Выбрать цвет слоя"\n                                onClicked: layerColorPicker.openFor(controller.layerColor(root.selectedId))\n                            }\n\n                            RGBWPicker {\n                                id: layerColorPicker\n                                onColorEdited: function(hex) { controller.setLayerField(root.selectedId, "color", hex) }\n                            }\n'''
s = replace_once(s, old, new, "layers color picker")
p.write_text(s, encoding="utf-8")

# -----------------------------------------------------------------------------
# Settings: appearance panel with light/dark theme + live accent RGBW picker.
# -----------------------------------------------------------------------------

write("qml/pages/Settings.qml", r'''
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
                        Column { Layout.fillWidth: true; spacing: 2; Text { text: "Сворачивать в трей при закрытии"; color: Theme.textSecondary; font.pixelSize: 11 }; Text { text: "Подсветка продолжает работать"; color: Theme.textMuted; font.pixelSize: 9 } }
                        CalmSwitch { checked: controller.closeToTray; onToggled: controller.setCloseToTray(checked) }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Column { Layout.fillWidth: true; spacing: 2; Text { text: "Запускать вместе с Windows"; color: Theme.textSecondary; font.pixelSize: 11 }; Text { text: "Стартует скрыто в трее"; color: Theme.textMuted; font.pixelSize: 9 } }
                        CalmSwitch { checked: controller.autostartEnabled; onToggled: controller.setAutostart(checked) }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Column { Layout.fillWidth: true; spacing: 2; Text { text: "Глобальные горячие клавиши"; color: Theme.textSecondary; font.pixelSize: 11 }; Text { text: "Работают при скрытом окне"; color: Theme.textMuted; font.pixelSize: 9 } }
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
''')

# -----------------------------------------------------------------------------
# Main window: theme-aware shell.
# -----------------------------------------------------------------------------

write("qml/Main.qml", r'''
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "pages"

ApplicationWindow {
    id: win
    visible: true
    width: 1360
    height: 840
    minimumWidth: 1080
    minimumHeight: 700
    title: "BladeRGB"
    color: Theme.background

    property string page: "dashboard"
    property string toastTitle: ""
    property string toastText: ""

    onClosing: function(close) {
        close.accepted = false
        if (controller.closeToTray) controller.hideWindow()
        else controller.quitApp()
    }

    Rectangle { anchors.fill: parent; color: Theme.background }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 204
            Layout.fillHeight: true
            color: Theme.sidebar
            Rectangle { width: 1; color: Theme.border; anchors.top: parent.top; anchors.bottom: parent.bottom; anchors.right: parent.right }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 5
                RowLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: 5
                    Layout.rightMargin: 5
                    Layout.topMargin: 5
                    Layout.bottomMargin: 21
                    spacing: 10
                    Rectangle {
                        width: 36; height: 36; radius: 10; color: Theme.accent
                        Text { anchors.centerIn: parent; text: "B"; color: "white"; font.pixelSize: 16; font.weight: Font.DemiBold }
                    }
                    Column {
                        spacing: 1
                        Text { text: "BladeRGB"; color: Theme.text; font.pixelSize: 15; font.weight: Font.DemiBold }
                        Text { text: "ARDOR BLADE"; color: Theme.textSubtle; font.pixelSize: 8; font.weight: Font.Medium }
                    }
                }

                NavItem { Layout.fillWidth: true; text: "Обзор"; glyph: "○"; selected: win.page === "dashboard"; onClicked: win.page = "dashboard" }
                NavItem { Layout.fillWidth: true; text: "Покраска"; glyph: "✦"; selected: win.page === "studio"; onClicked: win.page = "studio" }
                NavItem { Layout.fillWidth: true; text: "Слои"; glyph: "≡"; selected: win.page === "layers"; onClicked: win.page = "layers" }
                NavItem { Layout.fillWidth: true; text: "Анимация"; glyph: "◇"; selected: win.page === "animator"; onClicked: win.page = "animator" }
                NavItem { Layout.fillWidth: true; text: "Профили"; glyph: "◎"; selected: win.page === "profiles"; onClicked: win.page = "profiles" }
                NavItem { Layout.fillWidth: true; text: "Настройки"; glyph: "⚙"; selected: win.page === "settings"; onClicked: win.page = "settings" }
                Item { Layout.fillHeight: true }

                Rectangle {
                    Layout.fillWidth: true
                    height: 58
                    radius: 11
                    color: Theme.panelAlt
                    border.width: 1
                    border.color: Theme.border
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 8
                        Rectangle { width: 7; height: 7; radius: 4; color: controller.connected ? Theme.success : Theme.textSubtle }
                        Column {
                            Layout.fillWidth: true
                            spacing: 2
                            Text { text: "ARDOR BLADE"; color: Theme.text; font.pixelSize: 10; font.weight: Font.DemiBold }
                            Text { text: controller.statusText; color: Theme.textMuted; font.pixelSize: 8; font.weight: Font.Medium }
                        }
                        Text { text: controller.running ? controller.actualFps.toFixed(0) : "—"; color: Theme.accentLight; font.pixelSize: 10; font.weight: Font.DemiBold }
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Loader {
                anchors.fill: parent
                anchors.leftMargin: 28
                anchors.rightMargin: 28
                anchors.topMargin: 24
                anchors.bottomMargin: 24
                sourceComponent: win.page === "dashboard" ? dashboard : win.page === "studio" ? studio : win.page === "layers" ? layers : win.page === "animator" ? animator : win.page === "profiles" ? profiles : settings
            }
        }
    }

    Component { id: dashboard; Dashboard {} }
    Component { id: studio; Studio {} }
    Component { id: layers; Layers {} }
    Component { id: animator; Animator {} }
    Component { id: profiles; Profiles {} }
    Component { id: settings; Settings {} }

    Rectangle {
        id: toast
        width: Math.min(400, parent.width - 40)
        height: toastColumn.implicitHeight + 26
        radius: 12
        color: Theme.panel
        border.width: 1
        border.color: Theme.border
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 18
        opacity: 0
        visible: opacity > 0
        Column {
            id: toastColumn
            anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 13; spacing: 4
            Text { text: win.toastTitle; color: Theme.text; font.pixelSize: 12; font.weight: Font.DemiBold }
            Text { width: parent.width; text: win.toastText; color: Theme.textMuted; font.pixelSize: 10; wrapMode: Text.WordWrap }
        }
        Behavior on opacity { NumberAnimation { duration: 140 } }
        Timer { id: hideToast; interval: 3000; onTriggered: toast.opacity = 0 }
    }

    Connections {
        target: controller
        function onToast(title, message) { win.toastTitle = title; win.toastText = message; toast.opacity = 1; hideToast.restart() }
    }
}
''')

# -----------------------------------------------------------------------------
# Theme common hardcoded colors in remaining pages. This keeps light theme
# readable without changing their layout.
# -----------------------------------------------------------------------------

replacements = {
    '"#E4E6EC"': 'Theme.text',
    '"#E8E9EE"': 'Theme.text',
    '"#F0F1F5"': 'Theme.text',
    '"#E2E4EA"': 'Theme.text',
    '"#E5E7EC"': 'Theme.text',
    '"#DADCE3"': 'Theme.text',
    '"#D9DBE2"': 'Theme.text',
    '"#C4C7D0"': 'Theme.textSecondary',
    '"#BFC2CB"': 'Theme.textSecondary',
    '"#B9BDC7"': 'Theme.textSecondary',
    '"#A2A7B3"': 'Theme.textSecondary',
    '"#9B9FAC"': 'Theme.textMuted',
    '"#9297A5"': 'Theme.textMuted',
    '"#8F95A3"': 'Theme.textMuted',
    '"#8F95A2"': 'Theme.textMuted',
    '"#8E93A1"': 'Theme.textMuted',
    '"#7F8593"': 'Theme.textMuted',
    '"#777D8A"': 'Theme.textMuted',
    '"#747A87"': 'Theme.textSubtle',
    '"#737986"': 'Theme.textSubtle',
    '"#707683"': 'Theme.textSubtle',
    '"#6F7582"': 'Theme.textSubtle',
    '"#171A20"': 'Theme.panel',
    '"#1B1E25"': 'Theme.panelAlt',
    '"#191C22"': 'Theme.input',
    '"#1D2027"': 'Theme.input',
    '"#111318"': 'Theme.input',
    '"#252933"': 'Theme.border',
    '"#282C35"': 'Theme.border',
    '"#292D36"': 'Theme.border',
    '"#2A2E37"': 'Theme.border',
    '"#343843"': 'Theme.borderStrong',
    '"#7772C9"': 'Theme.accent',
    '"#9792D5"': 'Theme.accentLight',
    '"#A5A1D9"': 'Theme.accentLight',
}

for rel in ["qml/pages/Animator.qml", "qml/pages/Profiles.qml", "qml/pages/Layers.qml", "qml/pages/Studio.qml"]:
    p = ROOT / rel
    text = p.read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")

# Version + README.
write("VERSION.txt", "BladeRGB 1.3.0 RU\nRGBW Live Color, themes, accent and compact dashboard\n")

p = ROOT / "README.md"
s = p.read_text(encoding="utf-8")
notes = '''## 1.3.0 — RGBW Live UI\n\n- системный выбор цвета заменён собственным RGBW-диском: оттенки по окружности, белый в центре, отдельная яркость;\n- все цвета применяются в реальном времени прямо во время движения по цветовому диску;\n- RGBW-пикер используется для основной палитры, кисти, Reactive RGB, цвета слоя и акцентного цвета интерфейса;\n- добавлена задержка между переходами палитры на следующий цвет;\n- добавлены светлая и тёмная темы;\n- добавлен пользовательский акцентный цвет интерфейса с live-preview;\n- экран «Обзор» стал компактнее: клавиатура слева, основные параметры справа, ниже — основная подсветка и тонкая настройка эффекта;\n- сохранена совместимость профилей BladeRGB 1.1.x/1.2.x.\n\n'''
if "## 1.3.0 —" not in s:
    s = notes + s
s = s.replace("Текущая версия: **1.1.1 RU**", "Текущая версия: **1.3.0 RU**")
p.write_text(s, encoding="utf-8")

print("BladeRGB 1.3.0 patch applied")
