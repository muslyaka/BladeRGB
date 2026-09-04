import json
from pathlib import Path

from platform_win import get_foreground_exe


class AppProfileBindings:
    def __init__(self, path):
        self.path = Path(path)
        self.bindings = {}
        self.enabled = True
        self._last_poll = 0.0
        self._last_exe = None
        self.load()

    def load(self):
        try:
            if self.path.exists():
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self.bindings = {
                    str(k).lower(): str(v)
                    for k, v in data.get("bindings", {}).items()
                }
                self.enabled = bool(data.get("enabled", True))
        except Exception:
            self.bindings = {}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "enabled": self.enabled,
                    "bindings": self.bindings,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def bind(self, exe_name, profile_name):
        exe = exe_name.strip().lower()
        if not exe:
            raise ValueError("Укажи имя .exe")
        self.bindings[exe] = profile_name
        self.save()

    def unbind(self, exe_name):
        self.bindings.pop(exe_name.strip().lower(), None)
        self.save()

    def foreground_match(self):
        if not self.enabled:
            return None, None

        exe = get_foreground_exe()
        if not exe:
            return None, None

        return exe, self.bindings.get(exe.lower())
