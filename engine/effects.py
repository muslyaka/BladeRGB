import math
import time

from blade.layout import NORMALIZED_CENTERS
from .colors import hsv, palette_sample, multiply, clamp01, mix
from .palette_timing import automatic_palette_phase


class Effect:
    name = "Effect"

    def render(self, t, palette, p):
        raise NotImplementedError

    def close(self):
        pass


def _screen_tune(color, p):
    r, g, b = (float(v) for v in color)
    gain = max(0.0, float(p.get("screen_gain", 1.0)))
    saturation = max(0.0, float(p.get("screen_saturation", 1.0)))
    gray = (r + g + b) / 3.0
    tuned = tuple((gray + (v - gray) * saturation) * gain for v in (r, g, b))
    return tuple(max(0.0, min(255.0, v)) for v in tuned)


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
        repeat = max(0.05, p.get("gradient_repeat", 1.0))
        offset = p.get("gradient_offset", 0.0)
        return {
            k: palette_sample(
                palette,
                ((x * dx + y * dy) * p["scale"] * repeat)
                + automatic_palette_phase(t * p["speed"] * 0.16, p)
                + offset,
            )
            for k, (x, y) in NORMALIZED_CENTERS.items()
        }


class RainbowEffect(Effect):
    name = "Rainbow"

    def render(self, t, palette, p):
        a = math.radians(p["angle"])
        dx, dy = math.cos(a), math.sin(a)
        saturation = clamp01(p.get("rainbow_saturation", 0.95))
        width = max(0.05, p.get("rainbow_width", 1.0))
        shift = p.get("hue_shift", 0.0)
        return {
            k: hsv(
                (x * dx + y * dy) * 0.35 * p["scale"] * width
                + t * p["speed"] * 0.08
                + shift,
                saturation,
                1.0,
            )
            for k, (x, y) in NORMALIZED_CENTERS.items()
        }


class AuroraEffect(Effect):
    name = "Aurora"

    def render(self, t, palette, p):
        detail = max(0.05, p.get("aurora_detail", 1.0))
        drift = max(0.05, p.get("aurora_drift", 1.0))
        glow_mix = clamp01(p.get("aurora_glow", 0.68))
        s = max(0.05, p["scale"]) * detail
        tt = t * p["speed"] * drift
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            a = math.sin(x * 5.4 * s + tt * 0.65)
            b = math.sin(y * 7.1 * s - tt * 0.47 + x * 2.2)
            c = math.sin((x + y) * 4.2 * s + tt * 0.31)
            v = (a + b + c) / 6.0 + 0.5
            pulse = 0.5 + 0.5 * math.sin(y * 7 - tt * 0.3)
            glow = (1.0 - glow_mix) + glow_mix * (0.55 + 0.45 * pulse)
            out[k] = multiply(palette_sample(palette, v), glow)
        return out


class PlasmaEffect(Effect):
    name = "Plasma"

    def render(self, t, palette, p):
        detail = max(0.05, p.get("plasma_detail", 1.0))
        warp = max(0.0, p.get("plasma_warp", 1.0))
        s = max(0.05, p["scale"]) * detail
        tt = t * p["speed"]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            bend = math.sin((x - y) * 7 * s + tt * 0.31) * 0.08 * warp
            xx, yy = x + bend, y - bend
            v1 = math.sin(xx * 12 * s + tt)
            v2 = math.sin(yy * 10 * s - tt * 1.17)
            v3 = math.sin((xx + yy) * 8 * s + tt * 0.73)
            v4 = math.sin(math.hypot(xx - 0.5, yy - 0.5) * 18 * s - tt)
            out[k] = palette_sample(palette, (v1 + v2 + v3 + v4) / 8 + 0.5)
        return out


