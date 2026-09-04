import threading
import time


class SystemAudioMeter:
    """
    WASAPI loopback meter:
      bass, mid, high, level, beat  -> all 0..1
    """
    def __init__(self):
        self._thread = None
        self._stop = threading.Event()
        self._lock = threading.RLock()
        self._levels = (0, 0, 0, 0, 0)
        self.error = None

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def levels(self):
        with self._lock:
            return self._levels

    def start(self):
        if self.running:
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="BladeRGB-Audio",
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None

    def _run(self):
        try:
            import numpy as np
            import soundcard as sc

            speaker = sc.default_speaker()
            mic = sc.get_microphone(
                id=str(speaker.name),
                include_loopback=True,
            )

            sr = 44100
            n = 2048
            previous_bass = 0.0
            beat_decay = 0.0

            with mic.recorder(
                samplerate=sr,
                channels=2,
                blocksize=n,
            ) as rec:
                while not self._stop.is_set():
                    data = rec.record(numframes=n)
                    if data is None or len(data) == 0:
                        continue

                    mono = np.mean(data, axis=1).astype(np.float32)
                    mono -= np.mean(mono)

                    rms = float(np.sqrt(np.mean(mono * mono)))
                    spec = np.abs(np.fft.rfft(mono * np.hanning(len(mono))))
                    freqs = np.fft.rfftfreq(len(mono), 1 / sr)

                    def band(lo, hi):
                        mask = (freqs >= lo) & (freqs < hi)
                        if not np.any(mask):
                            return 0.0
                        return float(np.mean(spec[mask]))

                    bass_raw = min(1, band(35, 180) / 9)
                    mid_raw = min(1, band(180, 2000) / 4.5)
                    high_raw = min(1, band(2000, 10000) / 2.2)
                    level_raw = min(1, rms * 14)

                    delta = max(0.0, bass_raw - previous_bass * 0.86)
                    previous_bass = previous_bass * 0.65 + bass_raw * 0.35
                    beat_decay = max(beat_decay * 0.78, min(1.0, delta * 3.5))

                    with self._lock:
                        ob, om, oh, ol, obt = self._levels
                        a = 0.32
                        self._levels = (
                            ob * (1-a) + bass_raw * a,
                            om * (1-a) + mid_raw * a,
                            oh * (1-a) + high_raw * a,
                            ol * (1-a) + level_raw * a,
                            max(obt * 0.72, beat_decay),
                        )

                    self.error = None

        except Exception as e:
            self.error = str(e)

        finally:
            with self._lock:
                self._levels = (0, 0, 0, 0, 0)
