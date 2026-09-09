from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"Patch point not found: {label}")
    return text.replace(old, new, 1)


# -----------------------------------------------------------------------------
# Renderer: make palette_delay a real HOLD duration and give transitions their
# own duration. Each palette (main/layer) gets an independent deterministic
# cycle anchored when its palette/timing configuration changes.
# -----------------------------------------------------------------------------
p = ROOT / "engine/renderer.py"
s = p.read_text(encoding="utf-8")

s = replace_once(
    s,
    "'overlay_opacity': 1.0, 'palette_delay': 0.0}",
    "'overlay_opacity': 1.0, 'palette_delay': 0.0, 'palette_transition': 0.6}",
    "DEFAULT_PARAMS palette transition",
)

s = replace_once(
    s,
    "        self._layer_effects = {}\n",
    "        self._layer_effects = {}\n        self._palette_cycle_states = {}\n",
    "palette state storage",
)

old_func = '''    def _palette_with_delay(self, palette, now, delay):
        if len(palette) < 2:
            return palette
        try: delay = float(delay)
        except Exception: return palette
        if delay <= 0.0:
            return palette
        delay = max(0.10, delay)
        phase = now / delay
        whole = math.floor(phase)
        index = int(whole) % len(palette)
        fraction = phase - whole
        hold = 0.72
        if fraction <= hold:
            blend = 0.0
        else:
            blend = (fraction - hold) / (1.0 - hold)
            blend = blend * blend * (3.0 - 2.0 * blend)
        current = palette[index:] + palette[:index]
        next_index = (index + 1) % len(palette)
        following = palette[next_index:] + palette[:next_index]
        return [mix(a, b, blend) for a, b in zip(current, following)]
'''

new_func = '''    def _palette_with_delay(self, palette, now, delay, transition=0.6, key="main"):
        """Rotate the palette using a predictable hold -> crossfade cycle.

        `delay` is the exact time the current palette position is held.
        `transition` is a separate crossfade duration. The cycle starts at the
        first palette position whenever colors or timing settings change.
        """
        if len(palette) < 2:
            self._palette_cycle_states.pop(str(key), None)
            return palette

        try:
            delay = float(delay)
            transition = float(transition)
        except Exception:
            self._palette_cycle_states.pop(str(key), None)
            return palette

        if delay <= 0.0:
            self._palette_cycle_states.pop(str(key), None)
            return palette

        hold_time = max(0.05, delay)
        transition_time = max(0.05, min(5.0, transition))
        cycle_key = str(key)
        signature = tuple(
            tuple(int(round(channel)) for channel in color)
            for color in palette
        )
        settings = (
            signature,
            round(hold_time, 4),
            round(transition_time, 4),
        )

        state = self._palette_cycle_states.get(cycle_key)
        if state is None or state.get("settings") != settings:
            state = {
                "settings": settings,
                "anchor": float(now),
            }
            self._palette_cycle_states[cycle_key] = state

        elapsed = max(0.0, float(now) - state["anchor"])
        segment = hold_time + transition_time
        step = int(elapsed // segment)
        local = elapsed - step * segment

        if local < hold_time:
            blend = 0.0
        else:
            blend = (local - hold_time) / transition_time
            blend = max(0.0, min(1.0, blend))
            # Smoothstep removes visible speed jumps at both ends.
            blend = blend * blend * (3.0 - 2.0 * blend)

        index = step % len(palette)
        next_index = (index + 1) % len(palette)
        current = palette[index:] + palette[:index]
        following = palette[next_index:] + palette[:next_index]
        return [mix(a, b, blend) for a, b in zip(current, following)]
'''

s = replace_once(s, old_func, new_func, "palette timing implementation")

s = replace_once(
    s,
    "            palette=self._palette_with_delay(palette,now,p.get('palette_delay',0.0))\n",
    "            palette=self._palette_with_delay(\n                palette,\n                now,\n                p.get('palette_delay', 0.0),\n                p.get('palette_transition', 0.6),\n                key=f'layer:{layer.id}',\n            )\n",
    "layer palette timing",
)