class WaveEffect(Effect):
    name = "Wave"

    def render(self, t, palette, p):
        a = math.radians(p["angle"])
        dx, dy = math.cos(a), math.sin(a)
        s = max(0.05, p["scale"])
        freq = max(0.05, p.get("wave_frequency", 2.0))
        sharpness = max(0.1, p.get("wave_sharpness", 1.0))
        tt = t * p["speed"]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            q = x * dx + y * dy
            raw = 0.5 + 0.5 * math.sin(q * math.pi * 2 * freq * s - tt * 2.1)
            v = raw ** sharpness
            out[k] = palette_sample(palette, v, wrap=False)
        return out


class RadialEffect(Effect):
    name = "Radial"

    def render(self, t, palette, p):
        s = max(0.05, p["scale"])
        density = max(0.05, p.get("radial_density", 1.6))
        cx = clamp01(p.get("center_x", 0.5))
        cy = clamp01(p.get("center_y", 0.5))
        tt = t * p["speed"]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            d = math.hypot((x - cx) * 1.65, y - cy)
            out[k] = palette_sample(palette, d * density * s - tt * 0.22)
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
        width = max(0.004, p.get("scanner_width", 0.035)) / max(0.3, p["scale"])
        power = clamp01(p.get("scanner_glow", 1.0))
        for k, (x, y) in NORMALIZED_CENTERS.items():
            q = (x * dx + y * dy + 1) / 2
            d = abs(q - pos)
            glow = math.exp(-(d * d) / (2 * width * width)) * power
            out[k] = mix(multiply(base, 0.12), head, glow)
        return out


class TwinkleEffect(Effect):
    name = "Twinkle"

    def render(self, t, palette, p):
        speed = max(0.1, p["speed"])
        density = max(0.1, p.get("twinkle_density", 1.0))
        sharpness = max(1.0, p.get("twinkle_sharpness", 8.0))
        floor = clamp01(p.get("twinkle_floor", 0.16))
        out = {}
        for idx, (k, (x, y)) in enumerate(NORMALIZED_CENTERS.items()):
            phase = (idx * 0.61803398875 * density) % 1
            pulse = max(0.0, math.sin((t * speed * 0.9 + phase) * math.pi * 2))
            pulse = pulse ** sharpness
            pulse *= min(1.0, density)
            color_drift = automatic_palette_phase(t * speed * 0.04, p)
            base = palette_sample(palette, (x + y + color_drift) % 1)
            star = palette[-1] if palette else (255, 255, 255)
            out[k] = mix(multiply(base, floor), star, pulse)
        return out


class FireEffect(Effect):
    name = "Fire"

    def render(self, t, palette, p):
        tt = t * p["speed"]
        s = p["scale"] * max(0.1, p.get("fire_turbulence", 1.0))
        height = max(0.1, p.get("fire_height", 0.9))
        pal = palette if len(palette) >= 2 else [(20, 0, 0), (255, 60, 0), (255, 220, 60)]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            f = (
                math.sin(x * 29 * s + tt * 5.1)
                + math.sin(x * 11 * s - tt * 3.7 + y * 9)
                + math.sin((x + y) * 17 * s + tt * 2.9)
            ) / 9
            heat = clamp01((1 - y) * height + 0.18 + f)
            out[k] = palette_sample(pal, heat, False)
        return out


class OceanEffect(Effect):
    name = "Ocean"

    def render(self, t, palette, p):
        tt = t * p["speed"]
        chop = max(0.1, p.get("ocean_chop", 1.0))
        depth = max(0.1, p.get("ocean_depth", 1.0))
        s = p["scale"] * chop
        pal = palette if len(palette) >= 2 else [(0, 20, 70), (0, 120, 255), (60, 255, 230)]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            w = (
                math.sin((x * 9 + y * 4) * s - tt * 1.3)
                + 0.6 * math.sin((x * 17 - y * 6) * s + tt * 0.83)
            )
            sample = clamp01(0.5 + (w / 3.2) * depth)
            out[k] = palette_sample(pal, sample, False)
        return out


