import math
import random
import threading
import time
from blade.layout import KEY_OFFSETS, NORMALIZED_CENTERS
from .audio import SystemAudioMeter
from .animator import Animator
from .colors import mix, multiply, clamp255, blend_pixel, hex_to_rgb
from .effects import EFFECTS
from .layers import Layer
from .reactive import ReactiveInput
DEFAULT_PARAMS = {'speed': 1.0, 'scale': 1.0, 'angle': 25.0, 'brightness': 0.72, 'fps': 30.0, 'reactive_strength': 0.9, 'reactive_decay': 0.85, 'reactive_speed': 0.78, 'audio_gain': 1.25, 'overlay_opacity': 1.0}
BUILTIN_PRESETS = {'Midnight Aurora': {'effect': 'Aurora', 'palette': ['#10002b', '#3c096c', '#7b2cbf', '#c77dff', '#4cc9f0'], 'params': {'speed': 0.72, 'scale': 1.35, 'brightness': 0.74, 'angle': 30}}, 'Cyber Ice': {'effect': 'Plasma', 'palette': ['#001219', '#005f73', '#0a9396', '#94d2bd', '#e9d8a6'], 'params': {'speed': 0.8, 'scale': 1.15, 'brightness': 0.78, 'angle': 10}}, 'Deep Ocean': {'effect': 'Ocean', 'palette': ['#001233', '#023e8a', '#0077b6', '#00b4d8', '#90e0ef'], 'params': {'speed': 0.62, 'scale': 1.2, 'brightness': 0.7, 'angle': 0}}, 'Inferno': {'effect': 'Fire', 'palette': ['#100000', '#5c0000', '#ff3c00', '#ff9e00', '#fff1a8'], 'params': {'speed': 1.15, 'scale': 1.25, 'brightness': 0.85, 'angle': 0}}, 'Toxic Matrix': {'effect': 'Matrix', 'palette': ['#001800', '#007a00', '#39ff14', '#d8ffd0'], 'params': {'speed': 1.15, 'scale': 1, 'brightness': 0.78, 'angle': 90}}, 'Sunset Drive': {'effect': 'Gradient', 'palette': ['#240046', '#7b2cbf', '#ff006e', '#fb5607', '#ffbe0b'], 'params': {'speed': 0.35, 'scale': 1.5, 'brightness': 0.8, 'angle': 18}}, 'Scanner Red': {'effect': 'Scanner', 'palette': ['#120000', '#ff143d'], 'params': {'speed': 1.1, 'scale': 1.1, 'brightness': 0.82, 'angle': 0}}, 'Twinkle Night': {'effect': 'Twinkle', 'palette': ['#080914', '#25184a', '#6d5dfc', '#ffffff'], 'params': {'speed': 0.7, 'scale': 1, 'brightness': 0.7, 'angle': 0}}, 'Screen': {'effect': 'Screen Ambilight', 'palette': ['#ffffff'], 'params': {'speed': 1, 'scale': 1, 'brightness': 0.78, 'angle': 0}}}

