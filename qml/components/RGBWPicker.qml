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
