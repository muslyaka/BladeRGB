import json
from pathlib import Path

DEFAULTS = {
    "close_to_tray": True,
    "autostart": False,
    "auto_profiles": True,
    "transition_ms": 650,
    "hotkeys_enabled": True,
    "last_profile": "",
}

class SettingsStore:
    def __init__(self, path):
        self.path = Path(path)
        self.data = dict(DEFAULTS)
        self.load()

    def load(self):
        try:
            if self.path.exists():
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    self.data.update(loaded)
        except Exception:
            pass

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