class Renderer:
    def __init__(self, device):
        self.device = device
        self.effect_name = 'Aurora'
        self.effect = EFFECTS[self.effect_name]()
        self.palette = [(16, 0, 43), (60, 9, 108), (123, 44, 191), (199, 125, 255), (76, 201, 240)]
        self.params = dict(DEFAULT_PARAMS)
        self.reactive_enabled = True
        self.reactive_color = (255, 255, 255)
        self.reactive_mode = 'Ripple'
        self.audio_enabled = False
        self.audio_mode = 'Pulse'
        self.overlay_enabled = True
        self.overlay_keys = set()
        self.overlay_color = (255, 255, 255)
        self.overlay_key_colors = {}
        self.layers = []
        self._layer_effects = {}
        self.reactive = ReactiveInput()
        self.audio = SystemAudioMeter()
        self.animator = Animator()
        self.transition_duration = 0.65
        self._transition_from = None
        self._transition_started = 0.0
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread = None
        self.last_colors = {k: (0, 0, 0) for k in KEY_OFFSETS}
        self.last_error = None
        self.actual_fps = 0.0
        self.frame_counter = 0
        self.running = False
        self._previous_colors = None
        self._last_effect_change = time.perf_counter()

    def set_effect(self, name):
        if name not in EFFECTS: raise KeyError(name)
        with self._lock:
            try: self.effect.close()
            except Exception: pass
            self._previous_colors = dict(self.last_colors)
            self.effect_name = name
            self.effect = EFFECTS[name]()
            self._last_effect_change = time.perf_counter()

    def set_palette(self, palette):
        with self._lock: self.palette = [tuple(map(int, c)) for c in palette]
    def set_param(self, name, value):
        if name not in self.params: return
        with self._lock: self.params[name] = float(value)
    def update_params(self, **kwargs):
        with self._lock:
            for k,v in kwargs.items():
                if k in self.params: self.params[k]=float(v)
    def get_params(self):
        with self._lock: return dict(self.params)
    def get_layers(self):
        with self._lock: return [Layer.from_dict(x.to_dict()) for x in self.layers]
    def set_layers(self, layers):
        with self._lock:
            self.layers=[x if isinstance(x,Layer) else Layer.from_dict(x) for x in layers]; self._cleanup_layer_effects()
    def add_layer(self, layer):
        if not isinstance(layer,Layer): layer=Layer.from_dict(layer)
        with self._lock: self.layers.append(layer)
        return layer.id
    def update_layer(self, layer_id, **changes):
        with self._lock:
            layer=next((x for x in self.layers if x.id==layer_id),None)
            if layer is None: return False
            old_source=layer.source
            for k,v in changes.items():
                if hasattr(layer,k): setattr(layer,k,v)
            if old_source != layer.source: self._drop_layer_effect(layer_id)
            return True
    def remove_layer(self, layer_id):
        with self._lock:
            self.layers=[x for x in self.layers if x.id!=layer_id]; self._drop_layer_effect(layer_id)
    def move_layer(self, layer_id, delta):
        with self._lock:
            idx=next((i for i,x in enumerate(self.layers) if x.id==layer_id),None)
            if idx is None: return
            new=max(0,min(len(self.layers)-1,idx+int(delta)))
            if new==idx: return
            item=self.layers.pop(idx); self.layers.insert(new,item)
    def _drop_layer_effect(self, layer_id):
        obj=self._layer_effects.pop(layer_id,None)
        if obj is not None:
            try: obj.close()
            except Exception: pass
    def _cleanup_layer_effects(self):
        valid={x.id for x in self.layers}
        for layer_id in list(self._layer_effects):
            if layer_id not in valid: self._drop_layer_effect(layer_id)
    def _effect_for_layer(self, layer):
        obj=self._layer_effects.get(layer.id)
        if obj is None or getattr(obj,'name',None)!=layer.source:
            self._drop_layer_effect(layer.id); cls=EFFECTS.get(layer.source)
            if cls is None: return None
            obj=cls(); self._layer_effects[layer.id]=obj
        return obj
    def _audio_needed(self, layers=None):
        if self.audio_enabled: return True
        layers=layers if layers is not None else self.layers
        return any((x.enabled and x.type=='Audio' for x in layers))
    def sync_audio_state(self):
        with self._lock: needed=self._audio_needed()
        self.audio.start() if needed else self.audio.stop()
    def set_audio_enabled(self, value): self.audio_enabled=bool(value); self.sync_audio_state()
    def start(self):
        if self.running: return
        if not self.device.connected: self.device.connect()
        self.device.enable_manual_mode(); self.reactive.start(); self.sync_audio_state(); self._stop.clear(); self.running=True
        self._thread=threading.Thread(target=self._loop,name='BladeRGB-Renderer',daemon=True); self._thread.start()
    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive(): self._thread.join(timeout=2)
        self._thread=None; self.running=False; self.audio.stop(); self.reactive.stop()
    def blackout(self):
        if not self.device.connected: self.device.connect()
        self.device.enable_manual_mode(); self.device.blackout()
        with self._lock: self.last_colors={k:(0,0,0) for k in KEY_OFFSETS}
    def snapshot(self):
        with self._lock: return dict(self.last_colors)
    def begin_transition(self, duration=None):
        with self._lock:
            self._transition_from=dict(self.last_colors); self._transition_started=time.perf_counter()
            if duration is not None: self.transition_duration=max(0.0,float(duration))
    def set_animation(self, data): self.animator.set_config(data)
    def get_animation(self): return self.animator.get_config()
    def restart_animation(self): self.animator.restart()
    def randomize(self):
        pal=[tuple((random.randint(0,255) for _ in range(3))) for _ in range(random.randint(3,6))]
        with self._lock:
            self.palette=pal; self.params['speed']=random.uniform(0.25,1.8); self.params['scale']=random.uniform(0.55,2.4); self.params['angle']=random.uniform(0,360); self.params['brightness']=random.uniform(0.48,0.9)
    def _blend_map(self, base, top, keys, opacity, mode):
        out=dict(base)
        for k in keys:
            if k not in out or k not in top: continue
            out[k]=blend_pixel(out[k],top[k],opacity,mode)
        return out
    def _audio_map(self, mode, levels, color, gain):
        bass,mid,high,level,beat=levels; gain=max(0.1,float(gain)); out={k:(0,0,0) for k in KEY_OFFSETS}
        if mode=='Spectrum':
            for k,(x,y) in NORMALIZED_CENTERS.items():
                v=bass if x<0.33 else mid if x<0.66 else high; out[k]=multiply(color,min(1,v*gain))
        elif mode=='Bass Wave':
            phase=time.perf_counter()*2.5
            for k,(x,y) in NORMALIZED_CENTERS.items():
                wave=0.5+0.5*math.sin(x*12-phase); out[k]=multiply(color,min(1,bass*gain)*wave)
        elif mode=='VU Bars':
            power=min(1,level*gain)
            for k,(x,y) in NORMALIZED_CENTERS.items(): out[k]=multiply(color,1.0 if 1-y<=power else 0.03)
        elif mode=='Beat Flash':
            amount=min(1,beat*gain); out={k:multiply(color,amount) for k in KEY_OFFSETS}
        elif mode=='Three Band':
            for k,(x,y) in NORMALIZED_CENTERS.items():
                v=bass*max(0,1-abs(x-0.16)*3.2)+mid*max(0,1-abs(x-0.5)*3.2)+high*max(0,1-abs(x-0.84)*3.2); out[k]=multiply(color,min(1,v*gain))
        else:
            amount=min(1,(bass*0.72+level*0.35)*gain); out={k:multiply(color,amount) for k in KEY_OFFSETS}
        return out
    def _render_custom_layer(self, layer, now, base_params, audio_levels):
        keys=layer.keys(); p=dict(base_params); p.update(layer.params or {})
        if layer.type=='Effect':
            obj=self._effect_for_layer(layer)
            if obj is None: return (None,keys)
            palette=[hex_to_rgb(x) for x in layer.palette] if layer.palette else [(255,255,255)]
            return (obj.render(now,palette,p),keys)
        if layer.type=='Static':
            c=tuple(layer.color); return ({k:c for k in KEY_OFFSETS},keys)
        if layer.type=='Audio': return (self._audio_map(layer.source,audio_levels,tuple(layer.color),p.get('audio_gain',base_params['audio_gain'])),keys)
        if layer.type=='Reactive':
            blank={k:(0,0,0) for k in KEY_OFFSETS}; mode=layer.source if layer.source in ['Ripple','Glow','Key Flash'] else 'Ripple'
            rendered=self.reactive.apply(blank,now,color=tuple(layer.color),strength=float(layer.params.get('strength',0.9)),decay=float(layer.params.get('decay',0.85)),radius_speed=float(layer.params.get('speed',0.78)),mode=mode)
            return (rendered,keys)
        return (None,keys)
    def _quick_audio_overlay(self, colors, levels, palette, gain, mode):
        color=palette[-1] if palette else (255,255,255); top=self._audio_map(mode,levels,color,gain); return self._blend_map(colors,top,set(KEY_OFFSETS),0.38,'Screen')
    def _quick_overlay(self, colors, overlay_key_colors, keys, color, opacity):
        if overlay_key_colors:
            top={k:tuple(v) for k,v in overlay_key_colors.items() if k in KEY_OFFSETS}; blend_keys=set(top)
        else:
            top={k:color for k in KEY_OFFSETS}; blend_keys=set(keys)
        return self._blend_map(colors,top,blend_keys,opacity,'Normal')
    def _loop(self):
        last_stat=time.perf_counter(); stat_frames=0; last_audio_sync=0.0
        try:
            while not self._stop.is_set():
                start=time.perf_counter()
                with self._lock:
                    p=dict(self.params); palette=list(self.palette); effect=self.effect; reactive_enabled=self.reactive_enabled; reactive_color=self.reactive_color; reactive_mode=self.reactive_mode; audio_enabled=self.audio_enabled; audio_mode=self.audio_mode; overlay_enabled=self.overlay_enabled; overlay_keys=set(self.overlay_keys); overlay_color=self.overlay_color; overlay_key_colors={k:tuple(v) for k,v in self.overlay_key_colors.items()}; layers=[Layer.from_dict(x.to_dict()) for x in self.layers]; prev=self._previous_colors; change_time=self._last_effect_change; transition_from=self._transition_from; transition_started=self._transition_started; transition_duration=self.transition_duration
                anim=self.animator.sample(start)
                if anim is not None:
                    p['speed']=anim['speed']; p['scale']=anim['scale']; p['brightness']=anim['brightness']; p['angle']=anim['angle']; palette=list(anim['palette'])
                if start-last_audio_sync>1.0:
                    need_audio=audio_enabled or any((x.enabled and x.type=='Audio' for x in layers)); self.audio.start() if need_audio else self.audio.stop(); last_audio_sync=start
                audio_levels=self.audio.levels(); colors=effect.render(start,palette,p)
                if prev is not None:
                    alpha=min(1,(start-change_time)/0.38); colors={k:mix(prev.get(k,(0,0,0)),colors.get(k,(0,0,0)),alpha) for k in colors}
                    if alpha>=1:
                        with self._lock: self._previous_colors=None
                for layer in layers:
                    if not layer.enabled or layer.opacity<=0: continue
                    rendered,keys=self._render_custom_layer(layer,start,p,audio_levels)
                    if rendered is None: continue
                    colors=self._blend_map(colors,rendered,keys,layer.opacity,layer.blend_mode)
                if audio_enabled: colors=self._quick_audio_overlay(colors,audio_levels,palette,p['audio_gain'],audio_mode)
                if overlay_enabled: colors=self._quick_overlay(colors,overlay_key_colors,overlay_keys,overlay_color,p['overlay_opacity'])
                if reactive_enabled: colors=self.reactive.apply(colors,start,color=reactive_color,strength=p['reactive_strength'],decay=p['reactive_decay'],radius_speed=p['reactive_speed'],mode=reactive_mode)
                br=max(0,min(1,p['brightness'])); final={k:tuple((clamp255(v*br) for v in c)) for k,c in colors.items()}
                if transition_from is not None and transition_duration>0:
                    alpha=min(1.0,(start-transition_started)/transition_duration); final={k:tuple((clamp255(v) for v in mix(transition_from.get(k,(0,0,0)),final.get(k,(0,0,0)),alpha))) for k in final}
                    if alpha>=1.0:
                        with self._lock: self._transition_from=None
                self.device.send_colors(final)
                with self._lock:
                    self.last_colors=final; self.last_error=None; self.frame_counter+=1
                stat_frames+=1; now=time.perf_counter()
                if now-last_stat>=1:
                    self.actual_fps=stat_frames/(now-last_stat); stat_frames=0; last_stat=now
                target=1/max(10,min(60,p['fps'])); spent=time.perf_counter()-start
                if spent<target: self._stop.wait(target-spent)
        except Exception as e:
            self.last_error=f'{type(e).__name__}: {e}'
        finally:
            self.running=False
