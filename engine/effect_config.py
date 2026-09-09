PALETTE_SIZE = 8


def slider(key, label, minimum, maximum, step, default, decimals=2, suffix=""):
    return {
        "key": key,
        "label": label,
        "min": float(minimum),
        "max": float(maximum),
        "step": float(step),
        "default": float(default),
        "decimals": int(decimals),
        "suffix": suffix,
    }


EFFECT_PARAMETER_SCHEMA = {
    "Static": [],
    "Gradient": [
        slider("gradient_repeat", "Повтор градиента", 0.25, 4.0, 0.05, 1.0),
        slider("gradient_offset", "Смещение цветов", 0.0, 1.0, 0.01, 0.0),
    ],
    "Rainbow": [
        slider("rainbow_saturation", "Насыщенность", 0.15, 1.0, 0.01, 0.95),
        slider("rainbow_width", "Ширина спектра", 0.2, 2.5, 0.05, 1.0),
        slider("hue_shift", "Сдвиг оттенка", 0.0, 1.0, 0.01, 0.0),
    ],
    "Aurora": [
        slider("aurora_detail", "Детализация", 0.3, 3.0, 0.05, 1.0),
        slider("aurora_glow", "Мягкое свечение", 0.0, 1.0, 0.01, 0.68),
        slider("aurora_drift", "Дрейф", 0.1, 2.5, 0.05, 1.0),
    ],
    "Plasma": [
        slider("plasma_detail", "Детализация", 0.35, 3.0, 0.05, 1.0),
        slider("plasma_warp", "Искажение", 0.0, 2.5, 0.05, 1.0),
    ],
    "Wave": [
        slider("wave_frequency", "Частота волн", 0.4, 6.0, 0.05, 2.0),
        slider("wave_sharpness", "Резкость фронта", 0.4, 6.0, 0.05, 1.0),
    ],
    "Radial": [
        slider("radial_density", "Плотность колец", 0.4, 5.0, 0.05, 1.6),
        slider("center_x", "Центр по горизонтали", 0.0, 1.0, 0.01, 0.5),
        slider("center_y", "Центр по вертикали", 0.0, 1.0, 0.01, 0.5),
    ],
    "Scanner": [
        slider("scanner_width", "Ширина луча", 0.01, 0.20, 0.005, 0.035, 3),
        slider("scanner_glow", "Свечение луча", 0.1, 1.0, 0.01, 1.0),
    ],
    "Twinkle": [
        slider("twinkle_density", "Плотность искр", 0.2, 3.0, 0.05, 1.0),
        slider("twinkle_sharpness", "Резкость искр", 2.0, 20.0, 0.5, 8.0, 1),
        slider("twinkle_floor", "Фоновое свечение", 0.0, 0.5, 0.01, 0.16),
    ],
    "Fire": [
        slider("fire_turbulence", "Турбулентность", 0.2, 3.0, 0.05, 1.0),
        slider("fire_height", "Высота пламени", 0.25, 1.5, 0.05, 0.9),
    ],
    "Ocean": [
        slider("ocean_chop", "Волнение", 0.2, 3.0, 0.05, 1.0),
        slider("ocean_depth", "Глубина цвета", 0.25, 1.5, 0.05, 1.0),
    ],
    "Matrix": [
        slider("matrix_trail", "Длина шлейфа", 0.08, 0.9, 0.01, 0.42),
        slider("matrix_density", "Плотность потоков", 0.35, 2.0, 0.05, 1.0),
    ],
    "Breathing": [
        slider("breathing_min", "Минимальная яркость", 0.0, 0.5, 0.01, 0.08),
        slider("breathing_curve", "Характер дыхания", 0.5, 4.0, 0.05, 1.0),
    ],
    "Color Cycle": [
        slider("cycle_softness", "Плавность перехода", 0.2, 3.0, 0.05, 1.0),
    ],
    "Neon Flow": [
        slider("flow_twist", "Изгиб потока", 0.0, 5.0, 0.05, 1.6),
        slider("flow_width", "Ширина лент", 0.3, 4.0, 0.05, 1.35),
    ],
    "Lava Lamp": [
        slider("lava_blob_size", "Размер пузырей", 0.06, 0.35, 0.01, 0.17),
        slider("lava_contrast", "Контраст пузырей", 0.5, 4.0, 0.05, 1.8),
    ],
    "Comet": [
        slider("comet_width", "Размер ядра", 0.015, 0.18, 0.005, 0.055, 3),
        slider("comet_tail", "Длина хвоста", 0.05, 0.8, 0.01, 0.32),
    ],
    "Pulse Rings": [
        slider("ring_count", "Количество колец", 1.0, 8.0, 0.25, 3.0, 2),
        slider("ring_width", "Толщина колец", 0.015, 0.18, 0.005, 0.06, 3),
        slider("center_x", "Центр по горизонтали", 0.0, 1.0, 0.01, 0.5),
        slider("center_y", "Центр по вертикали", 0.0, 1.0, 0.01, 0.5),
    ],
    "Dual Wave": [
        slider("dual_mix", "Баланс волн", 0.0, 1.0, 0.01, 0.5),
        slider("wave_frequency", "Частота волн", 0.4, 6.0, 0.05, 2.0),
        slider("wave_sharpness", "Резкость фронта", 0.4, 6.0, 0.05, 1.0),
    ],
    "Screen Ambilight": [
        slider("screen_saturation", "Насыщенность экрана", 0.0, 2.0, 0.05, 1.0),
        slider("screen_gain", "Усиление цвета", 0.25, 2.0, 0.05, 1.0),
    ],
    "Screen Average": [
        slider("screen_saturation", "Насыщенность экрана", 0.0, 2.0, 0.05, 1.0),
        slider("screen_gain", "Усиление цвета", 0.25, 2.0, 0.05, 1.0),
    ],
    "Screen Edge": [
        slider("screen_saturation", "Насыщенность экрана", 0.0, 2.0, 0.05, 1.0),
        slider("screen_gain", "Усиление цвета", 0.25, 2.0, 0.05, 1.0),
    ],
}

