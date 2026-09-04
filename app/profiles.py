import json
from pathlib import Path

class ProfileStore:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_name(name):
        clean = "".join(c for c in str(name).strip() if c.isalnum() or c in " _-().").strip()
        return clean[:80] or "Profile"

    def names(self):
        return sorted((p.stem for p in self.directory.glob("*.json")), key=str.casefold)

    def save(self, name, state):
        safe = self._safe_name(name)
        (self.directory / f"{safe}.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        return safe

    def load(self, name):
        return json.loads((self.directory / f"{name}.json").read_text(encoding="utf-8"))

    def delete(self, name):
        path = self.directory / f"{name}.json"
        if path.exists(): path.unlink()

    def export_file(self, path, state):
        payload = {"format":"BladeRGB","version":2,"engine":"QtQuick","profile":state}
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def import_file(self, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("format") == "BladeRGB":
            return data.get("profile", {})
        return data
