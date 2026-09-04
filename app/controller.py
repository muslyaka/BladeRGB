import sys
from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer
from PySide6.QtWidgets import QFileDialog

from blade.device import BladeDevice
from blade.layout import KEY_GEOMETRY, KEY_OFFSETS, GROUPS
from engine.colors import hex_to_rgb, rgb_to_hex
from engine.effects import EFFECTS
from engine.layers import Layer, BLEND_MODES, MASK_NAMES
from engine.renderer import Renderer, BUILTIN_PRESETS
from app.settings import SettingsStore
from app.profiles import ProfileStore
from app_profiles import AppProfileBindings
from platform_win import get_foreground_exe, is_autostart_enabled, set_autostart
from hotkeys import GlobalHotkeys

SOURCE_DIR = Path(__file__).resolve().parents[1]
if getattr(sys, "frozen", False):
    DATA_DIR = Path(sys.executable).resolve().parent
else:
    DATA_DIR = SOURCE_DIR

CONFIG_DIR = DATA_DIR / "config"
PROFILE_DIR = DATA_DIR / "profiles"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

EFFECT_LABELS = {
    "Static": "Статичный цвет", "Gradient": "Градиент", "Rainbow": "Радуга", "Aurora": "Аврора",
    "Plasma": "Плазма", "Wave": "Волна", "Radial": "Радиальная волна", "Scanner": "Сканер",
    "Twinkle": "Мерцание", "Fire": "Огонь", "Ocean": "Океан", "Matrix": "Матрица",
    "Breathing": "Дыхание", "Color Cycle": "Смена цветов", "Screen Ambilight": "Подсветка экрана",
    "Screen Average": "Средний цвет экрана", "Screen Edge": "Цвета по краям экрана",
}
PRESET_LABELS = {
    "Midnight Aurora": "Полуночная аврора", "Cyber Ice": "Киберлёд", "Deep Ocean": "Глубокий океан",
    "Inferno": "Инферно", "Toxic Matrix": "Токсичная матрица", "Sunset Drive": "Закат",
    "Scanner Red": "Красный сканер", "Twinkle Night": "Ночное мерцание", "Screen": "Экран",
}
AUDIO_LABELS = {"Pulse":"Пульс","Spectrum":"Спектр","Bass Wave":"Басовая волна","VU Bars":"Индикатор уровня","Beat Flash":"Вспышка в бит","Three Band":"Три полосы"}
REACTIVE_LABELS = {"Ripple":"Волна от нажатия","Glow":"Свечение","Key Flash":"Вспышка клавиши"}
BLEND_LABELS = {"Normal":"Обычный","Add":"Сложение","Screen":"Осветление","Multiply":"Умножение","Max":"Максимум","Replace":"Замена"}
MASK_LABELS = {"All":"Все клавиши","WASD":"WASD","Arrows":"Стрелки","Numpad":"Цифровой блок","F-row":"F-клавиши","Custom":"Своя маска"}
LAYER_TYPE_LABELS = {"Effect":"Эффект","Static":"Статичный цвет","Audio":"Аудио","Reactive":"Нажатия"}
EASING_LABELS = {"Linear":"Линейно","Smoothstep":"Плавно","Ease In":"Разгон","Ease Out":"Торможение","Ease In Out":"Разгон и торможение"}
UI_LABEL_MAPS = {"effect":EFFECT_LABELS,"preset":PRESET_LABELS,"audio":AUDIO_LABELS,"reactive":REACTIVE_LABELS,"blend":BLEND_LABELS,"mask":MASK_LABELS,"layer_type":LAYER_TYPE_LABELS,"easing":EASING_LABELS}


def _ui_items(values, labels):
    return [{"value": value, "label": labels.get(value, value)} for value in values]


