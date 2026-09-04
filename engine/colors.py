import colorsys
import math


def clamp01(v):
    return max(0.0, min(1.0, float(v)))


def clamp255(v):
    return max(0, min(255, int(round(v))))


def mix(a, b, t):
    t = clamp01(t)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def multiply(c, k):
    return tuple(x * k for x in c)


def add(a, b):
    return tuple(min(255, a[i] + b[i]) for i in range(3))


def hsv(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, clamp01(s), clamp01(v))
    return r * 255, g * 255, b * 255


def palette_sample(pal, t, wrap=True):
    if not pal:
        return (255.0, 255.0, 255.0)
    if len(pal) == 1:
        return tuple(map(float, pal[0]))

    if wrap:
        t %= 1.0
        pos = t * len(pal)
        i = int(math.floor(pos))
        f = pos - i
        return mix(pal[i % len(pal)], pal[(i + 1) % len(pal)], f)

    t = clamp01(t)
    pos = t * (len(pal) - 1)
    i = min(len(pal) - 2, int(math.floor(pos)))
    f = pos - i
    return mix(pal[i], pal[i + 1], f)


def hex_to_rgb(v):
    v = str(v).strip().lstrip("#")
    # QML QColor may serialize opaque values as AARRGGBB.
    if len(v) == 8:
        v = v[-6:]
    if len(v) != 6:
        raise ValueError("Нужен цвет #RRGGBB")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(c):
    return "#{:02x}{:02x}{:02x}".format(*(clamp255(x) for x in c))


def blend_pixel(base, top, opacity=1.0, mode="Normal"):
    opacity = clamp01(opacity)
    b = tuple(float(x) for x in base)
    t = tuple(float(x) for x in top)

    if mode == "Add":
        raw = tuple(min(255.0, b[i] + t[i]) for i in range(3))
    elif mode == "Screen":
        raw = tuple(
            255.0 - ((255.0 - b[i]) * (255.0 - t[i]) / 255.0)
            for i in range(3)
        )
    elif mode == "Multiply":
        raw = tuple(b[i] * t[i] / 255.0 for i in range(3))
    elif mode == "Max":
        raw = tuple(max(b[i], t[i]) for i in range(3))
    elif mode == "Replace":
        raw = t
    else:
        raw = t

    return mix(b, raw, opacity)
