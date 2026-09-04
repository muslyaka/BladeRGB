import math
import time

from blade.layout import NORMALIZED_CENTERS
from .colors import hsv, palette_sample, multiply, clamp01, mix


class Effect:
    name = "Effect"
    def render(self, t, palette, p):
        raise NotImplementedError
    def close(self):
        pass


class StaticEffect(Effect):
    name = "Static"
    def render(self, t, palette, p):
        c = palette[0]
        return {k: c for k in NORMALIZED_CENTERS}


class GradientEffect(Effect):
    name = "Gradient"
    def render(self, t, palette, p):
        a = math.radians(p["angle"])
        dx, dy = math.cos(a), math.sin(a)
        return {
            k: palette_sample(
                palette,
                (x * dx + y * dy) * p["scale"] + t * p["speed"] * 0.16
            )
            for k, (x, y) in NORMALIZED_CENTERS.items()
        }


class RainbowEffect(Effect):
    name = "Rainbow"
    def render(self, t, palette, p):
        a = math.radians(p["angle"])
        dx, dy = math.cos(a), math.sin(a)
        return {
            k: hsv(
                (x * dx + y * dy) * 0.35 * p["scale"] + t * p["speed"] * 0.08,
                0.95, 1.0
            )
            for k, (x, y) in NORMALIZED_CENTERS.items()
        }


class AuroraEffect(Effect):
    name = "Aurora"
    def render(self, t, palette, p):
        s = max(0.05, p["scale"])
        tt = t * p["speed"]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            a = math.sin(x * 5.4 * s + tt * 0.65)
            b = math.sin(y * 7.1 * s - tt * 0.47 + x * 2.2)
            c = math.sin((x + y) * 4.2 * s + tt * 0.31)
            v = (a + b + c) / 6.0 + 0.5
            glow = 0.68 + 0.32 * (0.5 + 0.5 * math.sin(y * 7 - tt * 0.3))
            out[k] = multiply(palette_sample(palette, v), glow)
        return out


class PlasmaEffect(Effect):
    name = "Plasma"
    def render(self, t, palette, p):
        s = max(0.05, p["scale"])
        tt = t * p["speed"]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            v1 = math.sin(x * 12 * s + tt)
            v2 = math.sin(y * 10 * s - tt * 1.17)
            v3 = math.sin((x + y) * 8 * s + tt * 0.73)
            v4 = math.sin(math.hypot(x - 0.5, y - 0.5) * 18 * s - tt)
            out[k] = palette_sample(palette, (v1 + v2 + v3 + v4) / 8 + 0.5)
        return out


class WaveEffect(Effect):
    name = "Wave"
    def render(self, t, palette, p):
        a = math.radians(p["angle"])
        dx, dy = math.cos(a), math.sin(a)
        s = max(0.05, p["scale"])
        tt = t * p["speed"]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            q = x * dx + y * dy
            v = 0.5 + 0.5 * math.sin(q * math.pi * 4 * s - tt * 2.1)
            out[k] = palette_sample(palette, v, wrap=False)
        return out


class RadialEffect(Effect):
    name = "Radial"
    def render(self, t, palette, p):
        s = max(0.05, p["scale"])
        tt = t * p["speed"]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            d = math.hypot((x - 0.5) * 1.65, y - 0.5)
            out[k] = palette_sample(palette, d * 1.6 * s - tt * 0.22)
        return out


class ScannerEffect(Effect):
    name = "Scanner"
    def render(self, t, palette, p):
        a = math.radians(p["angle"])
        dx, dy = math.cos(a), math.sin(a)
        pos2 = (t * p["speed"] * 0.22) % 2.0
        pos = pos2 if pos2 <= 1 else 2 - pos2
        base = palette[0] if palette else (4, 4, 8)
        head = palette[-1] if palette else (255, 0, 0)
        out = {}
        width = 0.035 / max(0.3, p["scale"])
        for k, (x, y) in NORMALIZED_CENTERS.items():
            q = (x * dx + y * dy + 1) / 2
            d = abs(q - pos)
            glow = math.exp(-(d * d) / (2 * width * width))
            out[k] = mix(multiply(base, 0.12), head, glow)
        return out