class BladeController(QObject):
    stateChanged = Signal()
    frameChanged = Signal()
    profileListChanged = Signal()
    layersChanged = Signal()
    animatorChanged = Signal()
    bindingListChanged = Signal()
    toast = Signal(str, str)
    requestShowWindow = Signal()
    requestHideWindow = Signal()
    requestQuit = Signal()
    hotkeyReceived = Signal(str)
    hotkeyAction = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.device = BladeDevice()
        self.renderer = Renderer(self.device)
        self.settings = SettingsStore(CONFIG_DIR / "settings.json")
        self.profile_store = ProfileStore(PROFILE_DIR)
        self.bindings = AppProfileBindings(CONFIG_DIR / "app_bindings.json")
        self.bindings.enabled = bool(self.settings.get("auto_profiles", True))
        self._last_error = ""
        self._frame = {key: "#000000" for key in KEY_OFFSETS}
        self._current_profile = self.settings.get("last_profile", "")
        self._foreground_exe = ""
        self._auto_profile_active = ""
        self._manual_state_before_auto = None
        self._palette = ["#10002b", "#3c096c", "#7b2cbf", "#c77dff", "#4cc9f0"]
        self.renderer.transition_duration = float(self.settings.get("transition_ms", 650)) / 1000.0
        self.hotkeyAction.connect(self.handleHotkey)
        self.hotkeyReceived.connect(self.handleHotkey)
        self._hotkeys = GlobalHotkeys(self._hotkey_dispatch)
        self._hotkeys.enabled = bool(self.settings.get("hotkeys_enabled", True))
        if self._hotkeys.enabled:
            self._hotkeys.start()
        self._timer = QTimer(self)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._tick)
        self._timer.start()
        self._profile_timer = QTimer(self)
        self._profile_timer.setInterval(900)
        self._profile_timer.timeout.connect(self._profile_tick)
        self._profile_timer.start()
        QTimer.singleShot(350, self.autoConnect)

    @Property(bool, notify=stateChanged)
    def connected(self): return self.device.connected
    @Property(bool, notify=stateChanged)
    def running(self): return bool(self.renderer.running)
    @Property(float, notify=stateChanged)
    def actualFps(self): return float(self.renderer.actual_fps)
    @Property(str, notify=stateChanged)
    def statusText(self):
        if self.lastError: return "ОШИБКА"
        if self.renderer.running: return "РАБОТАЕТ"
        if self.device.connected: return "ПОДКЛЮЧЕНА"
        return "НЕ ПОДКЛЮЧЕНА"
    @Property(str, notify=stateChanged)
    def lastError(self):
        if self.renderer.last_error: return str(self.renderer.last_error)
        if self.renderer.audio.error: return str(self.renderer.audio.error)
        if self.renderer.reactive.error: return str(self.renderer.reactive.error)
        return self._last_error
    @Property(str, notify=stateChanged)
    def effectName(self): return self.renderer.effect_name
    @Property("QVariantMap", notify=frameChanged)
    def frameColors(self): return dict(self._frame)
    @Property("QVariantList", constant=True)
    def keyboardLayout(self): return [{"name":n,"x":x,"y":y,"w":w,"h":h} for n,(x,y,w,h) in KEY_GEOMETRY.items()]
    @Property("QStringList", constant=True)
    def effectNames(self): return list(EFFECTS)
    @Property("QStringList", constant=True)
    def presetNames(self): return list(BUILTIN_PRESETS)
    @Property("QStringList", constant=True)
    def blendModes(self): return list(BLEND_MODES)
    @Property("QStringList", constant=True)
    def maskNames(self): return list(MASK_NAMES)
    @Property("QStringList", constant=True)
    def audioModes(self): return ["Pulse", "Spectrum", "Bass Wave", "VU Bars", "Beat Flash", "Three Band"]
    @Property("QStringList", constant=True)
    def reactiveModes(self): return ["Ripple", "Glow", "Key Flash"]
    @Property("QVariantList", constant=True)
    def effectItems(self): return _ui_items(EFFECTS.keys(), EFFECT_LABELS)
    @Property("QVariantList", constant=True)
    def presetItems(self): return _ui_items(BUILTIN_PRESETS.keys(), PRESET_LABELS)
    @Property("QVariantList", constant=True)
    def audioItems(self): return _ui_items(self.audioModes, AUDIO_LABELS)
    @Property("QVariantList", constant=True)
    def reactiveItems(self): return _ui_items(self.reactiveModes, REACTIVE_LABELS)
    @Property("QVariantList", constant=True)
    def blendItems(self): return _ui_items(BLEND_MODES, BLEND_LABELS)
    @Property("QVariantList", constant=True)
    def maskItems(self): return _ui_items(MASK_NAMES, MASK_LABELS)
    @Property("QVariantList", constant=True)
    def layerTypeItems(self): return _ui_items(["Effect", "Static", "Audio", "Reactive"], LAYER_TYPE_LABELS)
    @Property("QVariantList", constant=True)
    def easingItems(self): return _ui_items(EASING_LABELS.keys(), EASING_LABELS)
    @Slot(str, str, result=str)
    def uiLabel(self, category, value): return UI_LABEL_MAPS.get(str(category), {}).get(str(value), str(value))
    @Property("QStringList", notify=profileListChanged)
    def profileNames(self): return self.profile_store.names()
    @Property(str, notify=profileListChanged)
    def currentProfile(self): return self._current_profile
    @Property("QStringList", notify=stateChanged)
    def palette(self): return list(self._palette)
    @Property("QVariantMap", notify=stateChanged)
    def params(self): return self.renderer.get_params()
    @Property(bool, notify=stateChanged)
    def reactiveEnabled(self): return bool(self.renderer.reactive_enabled)
    @Property(str, notify=stateChanged)
    def reactiveMode(self): return self.renderer.reactive_mode
    @Property(str, notify=stateChanged)
    def reactiveColor(self): return rgb_to_hex(self.renderer.reactive_color)
    @Property(bool, notify=stateChanged)
    def audioEnabled(self): return bool(self.renderer.audio_enabled)
    @Property(str, notify=stateChanged)
    def audioMode(self): return self.renderer.audio_mode
    @Property(int, notify=stateChanged)
    def paintedCount(self): return len(self.renderer.overlay_key_colors)
    @Property("QVariantMap", notify=stateChanged)
    def paintedColors(self): return {k:rgb_to_hex(v) for k,v in self.renderer.overlay_key_colors.items()}
    @Property("QVariantList", notify=layersChanged)
    def layers(self): return [layer.to_dict() for layer in self.renderer.get_layers()]
    @Property("QVariantMap", notify=animatorChanged)
    def animation(self):
        cfg=self.renderer.get_animation(); cfg["playhead"]=self.renderer.animator.playhead(); return cfg
    @Property(str, notify=stateChanged)
    def foregroundExe(self): return self._foreground_exe or "—"
    @Property("QVariantList", notify=bindingListChanged)
    def appBindings(self): return [{"exe":exe,"profile":profile} for exe,profile in sorted(self.bindings.bindings.items())]
    @Property(bool, notify=stateChanged)
    def autoProfilesEnabled(self): return bool(self.settings.get("auto_profiles", True))
    @Property(bool, notify=stateChanged)
    def closeToTray(self): return bool(self.settings.get("close_to_tray", True))
    @Property(bool, notify=stateChanged)
    def autostartEnabled(self): return bool(is_autostart_enabled())
    @Property(bool, notify=stateChanged)
    def hotkeysEnabled(self): return bool(self.settings.get("hotkeys_enabled", True))
    @Property(int, notify=stateChanged)
    def transitionMs(self): return int(self.settings.get("transition_ms", 650))

    def _tick(self):
        try:
            snapshot=self.renderer.snapshot(); next_frame={key:rgb_to_hex(color) for key,color in snapshot.items()}
            if next_frame != self._frame:
                self._frame=next_frame; self.frameChanged.emit()
            self.stateChanged.emit()
            if self.renderer.animator.enabled: self.animatorChanged.emit()
        except Exception as exc:
            self._last_error=f"{type(exc).__name__}: {exc}"; self.stateChanged.emit()

    @Slot()
    def autoConnect(self):
        self.connectDevice(silent=True)
        if self.device.connected: self.startEngine(silent=True)
    @Slot()
    @Slot(bool)
    def connectDevice(self, silent=False):
        try:
            self.device.connect(); self.device.enable_manual_mode(); self._last_error=""
            if not silent: self.toast.emit("Клавиатура подключена", "ARDOR BLADE готова к управлению подсветкой.")
        except Exception as exc:
            self._last_error=f"{type(exc).__name__}: {exc}"
            if not silent: self.toast.emit("Ошибка подключения", self._last_error)
        self.stateChanged.emit()
    @Slot()
    @Slot(bool)
    def startEngine(self, silent=False):
        try:
            if not self.device.connected: self.device.connect()
            self.device.enable_manual_mode(); self.renderer.start(); self._last_error=""
        except Exception as exc:
            self._last_error=f"{type(exc).__name__}: {exc}"
            if not silent: self.toast.emit("Ошибка подсветки", self._last_error)
        self.stateChanged.emit()
    @Slot()
    def stopEngine(self): self.renderer.stop(); self.stateChanged.emit()
    @Slot()
    def toggleEngine(self): self.stopEngine() if self.renderer.running else self.startEngine()
    @Slot()
    def blackout(self):
        try: self.renderer.blackout()
        except Exception as exc:
            self._last_error=f"{type(exc).__name__}: {exc}"; self.toast.emit("Ошибка отключения подсветки", self._last_error)
        self.stateChanged.emit()

    @Slot(str)
    def setEffect(self, name):
        if name in EFFECTS: self.renderer.set_effect(name); self.stateChanged.emit()
    @Slot(str, float)
    def setParam(self, name, value): self.renderer.set_param(name, value); self.stateChanged.emit()
    @Slot(int, str)
    def setPaletteColor(self, index, value):
        if index < 0: return
        while len(self._palette) <= index: self._palette.append("#ffffff")
        try:
            self._palette[index]=rgb_to_hex(hex_to_rgb(value)); self.renderer.set_palette([hex_to_rgb(x) for x in self._palette]); self.stateChanged.emit()
        except Exception: pass
    @Slot(str)
    def applyPreset(self, name):
        data=BUILTIN_PRESETS.get(name)
        if not data: return
        self.renderer.begin_transition(); effect=data.get("effect", "Aurora")
        if effect in EFFECTS: self.renderer.set_effect(effect)
        palette=list(data.get("palette", self._palette))
        while len(palette)<5: palette.append(palette[-1] if palette else "#ffffff")
        self._palette=palette[:5]; self.renderer.set_palette([hex_to_rgb(x) for x in self._palette])
        for key,value in data.get("params",{}).items(): self.renderer.set_param(key,value)
        self.stateChanged.emit(); self.toast.emit("Сцена применена", PRESET_LABELS.get(name,name))

    @Slot(str, str)
    def paintKey(self, key, color):
        if key not in KEY_OFFSETS: return
        try:
            self.renderer.overlay_key_colors[key]=hex_to_rgb(color); self.renderer.overlay_keys=set(self.renderer.overlay_key_colors); self.renderer.overlay_enabled=True; self.stateChanged.emit()
        except Exception: pass
    @Slot(str)
    def eraseKey(self, key): self.renderer.overlay_key_colors.pop(key,None); self.renderer.overlay_keys=set(self.renderer.overlay_key_colors); self.stateChanged.emit()
    @Slot()
    def clearPaint(self): self.renderer.overlay_key_colors.clear(); self.renderer.overlay_keys.clear(); self.stateChanged.emit()
    @Slot(str, str)
    def paintGroup(self, group, color):
        try: rgb=hex_to_rgb(color)
        except Exception: return
        for key in GROUPS.get(group,set()): self.renderer.overlay_key_colors[key]=rgb
        self.renderer.overlay_keys=set(self.renderer.overlay_key_colors); self.renderer.overlay_enabled=True; self.stateChanged.emit()

    @Slot(bool)
    def setReactiveEnabled(self, value): self.renderer.reactive_enabled=bool(value); self.stateChanged.emit()
    @Slot(str)
    def setReactiveMode(self, mode):
        if mode in self.reactiveModes: self.renderer.reactive_mode=mode
        self.stateChanged.emit()
    @Slot(str)
    def setReactiveColor(self, color):
        try: self.renderer.reactive_color=hex_to_rgb(color)
        except Exception: return
        self.stateChanged.emit()
    @Slot(bool)
    def setAudioEnabled(self, value): self.renderer.set_audio_enabled(bool(value)); self.stateChanged.emit()
    @Slot(str)
    def setAudioMode(self, mode):
        if mode in self.audioModes: self.renderer.audio_mode=mode
        self.stateChanged.emit()

    @Slot(str)
    def addLayer(self, layer_type):
        source={"Effect":"Aurora","Static":"Static","Audio":"Pulse","Reactive":"Ripple"}.get(layer_type,"Aurora")
        layer=Layer(name=LAYER_TYPE_LABELS.get(layer_type,layer_type),type=layer_type,source=source,opacity=0.8 if layer_type!="Static" else 1.0,blend_mode="Screen" if layer_type in {"Audio","Reactive"} else "Normal")
        self.renderer.add_layer(layer); self.renderer.sync_audio_state(); self.layersChanged.emit()
    @Slot(str)
    def removeLayer(self, layer_id): self.renderer.remove_layer(layer_id); self.renderer.sync_audio_state(); self.layersChanged.emit()
    @Slot(str, int)
    def moveLayer(self, layer_id, delta): self.renderer.move_layer(layer_id,delta); self.layersChanged.emit()
    @Slot(str, str, "QVariant")
    def setLayerField(self, layer_id, field, value):
        layer=next((x for x in self.renderer.get_layers() if x.id==layer_id),None)
        if layer is None: return
        changes={}
        try:
            if field=="enabled": changes[field]=bool(value)
            elif field=="opacity": changes[field]=float(value)
            elif field in {"name","source","blend_mode","mask"}: changes[field]=str(value)
            elif field=="color": changes[field]=list(hex_to_rgb(str(value)))
            elif field in {"speed","scale","angle"}:
                params=dict(layer.params); params[field]=float(value); changes["params"]=params
            else: return
        except Exception: return
        self.renderer.update_layer(layer_id,**changes); self.renderer.sync_audio_state(); self.layersChanged.emit()
    @Slot(str, "QStringList")
    def setLayerCustomKeys(self, layer_id, keys): self.renderer.update_layer(layer_id,mask="Custom",custom_keys=list(keys)); self.layersChanged.emit()

    def _change_anim(self, **kwargs):
        cfg=self.renderer.get_animation(); cfg.update(kwargs); self.renderer.set_animation(cfg); self.animatorChanged.emit()
    @Slot(bool)
    def setAnimatorEnabled(self, value): self._change_anim(enabled=bool(value))
    @Slot(bool)
    def setAnimatorLoop(self, value): self._change_anim(loop=bool(value))
    @Slot(float)
    def setAnimatorDuration(self, value): self._change_anim(duration=max(0.5,min(60.0,float(value))))
    @Slot(str)
    def setAnimatorEasing(self, value): self._change_anim(easing=str(value))
    @Slot()
    def restartAnimator(self): self.renderer.restart_animation(); self.animatorChanged.emit()
    @Slot()
    def captureKeyframe(self):
        cfg=self.renderer.get_animation(); frames=list(cfg.get("keyframes",[])); p=self.renderer.get_params()
        frames.append({"time":self.renderer.animator.playhead(),"speed":p["speed"],"scale":p["scale"],"brightness":p["brightness"],"angle":p["angle"],"palette":list(self._palette)})
        frames.sort(key=lambda x:float(x.get("time",0))); cfg["keyframes"]=frames; self.renderer.set_animation(cfg); self.animatorChanged.emit()
    @Slot(int)
    def deleteKeyframe(self, index):
        cfg=self.renderer.get_animation(); frames=list(cfg.get("keyframes",[]))
        if 0<=index<len(frames): frames.pop(index); cfg["keyframes"]=frames; self.renderer.set_animation(cfg); self.animatorChanged.emit()

    def capture_state(self):
        return {"effect":self.renderer.effect_name,"palette":list(self._palette),"params":self.renderer.get_params(),
                "reactive":{"enabled":self.renderer.reactive_enabled,"mode":self.renderer.reactive_mode,"color":rgb_to_hex(self.renderer.reactive_color)},
                "audio":{"enabled":self.renderer.audio_enabled,"mode":self.renderer.audio_mode},
                "paint":{"enabled":self.renderer.overlay_enabled,"opacity":self.renderer.params.get("overlay_opacity",1.0),"colors":{k:rgb_to_hex(v) for k,v in self.renderer.overlay_key_colors.items()}},
                "layers":[layer.to_dict() for layer in self.renderer.get_layers()],"animation":self.renderer.get_animation()}
    def apply_state(self, data):
        if not isinstance(data,dict): return
        self.renderer.begin_transition(float(self.settings.get("transition_ms",650))/1000.0)
        effect=data.get("effect","Aurora")
        if effect in EFFECTS: self.renderer.set_effect(effect)
        palette=list(data.get("palette",self._palette))
        while len(palette)<5: palette.append(palette[-1] if palette else "#ffffff")
        self._palette=[rgb_to_hex(hex_to_rgb(x)) for x in palette[:5]]; self.renderer.set_palette([hex_to_rgb(x) for x in self._palette])
        for key,value in data.get("params",{}).items(): self.renderer.set_param(key,value)
        reactive=data.get("reactive",{}); self.renderer.reactive_enabled=bool(reactive.get("enabled",True)); self.renderer.reactive_mode=reactive.get("mode","Ripple")
        try: self.renderer.reactive_color=hex_to_rgb(reactive.get("color","#ffffff"))
        except Exception: pass
        audio=data.get("audio",{}); self.renderer.audio_mode=audio.get("mode","Pulse"); self.renderer.set_audio_enabled(bool(audio.get("enabled",False)))
        paint=data.get("paint",{}); self.renderer.overlay_enabled=bool(paint.get("enabled",True)); self.renderer.set_param("overlay_opacity",paint.get("opacity",1.0))
        mapped={}
        for key,value in paint.get("colors",{}).items():
            if key in KEY_OFFSETS:
                try: mapped[key]=hex_to_rgb(value)
                except Exception: pass
        self.renderer.overlay_key_colors=mapped; self.renderer.overlay_keys=set(mapped); self.renderer.set_layers(data.get("layers",[])); self.renderer.set_animation(data.get("animation",{"enabled":False,"loop":True,"duration":8.0,"easing":"Smoothstep","keyframes":[]})); self.renderer.sync_audio_state(); self.stateChanged.emit(); self.layersChanged.emit(); self.animatorChanged.emit()

    @Slot(str)
    def saveProfile(self, name):
        safe=self.profile_store.save(name,self.capture_state()); self._current_profile=safe; self.settings.set("last_profile",safe); self.profileListChanged.emit(); self.toast.emit("Профиль сохранён",safe)
    @Slot(str)
    def loadProfile(self, name):
        try:
            self.apply_state(self.profile_store.load(name)); self._current_profile=name; self.settings.set("last_profile",name); self.profileListChanged.emit(); self.toast.emit("Профиль загружен",name)
        except Exception as exc: self.toast.emit("Ошибка профиля",f"{type(exc).__name__}: {exc}")
    @Slot(str)
    def deleteProfile(self, name):
        self.profile_store.delete(name)
        if self._current_profile==name: self._current_profile=""
        self.profileListChanged.emit()
    @Slot()
    def exportCurrentProfile(self):
        path,_=QFileDialog.getSaveFileName(None,"Экспорт профиля BladeRGB",str(DATA_DIR/"BladeRGB_Profile.brgb"),"Профиль BladeRGB (*.brgb);;JSON (*.json)")
        if not path: return
        try: self.profile_store.export_file(path,self.capture_state()); self.toast.emit("Профиль экспортирован",Path(path).name)
        except Exception as exc: self.toast.emit("Ошибка экспорта",str(exc))
    @Slot()
    def importProfile(self):
        path,_=QFileDialog.getOpenFileName(None,"Импорт профиля BladeRGB",str(DATA_DIR),"Профиль BladeRGB (*.brgb *.json)")
        if not path: return
        try: self.apply_state(self.profile_store.import_file(path)); self.toast.emit("Профиль импортирован",Path(path).name)
        except Exception as exc: self.toast.emit("Ошибка импорта",str(exc))

    def _profile_tick(self):
        exe=get_foreground_exe()
        if (exe or "")!=self._foreground_exe: self._foreground_exe=exe or ""; self.stateChanged.emit()
        if not self.settings.get("auto_profiles",True): return
        exe,profile=self.bindings.foreground_match()
        if profile and profile!=self._auto_profile_active:
            if not self._auto_profile_active: self._manual_state_before_auto=self.capture_state()
            try: self.apply_state(self.profile_store.load(profile)); self._auto_profile_active=profile
            except Exception: pass
        elif not profile and self._auto_profile_active:
            if self._manual_state_before_auto: self.apply_state(self._manual_state_before_auto)
            self._manual_state_before_auto=None; self._auto_profile_active=""
    @Slot(str,str)
    def bindApp(self, exe, profile):
        exe=str(exe).strip(); profile=str(profile).strip()
        if exe and profile: self.bindings.bind(exe,profile); self.bindingListChanged.emit()
    @Slot(str)
    def unbindApp(self, exe): self.bindings.unbind(exe); self.bindingListChanged.emit()
    @Slot(bool)
    def setAutoProfilesEnabled(self, value):
        value=bool(value); self.settings.set("auto_profiles",value); self.bindings.enabled=value; self.bindings.save(); self.stateChanged.emit()
    @Slot(bool)
    def setCloseToTray(self, value): self.settings.set("close_to_tray",bool(value)); self.stateChanged.emit()
    @Slot(bool)
    def setAutostart(self, value):
        try: set_autostart(bool(value)); self.settings.set("autostart",bool(value))
        except Exception as exc: self.toast.emit("Ошибка автозапуска",str(exc))
        self.stateChanged.emit()
    @Slot(bool)
    def setHotkeysEnabled(self, value):
        enabled=bool(value); self.settings.set("hotkeys_enabled",enabled); self._hotkeys.enabled=enabled; self._hotkeys.restart() if enabled else self._hotkeys.stop(); self.stateChanged.emit()
    @Slot(int)
    def setTransitionMs(self, value):
        value=max(0,min(2500,int(value))); self.settings.set("transition_ms",value); self.renderer.transition_duration=value/1000.0; self.stateChanged.emit()
    def _hotkey_dispatch(self, action): self.hotkeyAction.emit(str(action))
    @Slot(str)
    def handleHotkey(self, action):
        if action=="toggle_rgb": self.toggleEngine()
        elif action=="blackout": self.blackout()
        elif action in {"previous_profile","next_profile"}:
            names=self.profile_store.names()
            if not names: return
            direction=-1 if action=="previous_profile" else 1
            index=names.index(self._current_profile) if self._current_profile in names else (-1 if direction>0 else 0)
            self.loadProfile(names[(index+direction)%len(names)])
    @Slot()
    def hideWindow(self): self.requestHideWindow.emit()
    @Slot()
    def showWindow(self): self.requestShowWindow.emit()
    @Slot()
    def quitApp(self): self.requestQuit.emit()
    def shutdown(self):
        try: self._hotkeys.stop()
        except Exception: pass
        try: self.renderer.stop()
        except Exception: pass
        try: self.device.close()
        except Exception: pass
