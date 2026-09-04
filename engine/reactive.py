import ctypes
import math
import os
import threading
import time
from collections import deque

from blade.layout import NORMALIZED_CENTERS
from .colors import mix


VK_MAP = {
    0x1B: "ESC",
    **{0x70 + i: f"F{i+1}" for i in range(12)},
    **{ord(str(i)): str(i) for i in range(10)},
    **{ord(c): c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},

    0x08: "BACKSPACE",
    0x09: "TAB",
    0x0D: "ENTER",
    0x14: "CAPS",
    0x20: "SPACE",

    0x25: "LEFT",
    0x26: "UP",
    0x27: "RIGHT",
    0x28: "DOWN",
    0x2D: "INS",
    0x2E: "DEL",
    0x24: "HOME",
    0x23: "END",
    0x21: "PGUP",
    0x22: "PGDN",

    0xA0: "LSHIFT",
    0xA1: "RSHIFT",
    0xA2: "LCTRL",
    0xA3: "RCTRL",
    0xA4: "LALT",
    0xA5: "RALT",
    0x5B: "WIN",

    0x90: "NUMLOCK",
    0x6F: "NUM_DIV",
    0x6A: "NUM_MUL",
    0x6D: "NUM_MINUS",
    0x6B: "NUM_PLUS",
    0x6E: "NUM_DOT",
    **{0x60 + i: f"NUM{i}" for i in range(10)},

    0xC0: "~",
    0xBD: "-",
    0xBB: "=",
    0xDB: "[",
    0xDD: "]",
    0xDC: "\\",
    0xBA: ";",
    0xDE: "'",
    0xBC: ",",
    0xBE: ".",
    0xBF: "/",
}


class ReactiveInput:
    def __init__(self):
        self.events = deque(maxlen=96)
        self.lock = threading.RLock()
        self._thread = None
        self._stop = threading.Event()
        self._states = {}

        self.listener = None
        self.error = None
        self.backend = "not started"
        self.last_key = None
        self.last_event_time = 0.0
        self.total_events = 0

    @property
    def running(self):
        if os.name == "nt":
            return self._thread is not None and self._thread.is_alive()
        return self.listener is not None

    def inject(self, key_name):
        if key_name not in NORMALIZED_CENTERS:
            return False
        now = time.perf_counter()
        with self.lock:
            self.events.append((key_name, now))
            self.last_key = key_name
            self.last_event_time = now
            self.total_events += 1
        return True

    def _windows_loop(self):
        try:
            user32 = ctypes.windll.user32
            get_async = user32.GetAsyncKeyState
            get_async.argtypes = [ctypes.c_int]
            get_async.restype = ctypes.c_short

            self.backend = "Windows GetAsyncKeyState"
            self.error = None

            for vk in VK_MAP:
                self._states[vk] = bool(get_async(vk) & 0x8000)

            while not self._stop.is_set():
                for vk, key_name in VK_MAP.items():
                    down = bool(get_async(vk) & 0x8000)
                    old = self._states.get(vk, False)
                    if down and not old:
                        self.inject(key_name)
                    self._states[vk] = down

                self._stop.wait(0.008)

        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"
            self.backend = "Windows input ERROR"

    def _resolve_pynput(self, key):
        vk = getattr(key, "vk", None)
        if vk in VK_MAP:
            return VK_MAP[vk]

        ch = getattr(key, "char", None)
        if ch:
            upper = ch.upper()
            if upper in NORMALIZED_CENTERS:
                return upper
        return None

    def _on_pynput_press(self, key):
        name = self._resolve_pynput(key)
        if name in NORMALIZED_CENTERS:
            self.inject(name)

    def start(self):
        if self.running:
            return

        self._stop.clear()
        self.error = None

        if os.name == "nt":
            self._thread = threading.Thread(
                target=self._windows_loop,
                name="BladeRGB-KeyPoll",
                daemon=True,
            )
            self._thread.start()
            return

        try:
            from pynput import keyboard
            self.backend = "pynput"
            self.listener = keyboard.Listener(on_press=self._on_pynput_press)
            self.listener.start()
        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"
            self.backend = "pynput ERROR"
            self.listener = None

    def stop(self):
        self._stop.set()

        if self._thread is not None:
            if self._thread.is_alive():
                self._thread.join(timeout=1.0)
            self._thread = None

        if self.listener is not None:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None

        self._states.clear()

    def apply(
        self,
        colors,
        now,
        color=(255, 255, 255),
        strength=0.95,
        decay=0.85,
        radius_speed=0.75,
        width=0.105,
        mode="Ripple",
    ):
        with self.lock:
            snapshot = list(self.events)

        out = dict(colors)
        alive = []

        for source, ts in snapshot:
            age = now - ts
            if age < 0 or age > max(0.15, decay):
                continue

            alive.append((source, ts))
            sx, sy = NORMALIZED_CENTERS[source]
            fade = max(0.0, 1.0 - age / max(0.05, decay))

            if mode == "Key Flash":
                out[source] = mix(
                    out.get(source, (0, 0, 0)),
                    color,
                    min(1.0, fade * strength),
                )
                continue

            if mode == "Glow":
                spread = max(0.04, 0.22 * radius_speed)
                for key, (x, y) in NORMALIZED_CENTERS.items():
                    d = math.hypot((x - sx) * 1.55, y - sy)
                    amt = min(
                        1.0,
                        math.exp(-(d * d) / (2 * spread * spread))
                        * fade
                        * strength,
                    )
                    if amt > 0.01:
                        out[key] = mix(out.get(key, (0, 0, 0)), color, amt)
                continue

            radius = age * radius_speed

            for key, (x, y) in NORMALIZED_CENTERS.items():
                d = math.hypot((x - sx) * 1.55, y - sy)

                ring = math.exp(
                    -((d - radius) ** 2) / (2 * width * width)
                )
                center_flash = (
                    math.exp(-(d * d) / (2 * 0.060 * 0.060))
                    * max(0.0, 1.0 - age * 6.0)
                )

                amt = min(
                    1.0,
                    (ring * fade + center_flash) * strength,
                )

                if amt > 0.01:
                    out[key] = mix(
                        out.get(key, (0, 0, 0)),
                        color,
                        amt,
                    )

        with self.lock:
            alive_ids = {(k, ts) for k, ts in alive}
            current = list(self.events)
            kept = [
                e for e in current
                if e in alive_ids or e[1] > now
            ]
            self.events.clear()
            self.events.extend(kept[-96:])

        return out
