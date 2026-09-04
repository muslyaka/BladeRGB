import ctypes
import os
import threading


MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012


DEFAULT_HOTKEYS = {
    1: ("Ctrl+Alt+F9", MOD_CONTROL | MOD_ALT, 0x78, "toggle_rgb"),
    2: ("Ctrl+Alt+F10", MOD_CONTROL | MOD_ALT, 0x79, "blackout"),
    3: ("Ctrl+Alt+F11", MOD_CONTROL | MOD_ALT, 0x7A, "previous_profile"),
    4: ("Ctrl+Alt+F12", MOD_CONTROL | MOD_ALT, 0x7B, "next_profile"),
}


class GlobalHotkeys:
    def __init__(self, dispatch):
        self.dispatch = dispatch
        self.enabled = True
        self.error = None
        self._thread = None
        self._thread_id = None
        self._stop = threading.Event()
        self.registered = {}

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if os.name != "nt" or self.running or not self.enabled:
            return

        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="BladeRGB-Hotkeys",
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._stop.set()
        if os.name == "nt" and self._thread_id:
            try:
                ctypes.windll.user32.PostThreadMessageW(
                    self._thread_id, WM_QUIT, 0, 0
                )
            except Exception:
                pass

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        self._thread = None
        self._thread_id = None
        self.registered = {}

    def restart(self):
        self.stop()
        if self.enabled:
            self.start()

    def _run(self):
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            self._thread_id = kernel32.GetCurrentThreadId()

            self.registered = {}
            failed = []

            for hotkey_id, (label, mods, vk, action) in DEFAULT_HOTKEYS.items():
                ok = bool(user32.RegisterHotKey(None, hotkey_id, mods, vk))
                if ok:
                    self.registered[hotkey_id] = (label, action)
                else:
                    failed.append(label)

            if failed:
                self.error = "Не удалось зарегистрировать: " + ", ".join(failed)
            else:
                self.error = None

            class MSG(ctypes.Structure):
                _fields_ = [
                    ("hwnd", ctypes.c_void_p),
                    ("message", ctypes.c_uint),
                    ("wParam", ctypes.c_size_t),
                    ("lParam", ctypes.c_ssize_t),
                    ("time", ctypes.c_ulong),
                    ("pt_x", ctypes.c_long),
                    ("pt_y", ctypes.c_long),
                    ("lPrivate", ctypes.c_ulong),
                ]

            msg = MSG()

            while not self._stop.is_set():
                result = user32.GetMessageW(
                    ctypes.byref(msg), None, 0, 0
                )
                if result <= 0:
                    break

                if msg.message == WM_HOTKEY:
                    hotkey_id = int(msg.wParam)
                    item = self.registered.get(hotkey_id)
                    if item:
                        _, action = item
                        try:
                            self.dispatch(action)
                        except Exception:
                            pass

        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"

        finally:
            try:
                user32 = ctypes.windll.user32
                for hotkey_id in list(self.registered):
                    user32.UnregisterHotKey(None, hotkey_id)
            except Exception:
                pass
            self.registered = {}
