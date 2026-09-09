from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def must_replace(text, old, new, label, count=1):
    if old not in text:
        raise RuntimeError(f"Patch point not found: {label}")
    return text.replace(old, new, count)


# ---------------------------------------------------------------------------
# Renderer: register effect-specific parameters and additional presets.
# ---------------------------------------------------------------------------
p = ROOT / "engine/renderer.py"
s = p.read_text(encoding="utf-8")

s = must_replace(
    s,
    "from .layers import Layer\n",
    "from .layers import Layer\nfrom .effect_config import EFFECT_PARAM_DEFAULTS, EXTRA_PRESETS\n",
    "renderer config import",
)

marker = "BUILTIN_PRESETS = "
if marker not in s:
    raise RuntimeError("BUILTIN_PRESETS not found")

s = must_replace(
    s,
    "\n\nclass Renderer:\n",
    "\n\nDEFAULT_PARAMS.update(EFFECT_PARAM_DEFAULTS)\nBUILTIN_PRESETS.update(EXTRA_PRESETS)\n\n\nclass Renderer:\n",
    "renderer defaults/presets",
)

p.write_text(s, encoding="utf-8")


# ---------------------------------------------------------------------------
# Controller: Russian labels, 8-color palettes and dynamic effect controls.
# ---------------------------------------------------------------------------
p = ROOT / "app/controller.py"
s = p.read_text(encoding="utf-8")

s = must_replace(
    s,
    "from engine.effects import EFFECTS\n",
    "from engine.effects import EFFECTS\nfrom engine.effect_config import (\n    EFFECT_PARAMETER_SCHEMA, EFFECT_PARAM_DEFAULTS, PALETTE_PRESETS, PALETTE_SIZE\n)\n",
    "controller config import",
)

s = must_replace(
    s,
    '    "Screen Average": "Средний цвет экрана", "Screen Edge": "Цвета по краям экрана",\n',
    '    "Screen Average": "Средний цвет экрана", "Screen Edge": "Цвета по краям экрана",\n'
    '    "Neon Flow": "Неоновый поток", "Lava Lamp": "Лава-лампа", "Comet": "Комета",\n'
    '    "Pulse Rings": "Пульсирующие кольца", "Dual Wave": "Двойная волна",\n',
    "effect labels",
)

s = must_replace(
    s,
    '    "Scanner Red": "Красный сканер", "Twinkle Night": "Ночное мерцание", "Screen": "Экран",\n',
    '    "Scanner Red": "Красный сканер", "Twinkle Night": "Ночное мерцание", "Screen": "Экран",\n'
    '    "Neon River": "Неоновая река", "Calm Lava": "Спокойная лава",\n'
    '    "Blue Comet": "Синяя комета", "Soft Rings": "Мягкие кольца",\n'
    '    "Crossing Waves": "Пересекающиеся волны",\n',
    "preset labels",
)

s = must_replace(
    s,
    '        self._palette = ["#10002b", "#3c096c", "#7b2cbf", "#c77dff", "#4cc9f0"]\n',
    '        self._palette = list(PALETTE_PRESETS["Northern"]["colors"])\n',
    "initial palette",
)

property_anchor = '''    @Property("QVariantList", constant=True)\n    def easingItems(self): return _ui_items(EASING_LABELS.keys(), EASING_LABELS)\n'''
property_new = property_anchor + '''    @Property("QVariantList", notify=stateChanged)\n    def effectParameterItems(self):\n        return list(EFFECT_PARAMETER_SCHEMA.get(self.renderer.effect_name, []))\n    @Property("QVariantList", constant=True)\n    def palettePresetItems(self):\n        return [\n            {"value": key, "label": data["label"]}\n            for key, data in PALETTE_PRESETS.items()\n        ]\n'''
s = must_replace(s, property_anchor, property_new, "controller dynamic properties")

slot_anchor = '''    @Slot(int, str)\n    def setPaletteColor(self, index, value):\n        if index < 0: return\n        while len(self._palette) <= index: self._palette.append("#ffffff")\n        try:\n            self._palette[index]=rgb_to_hex(hex_to_rgb(value)); self.renderer.set_palette([hex_to_rgb(x) for x in self._palette]); self.stateChanged.emit()\n        except Exception: pass\n'''
slot_new = slot_anchor + '''    @Slot(str)\n    def applyPalettePreset(self, name):\n        data = PALETTE_PRESETS.get(str(name))\n        if not data: return\n        colors = list(data.get("colors", []))[:PALETTE_SIZE]\n        while len(colors) < PALETTE_SIZE:\n            colors.append(colors[-1] if colors else "#ffffff")\n        self._palette = [rgb_to_hex(hex_to_rgb(x)) for x in colors]\n        self.renderer.set_palette([hex_to_rgb(x) for x in self._palette])\n        self.stateChanged.emit()\n        self.toast.emit("Палитра применена", data.get("label", str(name)))\n    @Slot()\n    def resetEffectParameters(self):\n        for item in EFFECT_PARAMETER_SCHEMA.get(self.renderer.effect_name, []):\n            key = item.get("key")\n            if key in EFFECT_PARAM_DEFAULTS:\n                self.renderer.set_param(key, EFFECT_PARAM_DEFAULTS[key])\n        self.stateChanged.emit()\n'''
s = must_replace(s, slot_anchor, slot_new, "controller palette/effect slots")

# Replace every 5-color normalization from presets/profiles with 8-color normalization.
s = s.replace(
    'while len(palette)<5: palette.append(palette[-1] if palette else "#ffffff")\n        self._palette=palette[:5]',
    'while len(palette)<PALETTE_SIZE: palette.append(palette[-1] if palette else "#ffffff")\n        self._palette=palette[:PALETTE_SIZE]',
)
s = s.replace(
    'while len(palette)<5: palette.append(palette[-1] if palette else "#ffffff")\n        self._palette=[rgb_to_hex(hex_to_rgb(x)) for x in palette[:5]]',
    'while len(palette)<PALETTE_SIZE: palette.append(palette[-1] if palette else "#ffffff")\n        self._palette=[rgb_to_hex(hex_to_rgb(x)) for x in palette[:PALETTE_SIZE]]',
)

p.write_text(s, encoding="utf-8")


# ---------------------------------------------------------------------------
# Version / docs.
# ---------------------------------------------------------------------------
(ROOT / "VERSION.txt").write_text(
    "BladeRGB 1.2.0 RU\nEffects Lab: flexible parameters, 8-color palettes and new effects\n",
    encoding="utf-8",
)

p = ROOT / "README.md"
s = p.read_text(encoding="utf-8")
s = s.replace("Текущая версия: **1.1.1**", "Текущая версия: **1.2.0**")
notes = '''## 1.2.0 — Effects Lab\n\n- палитра основной подсветки расширена с 5 до 8 цветов;\n- добавлены готовые палитры: Северное сияние, Закат, Лёд, Угли, Океан, Сакура, Лес, Vaporwave, Конфетная и Монохром;\n- эффекты получили индивидуальные параметры: детализация, ширина, плотность, насыщенность, турбулентность, положение центра и другие;\n- новые эффекты: Неоновый поток, Лава-лампа, Комета, Пульсирующие кольца и Двойная волна;\n- добавлены готовые сцены для новых эффектов;\n- старые профили 1.1.x остаются совместимыми — недостающие цвета и параметры дополняются автоматически.\n\n'''
if "## 1.2.0 — Effects Lab" not in s:
    s = notes + s
p.write_text(s, encoding="utf-8")

print("BladeRGB 1.2.0 backend patch applied")
