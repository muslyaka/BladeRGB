from dataclasses import dataclass, field, asdict
import uuid

from blade.layout import GROUPS, KEY_OFFSETS


BLEND_MODES = ["Normal", "Add", "Screen", "Multiply", "Max", "Replace"]
LAYER_TYPES = ["Effect", "Static", "Audio", "Reactive"]
MASK_NAMES = ["All", "WASD", "Arrows", "Numpad", "F-row", "Custom"]


@dataclass
class Layer:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:10])
    name: str = "Layer"
    type: str = "Effect"
    enabled: bool = True
    source: str = "Aurora"
    opacity: float = 1.0
    blend_mode: str = "Normal"
    mask: str = "All"
    custom_keys: list = field(default_factory=list)
    color: list = field(default_factory=lambda: [255, 255, 255])
    palette: list = field(default_factory=lambda: [
        "#10002b", "#3c096c", "#7b2cbf", "#c77dff", "#4cc9f0"
    ])
    params: dict = field(default_factory=lambda: {
        "speed": 1.0,
        "scale": 1.0,
        "angle": 25.0,
    })

    def keys(self):
        if self.mask == "All":
            return set(KEY_OFFSETS)
        if self.mask == "Custom":
            return {k for k in self.custom_keys if k in KEY_OFFSETS}
        return set(GROUPS.get(self.mask, set(KEY_OFFSETS)))

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        known = {
            "id", "name", "type", "enabled", "source", "opacity",
            "blend_mode", "mask", "custom_keys", "color", "palette", "params"
        }
        clean = {k: v for k, v in dict(data).items() if k in known}
        obj = cls(**clean)
        obj.opacity = max(0.0, min(1.0, float(obj.opacity)))
        if obj.blend_mode not in BLEND_MODES:
            obj.blend_mode = "Normal"
        if obj.mask not in MASK_NAMES:
            obj.mask = "All"
        return obj