class MatrixEffect(Effect):
    name = "Matrix"

    def render(self, t, palette, p):
        tt = t * max(0.1, p["speed"])
        s = max(0.1, p["scale"])
        trail_len = max(0.02, p.get("matrix_trail", 0.42)) / s
        density = max(0.1, p.get("matrix_density", 1.0))
        head = palette[-1] if palette else (180, 255, 180)
        trail = palette[0] if palette else (0, 80, 0)
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            col = int(x * 28 * density)
            phase = (col * 0.38196601125) % 1
            pos = (tt * (0.18 + (col % 5) * 0.015) + phase) % 1.35 - 0.15
            d = y - pos
            if -0.03 <= d <= 0.04:
                c = head
            elif 0.04 < d < trail_len:
                power = max(0, 1 - d / trail_len)
                c = multiply(trail, 0.15 + 0.85 * power)
            else:
                c = multiply(trail, 0.02)
            out[k] = c
        return out


class BreathingEffect(Effect):
    name = "Breathing"

    def render(self, t, palette, p):
        minimum = clamp01(p.get("breathing_min", 0.08))
        curve = max(0.1, p.get("breathing_curve", 1.0))
        phase = 0.5 + 0.5 * math.sin(t * max(0.05, p["speed"]) * math.pi)
        phase = phase ** curve
        v = minimum + (1.0 - minimum) * phase
        color_position = automatic_palette_phase(t * p["speed"] * 0.06, p)
        c = multiply(palette_sample(palette, color_position), v)
        return {k: c for k in NORMALIZED_CENTERS}


class ColorCycleEffect(Effect):
    name = "Color Cycle"

    def render(self, t, palette, p):
        softness = max(0.05, p.get("cycle_softness", 1.0))
        position = automatic_palette_phase(t * p["speed"] * 0.08, p)
        c = palette_sample(palette, position / softness)
        return {k: c for k in NORMALIZED_CENTERS}


class NeonFlowEffect(Effect):
    name = "Neon Flow"

    def render(self, t, palette, p):
        a = math.radians(p["angle"])
        dx, dy = math.cos(a), math.sin(a)
        twist = p.get("flow_twist", 1.6)
        width = max(0.1, p.get("flow_width", 1.35))
        speed = p["speed"]
        scale = max(0.1, p["scale"])
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            q = x * dx + y * dy
            bend = math.sin((x + y) * math.pi * 2 * scale + t * speed * 0.55) * 0.12 * twist
            motion_pos = q * width + bend + t * speed * 0.12
            color_pos = q * width + bend + automatic_palette_phase(
                t * speed * 0.12, p
            )
            ribbon = 0.5 + 0.5 * math.sin(motion_pos * math.pi * 2.0)
            glow = 0.62 + 0.38 * (ribbon ** 2)
            out[k] = multiply(palette_sample(palette, color_pos), glow)
        return out


class LavaLampEffect(Effect):
    name = "Lava Lamp"

    def render(self, t, palette, p):
        blob_size = max(0.03, p.get("lava_blob_size", 0.17))
        contrast = max(0.1, p.get("lava_contrast", 1.8))
        speed = p["speed"]
        scale = max(0.2, p["scale"])
        centers = [
            (0.18 + 0.10 * math.sin(t * speed * 0.43), 0.78 - (t * speed * 0.08) % 1.1),
            (0.48 + 0.16 * math.sin(t * speed * 0.31 + 2.0), 0.90 - (t * speed * 0.055 + 0.35) % 1.2),
            (0.78 + 0.08 * math.sin(t * speed * 0.39 + 4.0), 0.86 - (t * speed * 0.07 + 0.7) % 1.15),
        ]
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            field = 0.0
            for cx, cy in centers:
                cy = ((cy + 0.2) % 1.4) - 0.2
                d = math.hypot((x - cx) * 1.45, (y - cy) * scale)
                field += math.exp(-(d * d) / (2 * blob_size * blob_size))
            v = clamp01((field / 1.8) ** (1.0 / contrast))
            out[k] = palette_sample(palette, v, False)
        return out


