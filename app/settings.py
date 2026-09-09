import json
import os
from pathlib import Path

DEFAULTS = {
    "close_to_tray": True,
    "autostart": False,
    "auto_profiles": True,
    "transition_ms": 650,
    "hotkeys_enabled": True,
    "last_profile": "",
    "theme": "dark",
    "accent_color": "#7772C9",
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
        payload = json.dumps(self.data, ensure_ascii=False, indent=2)
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")

        try:
            with temp_path.open("w", encoding="utf-8", newline="\n") as fh:
                fh.write(payload)
                fh.flush()
                os.fsync(fh.fileno())
            temp_path.replace(self.path)
        except Exception:
            try:
                temp_path.unlink(missing_ok=True)
            except Exception:
                pass
            self.path.write_text(payload, encoding="utf-8")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
