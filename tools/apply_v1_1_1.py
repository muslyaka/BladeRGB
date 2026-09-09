from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"Patch point not found: {label}")
    return text.replace(old, new, 1)


# 1) Atomic settings writes.
p = ROOT / "app/settings.py"
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    "import json\nfrom pathlib import Path\n",
    "import json\nimport os\nfrom pathlib import Path\n",
    "settings imports",
)
s = replace_once(
    s,
    '''    def save(self):\n        self.path.parent.mkdir(parents=True, exist_ok=True)\n        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")\n''',
    '''    def save(self):\n        self.path.parent.mkdir(parents=True, exist_ok=True)\n        payload = json.dumps(self.data, ensure_ascii=False, indent=2)\n        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")\n\n        try:\n            with temp_path.open("w", encoding="utf-8", newline="\\n") as fh:\n                fh.write(payload)\n                fh.flush()\n                os.fsync(fh.fileno())\n            temp_path.replace(self.path)\n        except Exception:\n            try:\n                temp_path.unlink(missing_ok=True)\n            except Exception:\n                pass\n            self.path.write_text(payload, encoding="utf-8")\n''',
    "settings save",
)
p.write_text(s, encoding="utf-8")


# 2) Restore/autosave the complete current lighting scene from main.py.
p = ROOT / "main.py"
s = p.read_text(encoding="utf-8")
s = replace_once(s, "import logging\nimport os\nimport sys\n", "import json\nimport logging\nimport os\nimport sys\n", "main json import")
s = replace_once(s, "from PySide6.QtCore import QUrl, Qt\n", "from PySide6.QtCore import QTimer, QUrl, Qt\n", "main QTimer import")
s = replace_once(
    s,
    '''    controller = BladeController()\n    engine = QQmlApplicationEngine()\n''',
    '''    controller = BladeController()\n\n    # Restore the exact last scene, including unsaved slider/palette/reactive\n    # adjustments. If there is no autosaved scene yet, fall back to the last\n    # explicitly loaded named profile.\n    restored_state = controller.settings.get("last_state")\n    if not isinstance(restored_state, dict):\n        last_profile = controller.settings.get("last_profile", "")\n        if last_profile:\n            try:\n                restored_state = controller.profile_store.load(last_profile)\n            except Exception:\n                restored_state = None\n    if isinstance(restored_state, dict):\n        try:\n            controller.apply_state(restored_state)\n        except Exception:\n            logging.exception("Failed to restore last lighting state")\n\n    # Save only when the scene actually changes. Polling also covers future UI\n    # controls without requiring a persistence hook in each setter.\n    last_saved_fingerprint = {"value": None}\n\n    def save_current_scene(force=False):\n        try:\n            state = controller.capture_state()\n            fingerprint = json.dumps(\n                state,\n                ensure_ascii=False,\n                sort_keys=True,\n                separators=(",", ":"),\n            )\n            if force or fingerprint != last_saved_fingerprint["value"]:\n                controller.settings.set("last_state", state)\n                last_saved_fingerprint["value"] = fingerprint\n        except Exception:\n            logging.exception("Failed to autosave lighting state")\n\n    save_current_scene(force=True)\n    autosave_timer = QTimer(app)\n    autosave_timer.setInterval(300)\n    autosave_timer.timeout.connect(save_current_scene)\n    autosave_timer.start()\n\n    engine = QQmlApplicationEngine()\n''',
    "main restore/autosave",
)
s = replace_once(
    s,
    '''    def quit_app():\n        controller.shutdown()\n        tray.hide()\n        app.quit()\n''',
    '''    def quit_app():\n        save_current_scene(force=True)\n        controller.shutdown()\n        tray.hide()\n        app.quit()\n''',
    "main quit save",
)
s = replace_once(
    s,
    '''    controller.requestQuit.connect(quit_app)\n\n    def tray_activated(reason):\n''',
    '''    controller.requestQuit.connect(quit_app)\n    app.aboutToQuit.connect(lambda: save_current_scene(force=True))\n\n    def tray_activated(reason):\n''',
    "main aboutToQuit save",
)
s = replace_once(
    s,
    '''    code = app.exec()\n    controller.shutdown()\n    return code\n''',
    '''    code = app.exec()\n    save_current_scene(force=True)\n    controller.shutdown()\n    return code\n''',
    "main final save",
)
p.write_text(s, encoding="utf-8")


# 3) Global brightness must not dim key-press feedback.
p = ROOT / "engine/renderer.py"
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    '''                if reactive_enabled:\n                    colors = self.reactive.apply(\n                        colors,\n                        start,\n                        color=reactive_color,\n                        strength=p["reactive_strength"],\n                        decay=p["reactive_decay"],\n                        radius_speed=p["reactive_speed"],\n                        mode=reactive_mode,\n                    )\n\n                br = max(0, min(1, p["brightness"]))\n                final = {\n                    k: tuple(clamp255(v*br) for v in c)\n                    for k, c in colors.items()\n                }\n''',
    '''                # Global brightness controls the steady scene. Reactive key\n                # feedback is composited afterwards, so it is not dimmed by the\n                # background brightness slider.\n                br = max(0, min(1, p["brightness"]))\n                final = {\n                    k: tuple(clamp255(v*br) for v in c)\n                    for k, c in colors.items()\n                }\n\n                if reactive_enabled:\n                    final = self.reactive.apply(\n                        final,\n                        start,\n                        color=reactive_color,\n                        strength=p["reactive_strength"],\n                        decay=p["reactive_decay"],\n                        radius_speed=p["reactive_speed"],\n                        mode=reactive_mode,\n                    )\n                    final = {\n                        k: tuple(clamp255(v) for v in c)\n                        for k, c in final.items()\n                    }\n''',
    "renderer reactive/brightness order",
)
p.write_text(s, encoding="utf-8")


# 4) The reactive ColorDialog used a live binding to controller.reactiveColor.
# stateChanged fires frequently, so the binding could reset the user's in-dialog
# selection back to the old (usually white) value. Initialize only on open.
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


# 5) Version and changelog.
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

print("BladeRGB 1.1.1 patch applied")