class CometEffect(Effect):
    name = "Comet"

    def render(self, t, palette, p):
        a = math.radians(p["angle"])
        dx, dy = math.cos(a), math.sin(a)
        width = max(0.005, p.get("comet_width", 0.055))
        tail = max(0.01, p.get("comet_tail", 0.32))
        pos = (t * p["speed"] * 0.22) % 1.6 - 0.3
        head = palette[-1] if palette else (255, 255, 255)
        base = palette[0] if palette else (0, 0, 0)
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            q = x * dx + y * dy
            cross = -x * dy + y * dx
            head_dist = math.hypot((q - pos), (cross - 0.5) * 0.6)
            core = math.exp(-(head_dist * head_dist) / (2 * width * width))
            behind = pos - q
            tail_power = 0.0
            if 0 <= behind <= tail:
                tail_power = (1 - behind / tail) * math.exp(-((cross - 0.5) ** 2) / 0.12)
            power = clamp01(core + tail_power * 0.75)
            out[k] = mix(multiply(base, 0.10), palette_sample(palette, 0.55 + 0.45 * power, False), power)
            if core > 0.45:
                out[k] = mix(out[k], head, core)
        return out


class PulseRingsEffect(Effect):
    name = "Pulse Rings"

    def render(self, t, palette, p):
        count = max(1.0, p.get("ring_count", 3.0))
        width = max(0.005, p.get("ring_width", 0.06))
        cx = clamp01(p.get("center_x", 0.5))
        cy = clamp01(p.get("center_y", 0.5))
        phase = (t * p["speed"] * 0.22) % 1.0
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            d = math.hypot((x - cx) * 1.65, y - cy)
            band = (d * count - phase * count) % 1.0
            band = min(band, 1.0 - band)
            glow = math.exp(-(band * band) / (2 * width * width))
            color_pos = (d * count - phase) % 1.0
            out[k] = multiply(palette_sample(palette, color_pos), 0.18 + 0.82 * glow)
        return out


class DualWaveEffect(Effect):
    name = "Dual Wave"

    def render(self, t, palette, p):
        a = math.radians(p["angle"])
        dx, dy = math.cos(a), math.sin(a)
        mix_amount = clamp01(p.get("dual_mix", 0.5))
        freq = max(0.1, p.get("wave_frequency", 2.0))
        sharpness = max(0.1, p.get("wave_sharpness", 1.0))
        scale = max(0.1, p["scale"])
        tt = t * p["speed"] * 2.0
        out = {}
        for k, (x, y) in NORMALIZED_CENTERS.items():
            q1 = x * dx + y * dy
            q2 = x * (-dy) + y * dx
            v1 = 0.5 + 0.5 * math.sin(q1 * math.pi * 2 * freq * scale - tt)
            v2 = 0.5 + 0.5 * math.sin(q2 * math.pi * 2 * freq * scale + tt * 0.77)
            v = ((1 - mix_amount) * v1 + mix_amount * v2) ** sharpness
            out[k] = palette_sample(palette, v, False)
        return out


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
            arr = self._np.asarray(self._mss.grab(mon), dtype=self._np.uint8)[..., :3]
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
            out[k] = _screen_tune(grid[iy, ix], p)
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
            c = _screen_tune(grid.reshape(-1, 3).mean(axis=0), p)
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
            c = tuple(sum(colors[j][i] * weights[j] for j in range(4)) / total for i in range(3))
            out[k] = _screen_tune(c, p)
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
    NeonFlowEffect,
    LavaLampEffect,
    CometEffect,
    PulseRingsEffect,
    DualWaveEffect,
    ScreenAmbilightEffect,
    ScreenAverageEffect,
    ScreenEdgeEffect,
]

EFFECTS = {cls.name: cls for cls in EFFECT_CLASSES}
