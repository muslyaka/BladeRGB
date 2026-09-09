from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"Patch point not found: {label}")
    return text.replace(old, new, 1)


# Renderer: move global brightness before quick Reactive RGB.
p = ROOT / "engine/renderer.py"
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    '''                if reactive_enabled:\n                    colors = self.reactive.apply(\n                        colors,\n                        start,\n                        color=reactive_color,\n                        strength=p["reactive_strength"],\n                        decay=p["reactive_decay"],\n                        radius_speed=p["reactive_speed"],\n                        mode=reactive_mode,\n                    )\n\n                br = max(0, min(1, p["brightness"]))\n                final = {\n                    k: tuple(clamp255(v*br) for v in c)\n                    for k, c in colors.items()\n                }\n''',
    '''                # Global brightness controls the steady scene. Reactive key\n                # feedback is composited afterwards, so it is not dimmed by the\n                # background brightness slider.\n                br = max(0, min(1, p["brightness"]))\n                final = {\n                    k: tuple(clamp255(v*br) for v in c)\n                    for k, c in colors.items()\n                }\n\n                if reactive_enabled:\n                    final = self.reactive.apply(\n                        final,\n                        start,\n                        color=reactive_color,\n                        strength=p["reactive_strength"],\n                        decay=p["reactive_decay"],\n                        radius_speed=p["reactive_speed"],\n                        mode=reactive_mode,\n                    )\n                    final = {\n                        k: tuple(clamp255(v) for v in c)\n                        for k, c in final.items()\n                    }\n''',
    "renderer reactive/brightness order",
)
p.write_text(s, encoding="utf-8")


# Reactive color dialog: initialize color only when opening the dialog.
p = ROOT / "qml/pages/Studio.qml"
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    '''                            MouseArea {\n                                anchors.fill: parent\n                                onClicked: reactiveDialog.open()\n                            }\n\n                            ColorDialog {\n                                id: reactiveDialog\n                                title: "Цвет реакции"\n                                selectedColor: controller.reactiveColor\n                                onAccepted: controller.setReactiveColor(selectedColor.toString())\n                            }\n''',
    '''                            MouseArea {\n                                anchors.fill: parent\n                                onClicked: {\n                                    reactiveDialog.selectedColor = controller.reactiveColor\n                                    reactiveDialog.open()\n                                }\n                            }\n\n                            ColorDialog {\n                                id: reactiveDialog\n                                title: "Цвет реакции"\n                                selectedColor: "#ffffff"\n                                onAccepted: controller.setReactiveColor(selectedColor.toString())\n                            }\n''',
    "reactive ColorDialog binding",
)
s = replace_once(
    s,
    '''                        SectionLabel { text: "Цвет реакции" }\n                        Item { Layout.fillWidth: true }\n\n                        Rectangle {\n''',
    '''                        SectionLabel { text: "Цвет реакции" }\n                        Item { Layout.fillWidth: true }\n\n                        Text {\n                            text: controller.reactiveColor.toUpperCase()\n                            color: "#8F95A2"\n                            font.pixelSize: 10\n                            font.weight: Font.DemiBold\n                        }\n\n                        Rectangle {\n''',
    "reactive HEX label",
)
p.write_text(s, encoding="utf-8")


# Version and README.
(ROOT / "VERSION.txt").write_text(
    "BladeRGB 1.1.1 RU\nBugfix: autosave state + reactive color/brightness\n",
    encoding="utf-8",
)
p = ROOT / "README.md"
s = p.read_text(encoding="utf-8")
s = s.replace("# BladeRGB 1.1.0 — Russian Calm UI", "# BladeRGB 1.1.1 — Russian Calm UI", 1)
notes = '''## 1.1.1 — сохранение состояния и Reactive RGB\n\n- последнее состояние подсветки автоматически сохраняется после изменений и восстанавливается при следующем запуске;\n- состояние дополнительно сохраняется при штатном выходе и завершении Windows-сессии;\n- `settings.json` записывается через временный файл с атомарной заменой;\n- общая яркость теперь регулирует основную подсветку, но не приглушает реакцию на нажатие;\n- исправлен выбор цвета реакции: диалог больше не сбрасывает цвет обратно на белый;\n- рядом с выбором цвета реакции отображается фактический HEX-цвет.\n\n'''
if "## 1.1.1 —" not in s:
    marker = "## Что изменилось в 1.1.0\n"
    if marker in s:
        s = s.replace(marker, notes + marker, 1)
    else:
        s = notes + s
p.write_text(s, encoding="utf-8")

print("BladeRGB 1.1.1 finish patch applied")