class TwinkleEffect(Effect):
    name = "Twinkle"
    def render(self, t, palette, p):
        speed = max(0.1, p["speed"])
        out = {}
        for idx, (k, (x, y)) in enumerate(NORMALIZED_CENTERS.items()):
            phase = (idx * 0.61803398875) % 1
            pulse = max(0.0, math.sin((t * speed * 0.9 + phase) * math.pi * 2))
            pulse = pulse ** 8
            base = palette_sample(palette, (x + y + t * speed * 0.04) % 1)
            star = palette[-1] if palette else (255, 255, 255)
            out[k] = mix(multiply(base, 0.16), star, pulse)
        return out


class FireEffect(Effect):
    name = "Fire"
    def render(self, t, palette, p):
        tt = t * p["speed"]
        s = p["scale"]
        pal = palette if len(palette) >= 2 else [
            (20, 0, 0), (255, 60, 0), (255, 220, 60)
        ]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            f = (
                math.sin(x * 29 * s + tt * 5.1)
                + math.sin(x * 11 * s - tt * 3.7 + y * 9)
                + math.sin((x + y) * 17 * s + tt * 2.9)
            ) / 9
            heat = clamp01((1 - y) * 0.9 + 0.18 + f)
            out[k] = palette_sample(pal, heat, False)
        return out


class OceanEffect(Effect):
    name = "Ocean"
    def render(self, t, palette, p):
        tt = t * p["speed"]
        s = p["scale"]
        pal = palette if len(palette) >= 2 else [
            (0, 20, 70), (0, 120, 255), (60, 255, 230)
        ]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            w = (
                math.sin((x * 9 + y * 4) * s - tt * 1.3)
                + 0.6 * math.sin((x * 17 - y * 6) * s + tt * 0.83)
            )
            out[k] = palette_sample(pal, w / 3.2 + 0.5, False)
        return out


class MatrixEffect(Effect):
    name = "Matrix"
    def render(self, t, palette, p):
        tt = t * max(0.1, p["speed"])
        s = max(0.1, p["scale"])
        head = palette[-1] if palette else (180, 255, 180)
        trail = palette[0] if palette else (0, 80, 0)
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            col = int(x * 28)
            phase = (col * 0.38196601125) % 1
            pos = (tt * (0.18 + (col % 5) * 0.015) + phase) % 1.35 - 0.15
            d = y - pos
            if -0.03 <= d <= 0.04:
                c = head
            elif 0.04 < d < 0.42 / s:
                power = max(0, 1 - d / (0.42 / s))
                c = multiply(trail, 0.15 + 0.85 * power)
            else:
                c = multiply(trail, 0.02)
            out[k] = c
        return out


class BreathingEffect(Effect):
    name = "Breathing"
    def render(self, t, palette, p):
        v = 0.08 + 0.92 * (
            0.5 + 0.5 * math.sin(t * max(0.05, p["speed"]) * math.pi)
        )
        c = multiply(palette_sample(palette, t * p["speed"] * 0.06), v)
        return {k: c for k in NORMALIZED_CENTERS}


class ColorCycleEffect(Effect):
    name = "Color Cycle"
    def render(self, t, palette, p):
        c = palette_sample(palette, t * p["speed"] * 0.08)
        return {k: c for k in NORMALIZED_CENTERS}


