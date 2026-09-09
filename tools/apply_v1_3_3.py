from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"Patch point not found: {label}")
    return text.replace(old, new, 1)


# Effects: when palette hold timing is enabled, effects must not also perform
# their own continuous palette drift. Geometry/motion may continue, but the
# palette phase is controlled only by the renderer's hold/crossfade clock.
p = ROOT / "engine/effects.py"
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    "from .colors import hsv, palette_sample, multiply, clamp01, mix\n",
    "from .colors import hsv, palette_sample, multiply, clamp01, mix\nfrom .palette_timing import automatic_palette_phase\n",
    "palette timing import",
)

s = replace_once(
    s,
    '''                + t * p["speed"] * 0.16\n                + offset,\n''',
    '''                + automatic_palette_phase(t * p["speed"] * 0.16, p)\n                + offset,\n''',
    "Gradient palette drift",
)

s = replace_once(
    s,
    '''            base = palette_sample(palette, (x + y + t * speed * 0.04) % 1)\n''',
    '''            color_drift = automatic_palette_phase(t * speed * 0.04, p)\n            base = palette_sample(palette, (x + y + color_drift) % 1)\n''',
    "Twinkle palette drift",
)

s = replace_once(
    s,
    '''        c = multiply(palette_sample(palette, t * p["speed"] * 0.06), v)\n''',
    '''        color_position = automatic_palette_phase(t * p["speed"] * 0.06, p)\n        c = multiply(palette_sample(palette, color_position), v)\n''',
    "Breathing palette drift",
)

s = replace_once(
    s,
    '''        position = t * p["speed"] * 0.08\n        c = palette_sample(palette, position / softness)\n''',
    '''        position = automatic_palette_phase(t * p["speed"] * 0.08, p)\n        c = palette_sample(palette, position / softness)\n''',
    "Color Cycle palette drift",
)

s = replace_once(
    s,
    '''            pos = q * width + bend + t * speed * 0.12\n            ribbon = 0.5 + 0.5 * math.sin(pos * math.pi * 2.0)\n            glow = 0.62 + 0.38 * (ribbon ** 2)\n            out[k] = multiply(palette_sample(palette, pos), glow)\n''',
    '''            motion_pos = q * width + bend + t * speed * 0.12\n            color_pos = q * width + bend + automatic_palette_phase(\n                t * speed * 0.12, p\n            )\n            ribbon = 0.5 + 0.5 * math.sin(motion_pos * math.pi * 2.0)\n            glow = 0.62 + 0.38 * (ribbon ** 2)\n            out[k] = multiply(palette_sample(palette, color_pos), glow)\n''',
    "Neon Flow palette drift",
)

p.write_text(s, encoding="utf-8")


# Renderer: keep one palette clock implementation and delegate cycle math to a
# small tested pure function.
p = ROOT / "engine/renderer.py"
s = p.read_text(encoding="utf-8")
s = replace_once(
    s,
    "from .reactive import ReactiveInput\n",
    "from .reactive import ReactiveInput\nfrom .palette_timing import palette_cycle_position\n",
    "renderer palette timing import",
)

old = '''        elapsed = max(0.0, float(now) - state["anchor"])\n        segment = hold_time + transition_time\n        step = int(elapsed // segment)\n        local = elapsed - step * segment\n\n        if local < hold_time:\n            blend = 0.0\n        else:\n            blend = (local - hold_time) / transition_time\n            blend = max(0.0, min(1.0, blend))\n            # Smoothstep removes visible speed jumps at both ends.\n            blend = blend * blend * (3.0 - 2.0 * blend)\n\n        index = step % len(palette)\n        next_index = (index + 1) % len(palette)\n'''
new = '''        elapsed = max(0.0, float(now) - state["anchor"])\n        index, next_index, blend = palette_cycle_position(\n            elapsed,\n            len(palette),\n            hold_time,\n            transition_time,\n        )\n'''
s = replace_once(s, old, new, "renderer palette cycle math")
p.write_text(s, encoding="utf-8")


# Add deterministic unit-style tests. These run without HID/Qt dependencies.
p = ROOT / "test_palette_timing.py"
p.write_text(
    '''from engine.palette_timing import (\n    automatic_palette_phase,\n    palette_cycle_position,\n)\n\n\ndef close(a, b, eps=1e-6):\n    assert abs(a - b) <= eps, (a, b)\n\n\n# 2s hold + 1s transition.\ni, n, blend = palette_cycle_position(0.0, 3, 2.0, 1.0)\nassert (i, n) == (0, 1)\nclose(blend, 0.0)\n\ni, n, blend = palette_cycle_position(1.999, 3, 2.0, 1.0)\nassert (i, n) == (0, 1)\nclose(blend, 0.0)\n\ni, n, blend = palette_cycle_position(2.5, 3, 2.0, 1.0)\nassert (i, n) == (0, 1)\nclose(blend, 0.5)\n\ni, n, blend = palette_cycle_position(3.0, 3, 2.0, 1.0)\nassert (i, n) == (1, 2)\nclose(blend, 0.0)\n\ni, n, blend = palette_cycle_position(6.0, 3, 2.0, 1.0)\nassert (i, n) == (2, 0)\nclose(blend, 0.0)\n\n# An enabled palette hold disables a second, effect-local color clock.\nassert automatic_palette_phase(12.5, {"palette_delay": 2.0}) == 0.0\nassert automatic_palette_phase(12.5, {"palette_delay": 0.0}) == 12.5\n\nprint("palette timing tests: OK")\n''',
    encoding="utf-8",
)


# CI should now verify timing behavior, not only syntax.
p = ROOT / ".github/workflows/check.yml"
s = p.read_text(encoding="utf-8")
if "Palette timing tests" not in s:
    s += '''      - name: Palette timing tests\n        run: python test_palette_timing.py\n'''
p.write_text(s, encoding="utf-8")


# Version/docs.
(ROOT / "VERSION.txt").write_text(
    "BladeRGB 1.3.3 RU\n"
    "Palette hold fix: single color clock + deterministic timing tests\n",
    encoding="utf-8",
)

p = ROOT / "README.md"
s = p.read_text(encoding="utf-8")
notes = '''## 1.3.3 — реальная пауза между цветами\n\n- исправлена главная причина, из-за которой пауза палитры визуально не работала: часть эффектов продолжала самостоятельно прокручивать цвет по времени;\n- при включённой паузе теперь используется один источник тайминга палитры — `пауза → переход → следующий цвет`;\n- убран второй цветовой таймер у Gradient, Twinkle, Breathing, Color Cycle и Neon Flow;\n- движение/геометрия Neon Flow остаются живыми, но смена цвета подчиняется отдельному таймеру палитры;\n- тайминг вынесен в чистый модуль `engine/palette_timing.py`;\n- CI теперь проверяет не только синтаксис, но и реальные контрольные точки паузы/перехода.\n\n'''
if "## 1.3.3 —" not in s:
    s = notes + s
s = s.replace("Текущая версия: **1.3.2 RU**", "Текущая версия: **1.3.3 RU**")
p.write_text(s, encoding="utf-8")

print("BladeRGB 1.3.3 patch applied")
