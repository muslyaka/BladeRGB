import threading
import hid
from .layout import KEY_OFFSETS
from .protocol import VID,PID,USAGE_PAGE,USAGE,INTERFACE,build_frame,make_manual_mode_packet,write_frame

class BladeDevice:
    def __init__(self, inter_report_delay=0.001):
        self._dev=None
        self._lock=threading.RLock()
        self.path=None
        self.inter_report_delay=float(inter_report_delay)

    @property
    def connected(self): return self._dev is not None

    @staticmethod
    def find():
        for d in hid.enumerate(VID,PID):
            if (d.get("interface_number")==INTERFACE and
                d.get("usage_page")==USAGE_PAGE and
                d.get("usage")==USAGE):
                return d
        return None

    def connect(self):
        with self._lock:
            if self.connected: return
            info=self.find()
            if not info:
                raise RuntimeError("Не найден RGB HID 0416:C345 / MI_02 / FF1B:0091")
            dev=hid.device()
            dev.open_path(info["path"])
            self._dev=dev
            self.path=info["path"]

    def enable_manual_mode(self):
        with self._lock:
            if not self.connected: raise RuntimeError("Клавиатура не подключена")
            return self._dev.write(make_manual_mode_packet())

    @staticmethod
    def _c(v): return max(0,min(255,int(round(v))))

    def colors_to_frame(self, colors):
        f=build_frame()
        for key,c in colors.items():
            a=KEY_OFFSETS.get(key)
            if a is None: continue
            r,g,b=c
            f[a-1]=self._c(r); f[a]=self._c(g); f[a+1]=self._c(b)
        return f

    def send_colors(self, colors):
        with self._lock:
            if not self.connected: raise RuntimeError("Клавиатура не подключена")
            return write_frame(self._dev,self.colors_to_frame(colors),self.inter_report_delay)

    def blackout(self):
        self.send_colors({k:(0,0,0) for k in KEY_OFFSETS})

    def close(self):
        with self._lock:
            if self._dev is not None:
                try: self._dev.close()
                finally:
                    self._dev=None
                    self.path=None
