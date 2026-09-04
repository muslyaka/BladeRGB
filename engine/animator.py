from dataclasses import dataclass, field, asdict
import math
import threading
import time

from .colors import mix, hex_to_rgb, rgb_to_hex


EASINGS = [
    "Linear",
    "Smoothstep",
    "Ease In",
    "Ease Out",
    "Ease In Out",
]


def _ease(t, name):
    t = max(0.0, min(1.0, float(t)))
    if name == "Smoothstep":
        return t * t * (3.0 - 2.0 * t)
    if name == "Ease In":
        return t * t
    if name == "Ease Out":
        return 1.0 - (1.0 - t) * (1.0 - t)
    if name == "Ease In Out":
        if t < 0.5:
            return 2.0 * t * t
        return 1.0 - ((-2.0 * t + 2.0) ** 2) / 2.0
    return t


def _lerp(a, b, t):
    return float(a) + (float(b) - float(a)) * t


def _lerp_angle(a, b, t):
    # shortest 0..360 path
    a = float(a) % 360.0
    b = float(b) % 360.0
    delta = (b - a + 180.0) % 360.0 - 180.0
    return (a + delta * t) % 360.0


@dataclass
class Keyframe:
    time: float = 0.0
    speed: float = 1.0
    scale: float = 1.0
    brightness: float = 0.72
    angle: float = 25.0
    palette: list = field(default_factory=lambda: [
        "#10002b", "#3c096c", "#7b2cbf", "#c77dff", "#4cc9f0"
    ])

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        obj = cls(**{
            k:v for k,v in dict(data).items()
            if k in {"time","speed","scale","brightness","angle","palette"}
        })
        obj.time = max(0.0, float(obj.time))
        obj.speed = float(obj.speed)
        obj.scale = float(obj.scale)
        obj.brightness = max(0.0, min(1.0, float(obj.brightness)))
        obj.angle = float(obj.angle) % 360.0
        obj.palette = list(obj.palette or ["#ffffff"])
        return obj


class Animator:
    def __init__(self):
        self._lock = threading.RLock()
        self.enabled = False
        self.loop = True
        self.duration = 8.0
        self.easing = "Smoothstep"
        self.started_at = time.perf_counter()
        self.keyframes = []

    def restart(self):
        with self._lock:
            self.started_at = time.perf_counter()

    def set_config(self, data):
        with self._lock:
            self.enabled = bool(data.get("enabled", False))
            self.loop = bool(data.get("loop", True))
            self.duration = max(0.1, float(data.get("duration", 8.0)))
            easing = data.get("easing", "Smoothstep")
            self.easing = easing if easing in EASINGS else "Smoothstep"
            self.keyframes = sorted(
                [Keyframe.from_dict(x) for x in data.get("keyframes", [])],
                key=lambda k:k.time
            )
            self.started_at = time.perf_counter()

    def get_config(self):
        with self._lock:
            return {
                "enabled": self.enabled,
                "loop": self.loop,
                "duration": self.duration,
                "easing": self.easing,
                "keyframes": [k.to_dict() for k in self.keyframes],
            }

    def playhead(self, now=None):
        now = time.perf_counter() if now is None else now
        with self._lock:
            elapsed = max(0.0, now - self.started_at)
            duration = max(0.1, self.duration)
            if self.loop:
                return elapsed % duration
            return min(duration, elapsed)

    def sample(self, now=None):
        now = time.perf_counter() if now is None else now

        with self._lock:
            if not self.enabled or not self.keyframes:
                return None

            frames = list(self.keyframes)
            duration = max(0.1, self.duration)
            easing = self.easing
            elapsed = max(0.0, now - self.started_at)
            playhead = elapsed % duration if self.loop else min(duration, elapsed)

        if len(frames) == 1:
            k = frames[0]
            return {
                "speed": k.speed,
                "scale": k.scale,
                "brightness": k.brightness,
                "angle": k.angle,
                "palette": [hex_to_rgb(x) for x in k.palette],
                "playhead": playhead,
            }

        # Wrap-aware segment search.
        pairs = []
        for i in range(len(frames)-1):
            pairs.append((frames[i], frames[i+1], frames[i].time, frames[i+1].time))

        # If looping, interpolate last -> first across the end boundary.
        if self.loop:
            pairs.append((frames[-1], frames[0], frames[-1].time, frames[0].time + duration))

        # Normal non-loop region before first / after last.
        if not self.loop:
            if playhead <= frames[0].time:
                a = b = frames[0]
                t = 0.0
            elif playhead >= frames[-1].time:
                a = b = frames[-1]
                t = 0.0
            else:
                a = b = frames[0]
                t = 0.0
                for x,y,ta,tb in pairs:
                    if ta <= playhead <= tb:
                        a,b = x,y
                        t = (playhead-ta)/max(1e-9,tb-ta)
                        break
        else:
            ph = playhead
            # Region before first keyframe belongs to last->first wrap.
            if ph < frames[0].time:
                ph += duration

            a = b = frames[0]
            t = 0.0
            for x,y,ta,tb in pairs:
                test_ph = ph
                if ta == frames[-1].time and test_ph < ta:
                    test_ph += duration
                if ta <= test_ph <= tb:
                    a,b = x,y
                    t = (test_ph-ta)/max(1e-9,tb-ta)
                    break

        t = _ease(t, easing)

        max_colors = max(len(a.palette), len(b.palette), 1)
        pa = list(a.palette or ["#ffffff"])
        pb = list(b.palette or ["#ffffff"])
        while len(pa) < max_colors:
            pa.append(pa[-1])
        while len(pb) < max_colors:
            pb.append(pb[-1])

        palette = []
        for ca, cb in zip(pa, pb):
            palette.append(
                mix(hex_to_rgb(ca), hex_to_rgb(cb), t)
            )

        return {
            "speed": _lerp(a.speed, b.speed, t),
            "scale": _lerp(a.scale, b.scale, t),
            "brightness": _lerp(a.brightness, b.brightness, t),
            "angle": _lerp_angle(a.angle, b.angle, t),
            "palette": palette,
            "playhead": playhead,
        }