s = replace_once(
    s,
    "                palette=self._palette_with_delay(palette,start,p.get('palette_delay',0.0))\n",
    "                palette=self._palette_with_delay(\n                    palette,\n                    start,\n                    p.get('palette_delay', 0.0),\n                    p.get('palette_transition', 0.6),\n                    key='main',\n                )\n",
    "main palette timing",
)

p.write_text(s, encoding="utf-8")


# -----------------------------------------------------------------------------
# Dashboard: make FPS explicit and expose independent transition duration.
# -----------------------------------------------------------------------------
p = ROOT / "qml/pages/Dashboard.qml"
s = p.read_text(encoding="utf-8")

s = replace_once(
    s,
    '''                        label: "Частота обновления"
                        from: 15
''',
    '''                        label: "FPS (лимит)"
                        from: 10
''',
    "FPS label/range",
)

s = replace_once(
    s,
    '''                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Задержка перехода к следующему цвету"
                        from: 0
                        to: 8
                        stepSize: 0.1
                        decimals: 1
                        suffix: " с"
                        value: controller.params.palette_delay || 0
                        onChanged: controller.setParam("palette_delay", value)
                    }

                    RowLayout {
''',
    '''                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Пауза на каждом цвете"
                        from: 0
                        to: 8
                        stepSize: 0.1
                        decimals: 1
                        suffix: " с"
                        value: controller.params.palette_delay || 0
                        onChanged: controller.setParam("palette_delay", value)
                    }

                    MetricSlider {
                        Layout.fillWidth: true
                        label: "Длительность перехода"
                        from: 0.1
                        to: 3
                        stepSize: 0.05
                        decimals: 2
                        suffix: " с"
                        value: controller.params.palette_transition === undefined
                            ? 0.6
                            : controller.params.palette_transition
                        onChanged: controller.setParam("palette_transition", value)
                    }

                    Text {
                        Layout.fillWidth: true
                        text: controller.params.palette_delay > 0
                            ? "Цикл: пауза → плавный переход → следующий цвет"
                            : "0 с — дополнительная задержка палитры отключена"
                        color: Theme.textSubtle
                        font.pixelSize: 8
                    }

                    RowLayout {
''',
    "palette timing controls",
)

# More vertical room for the extra transition slider.
s = s.replace("Layout.preferredHeight: 410", "Layout.preferredHeight: 475")

p.write_text(s, encoding="utf-8")


# -----------------------------------------------------------------------------
# Version / README.
# -----------------------------------------------------------------------------
(ROOT / "VERSION.txt").write_text(
    "BladeRGB 1.3.2 RU\n"
    "Deterministic palette hold/crossfade timing + explicit FPS control\n",
    encoding="utf-8",
)

p = ROOT / "README.md"
s = p.read_text(encoding="utf-8")
notes = '''## 1.3.2 — корректный тайминг палитры и FPS\n\n- параметр задержки палитры теперь означает реальное время удержания каждого цвета;\n- переход к следующему цвету получил отдельную регулируемую длительность;\n- цикл палитры начинается детерминированно и больше не зависит от `perf_counter()` / времени работы системы;\n- основная палитра и палитры отдельных слоёв имеют независимые циклы;\n- изменение цветов или тайминга корректно перезапускает цикл с текущей палитры;\n- в «Основных параметрах» явно возвращён `FPS (лимит)` с диапазоном 10–60 кадров/с;\n- фактический FPS по-прежнему отображается над предпросмотром клавиатуры.\n\n'''
if "## 1.3.2 —" not in s:
    s = notes + s
s = s.replace("Текущая версия: **1.3.0 RU**", "Текущая версия: **1.3.2 RU**")
s = s.replace("Текущая версия: **1.3.1 RU**", "Текущая версия: **1.3.2 RU**")
p.write_text(s, encoding="utf-8")

print("BladeRGB 1.3.2 patch applied")