EFFECT_PARAM_DEFAULTS = {
    item["key"]: item["default"]
    for items in EFFECT_PARAMETER_SCHEMA.values()
    for item in items
}
EFFECT_PARAM_KEYS = set(EFFECT_PARAM_DEFAULTS)


PALETTE_PRESETS = {
    "Northern": {
        "label": "Северное сияние",
        "colors": ["#06141f", "#0b3142", "#0f766e", "#2dd4bf", "#67e8f9", "#7c83fd", "#b794f4", "#e9d5ff"],
    },
    "Sunset": {
        "label": "Тёплый закат",
        "colors": ["#22092c", "#4a1942", "#893168", "#da4167", "#f26b38", "#f59e0b", "#ffd166", "#fff1c1"],
    },
    "Ice": {
        "label": "Лёд",
        "colors": ["#071a2b", "#0b3558", "#0e7490", "#22d3ee", "#67e8f9", "#bae6fd", "#dbeafe", "#f8fafc"],
    },
    "Ember": {
        "label": "Угли",
        "colors": ["#120606", "#350b0b", "#741414", "#b91c1c", "#ea580c", "#f59e0b", "#facc15", "#fef3c7"],
    },
    "Ocean": {
        "label": "Глубокий океан",
        "colors": ["#020617", "#082f49", "#0c4a6e", "#0369a1", "#0284c7", "#06b6d4", "#2dd4bf", "#99f6e4"],
    },
    "Sakura": {
        "label": "Сакура",
        "colors": ["#2a1428", "#52213f", "#7c2d5b", "#be4778", "#ec6f9e", "#f9a8d4", "#fbcfe8", "#fff1f6"],
    },
    "Forest": {
        "label": "Лес",
        "colors": ["#07130d", "#0b2b1b", "#14532d", "#15803d", "#22c55e", "#4ade80", "#86efac", "#d1fae5"],
    },
    "Vapor": {
        "label": "Vaporwave",
        "colors": ["#10002b", "#240046", "#5a189a", "#9d4edd", "#c77dff", "#ff4dbe", "#00d4ff", "#7df9ff"],
    },
    "Candy": {
        "label": "Конфетная",
        "colors": ["#ff5d8f", "#ff87ab", "#ffc2d1", "#ffe5ec", "#bde0fe", "#a2d2ff", "#cdb4db", "#b8c0ff"],
    },
    "Mono": {
        "label": "Монохром",
        "colors": ["#050505", "#121212", "#242424", "#3a3a3a", "#5c5c5c", "#858585", "#b8b8b8", "#f3f3f3"],
    },
}


EXTRA_PRESETS = {
    "Neon River": {
        "effect": "Neon Flow",
        "palette": PALETTE_PRESETS["Vapor"]["colors"],
        "params": {"speed": 0.72, "scale": 1.25, "brightness": 0.72, "angle": 18, "flow_twist": 1.9, "flow_width": 1.4},
    },
    "Calm Lava": {
        "effect": "Lava Lamp",
        "palette": ["#130f20", "#2c183d", "#5b235c", "#9a3469", "#d35462", "#ef7b5a", "#f4b66f", "#ffe7ad"],
        "params": {"speed": 0.38, "scale": 1.0, "brightness": 0.66, "lava_blob_size": 0.19, "lava_contrast": 1.7},
    },
    "Blue Comet": {
        "effect": "Comet",
        "palette": ["#020617", "#082f49", "#0c4a6e", "#0369a1", "#0ea5e9", "#38bdf8", "#bae6fd", "#ffffff"],
        "params": {"speed": 0.9, "scale": 1.0, "brightness": 0.78, "angle": 0, "comet_width": 0.05, "comet_tail": 0.38},
    },
    "Soft Rings": {
        "effect": "Pulse Rings",
        "palette": PALETTE_PRESETS["Northern"]["colors"],
        "params": {"speed": 0.55, "scale": 1.0, "brightness": 0.7, "ring_count": 3.4, "ring_width": 0.075},
    },
    "Crossing Waves": {
        "effect": "Dual Wave",
        "palette": PALETTE_PRESETS["Sakura"]["colors"],
        "params": {"speed": 0.62, "scale": 1.1, "brightness": 0.68, "angle": 25, "dual_mix": 0.5, "wave_frequency": 2.2, "wave_sharpness": 1.2},
    },
}