class _ScreenSampler:
    def __init__(self):
        self._mss = None
        self._np = None
        self._last = 0
        self._grid = None
        self.error = None

    def capture(self, fps=15):
        now = time.perf_counter()
        if self._grid is not None and now - self._last < 1 / max(1, fps):
            return self._grid

        self._last = now
        try:
            if self._mss is None:
                import mss
                import numpy as np
                self._mss = mss.mss()
                self._np = np

            mon = self._mss.monitors[1]
            arr = self._np.asarray(
                self._mss.grab(mon),
                dtype=self._np.uint8
            )[..., :3]

            h, w, _ = arr.shape
            ys = self._np.linspace(0, h - 1, 12).astype(int)
            xs = self._np.linspace(0, w - 1, 36).astype(int)
            self._grid = arr[ys][:, xs][:, :, ::-1]
            self.error = None
        except Exception as e:
            self.error = str(e)

        return self._grid

    def close(self):
        if self._mss:
            try:
                self._mss.close()
            except Exception:
                pass
        self._mss = None


class ScreenAmbilightEffect(Effect):
    name = "Screen Ambilight"
    def __init__(self):
        self.sampler = _ScreenSampler()
        self.error = None

    def render(self, t, palette, p):
        grid = self.sampler.capture(15)
        self.error = self.sampler.error
        if grid is None:
            return {k: (18, 18, 24) for k in NORMALIZED_CENTERS}

        gy, gx, _ = grid.shape
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            ix = max(0, min(gx - 1, int(x * (gx - 1))))
            iy = max(0, min(gy - 1, int(y * (gy - 1))))
            r, g, b = grid[iy, ix]
            out[k] = float(r), float(g), float(b)
        return out

    def close(self):
        self.sampler.close()


class ScreenAverageEffect(Effect):
    name = "Screen Average"
    def __init__(self):
        self.sampler = _ScreenSampler()
        self.error = None

    def render(self, t, palette, p):
        grid = self.sampler.capture(15)
        self.error = self.sampler.error
        if grid is None:
            c = (18, 18, 24)
        else:
            c = tuple(float(v) for v in grid.reshape(-1, 3).mean(axis=0))
        return {k: c for k in NORMALIZED_CENTERS}

    def close(self):
        self.sampler.close()


class ScreenEdgeEffect(Effect):
    name = "Screen Edge"
    def __init__(self):
        self.sampler = _ScreenSampler()
        self.error = None

    def render(self, t, palette, p):
        grid = self.sampler.capture(15)
        self.error = self.sampler.error
        if grid is None:
            return {k: (18, 18, 24) for k in NORMALIZED_CENTERS}

        gy, gx, _ = grid.shape
        edge = max(1, min(4, int(round(p.get("scale", 1.0) * 2))))
        left = grid[:, :edge].reshape(-1, 3).mean(axis=0)
        right = grid[:, -edge:].reshape(-1, 3).mean(axis=0)
        top = grid[:edge, :].reshape(-1, 3).mean(axis=0)
        bottom = grid[-edge:, :].reshape(-1, 3).mean(axis=0)

        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            wx_l = max(0, 1 - x * 2)
            wx_r = max(0, (x - 0.5) * 2)
            wy_t = max(0, 1 - y * 2)
            wy_b = max(0, (y - 0.5) * 2)
            weights = [wx_l, wx_r, wy_t, wy_b]
            colors = [left, right, top, bottom]
            total = sum(weights) or 1.0
            c = tuple(
                sum(colors[j][i] * weights[j] for j in range(4)) / total
                for i in range(3)
            )
            out[k] = c
        return out

    def close(self):
        self.sampler.close()


EFFECT_CLASSES = [
    StaticEffect,
    GradientEffect,
    RainbowEffect,
    AuroraEffect,
    PlasmaEffect,
    WaveEffect,
    RadialEffect,
    ScannerEffect,
    TwinkleEffect,
    FireEffect,
    OceanEffect,
    MatrixEffect,
    BreathingEffect,
    ColorCycleEffect,
    ScreenAmbilightEffect,
    ScreenAverageEffect,
    ScreenEdgeEffect,
]

EFFECTS = {cls.name: cls for cls in EFFECT_CLASSES}
