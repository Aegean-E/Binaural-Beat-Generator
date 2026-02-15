import time
import numpy as np
import sounddevice as sd
from scipy import signal

class AudioEngine:
    def __init__(self):
        self.stream = None
        self.is_playing = False
        self.start_time = 0.0

        # Audio parameters
        self.sample_rate = 44100
        self.left_hz = 432.0
        self.right_hz = 432.0
        self.left_vol = 0.5
        self.right_vol = 0.5
        self.left_waveform = "Sine"
        self.right_waveform = "Sine"

        # Ramp parameters
        self.use_ramp = False
        self.ramp_carrier_hz = 432.0
        self.ramp_start_beat_hz = 20.0
        self.ramp_end_beat_hz = 3.0
        self.ramp_duration_s = 1800.0

        # Noise parameters
        self.noise_type = "None"  # "None", "White", "Pink", "Brown"
        self.noise_vol = 0.0
        self.noise_state = None  # For filtering state if needed

        # Internal state
        self.phase_l = 0.0
        self.phase_r = 0.0

        self.waveforms = {
            "Sine": np.sin,
            "Square": signal.square,
            "Sawtooth": signal.sawtooth,
        }

    def _clamp(self, value, lo, hi):
        return max(lo, min(hi, value))

    def _soft_limiter(self, stereo_audio: np.ndarray, drive: float = 2.5) -> np.ndarray:
        limited = np.tanh(stereo_audio * drive) / np.tanh(drive)
        # Avoid global peak normalization across the chunk which causes volume pumping.
        # Just hard clip at 1.0 if it still exceeds, though tanh shouldn't exceed much if input is reasonable.
        # But to be safe against float artifacts:
        np.clip(limited, -1.0, 1.0, out=limited)
        return limited

    def _compute_ramped_beat_hz(self, elapsed_s: float) -> float:
        if self.ramp_duration_s <= 0:
            return self.ramp_end_beat_hz
        x = self._clamp(elapsed_s / self.ramp_duration_s, 0.0, 1.0)
        return self.ramp_start_beat_hz + (self.ramp_end_beat_hz - self.ramp_start_beat_hz) * x

    def _generate_noise(self, frames):
        if self.noise_type == "White":
            return np.random.uniform(-1.0, 1.0, frames) * self.noise_vol
        elif self.noise_type == "Pink":
            # Simple 1/f approximation: filter white noise
            # We use a simple IIR filter for approximation.
            # Ideally we need state to be persistent, but for simplicity in this chunk-based
            # approach without complex state management, we might accept some discontinuity
            # or we need to store 'zi'.
            # Let's try to do it right with lfilter_zi.

            white = np.random.uniform(-1.0, 1.0, frames)
            b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
            a = [1.0, -2.494956002, 2.017265875, -0.522189400]

            if self.noise_state is None:
                self.noise_state = signal.lfilter_zi(b, a)

            pink, self.noise_state = signal.lfilter(b, a, white, zi=self.noise_state)
            return pink * self.noise_vol * 10.0 # Adjust gain

        elif self.noise_type == "Brown":
            # Brown noise is integrated white noise (random walk)
            white = np.random.uniform(-1.0, 1.0, frames)
            # Leaky integrator
            b = [0.02]
            a = [1.0, -0.98]

            if self.noise_state is None:
                self.noise_state = signal.lfilter_zi(b, a)

            brown, self.noise_state = signal.lfilter(b, a, white, zi=self.noise_state)
            return brown * self.noise_vol * 5.0

        return np.zeros(frames)

    def _callback(self, outdata, frames, _time_info, status):
        if status:
            pass # In a real app we might log this

        now = time.time()
        elapsed = now - self.start_time

        # Determine current frequencies
        if self.use_ramp:
            beat_hz = self._compute_ramped_beat_hz(elapsed)
            lf = self.ramp_carrier_hz - (beat_hz / 2.0)
            rf = self.ramp_carrier_hz + (beat_hz / 2.0)
        else:
            lf = self.left_hz
            rf = self.right_hz

        lf = max(0.0, float(lf))
        rf = max(0.0, float(rf))

        t = np.arange(frames, dtype=np.float64) / self.sample_rate

        # Left Channel
        wl = 2.0 * np.pi * lf
        phase_vec_l = self.phase_l + wl * t
        left_signal = self.left_vol * self.waveforms[self.left_waveform](phase_vec_l)
        self.phase_l = (self.phase_l + wl * (frames / self.sample_rate)) % (2.0 * np.pi)

        # Right Channel
        wr = 2.0 * np.pi * rf
        phase_vec_r = self.phase_r + wr * t
        right_signal = self.right_vol * self.waveforms[self.right_waveform](phase_vec_r)
        self.phase_r = (self.phase_r + wr * (frames / self.sample_rate)) % (2.0 * np.pi)

        # Noise
        noise = self._generate_noise(frames)

        # Mix noise (add to both channels)
        left_signal += noise
        right_signal += noise

        stereo = np.column_stack((left_signal, right_signal))
        stereo = self._soft_limiter(stereo).astype(np.float32, copy=False)

        outdata[:] = stereo

    def start(self,
              left_hz, right_hz,
              left_vol, right_vol,
              left_waveform, right_waveform,
              use_ramp=False,
              ramp_carrier_hz=432.0,
              ramp_start_beat_hz=20.0,
              ramp_end_beat_hz=3.0,
              ramp_duration_s=1800.0,
              noise_type="None",
              noise_vol=0.0):

        self.stop() # Stop existing stream if any

        self.left_hz = left_hz
        self.right_hz = right_hz
        self.left_vol = left_vol
        self.right_vol = right_vol
        self.left_waveform = left_waveform
        self.right_waveform = right_waveform

        self.use_ramp = use_ramp
        self.ramp_carrier_hz = ramp_carrier_hz
        self.ramp_start_beat_hz = ramp_start_beat_hz
        self.ramp_end_beat_hz = ramp_end_beat_hz
        self.ramp_duration_s = ramp_duration_s

        self.noise_type = noise_type
        self.noise_vol = noise_vol
        self.noise_state = None # Reset noise filter state

        self.phase_l = 0.0
        self.phase_r = 0.0
        self.start_time = time.time()
        self.is_playing = True

        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=2,
                dtype="float32",
                callback=self._callback,
                blocksize=0 # let backend decide
            )
            self.stream.start()
        except Exception as e:
            self.is_playing = False
            raise e

    def stop(self):
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        self.is_playing = False

    def get_status(self):
        if not self.is_playing:
            return None

        elapsed = time.time() - self.start_time
        if self.use_ramp:
            beat = self._compute_ramped_beat_hz(elapsed)
            lf = self.ramp_carrier_hz - (beat / 2.0)
            rf = self.ramp_carrier_hz + (beat / 2.0)
            return {
                "elapsed": elapsed,
                "beat_hz": beat,
                "left_hz": lf,
                "right_hz": rf,
                "is_ramp": True,
                "ramp_duration": self.ramp_duration_s
            }
        else:
            beat = abs(self.right_hz - self.left_hz)
            return {
                "elapsed": elapsed,
                "beat_hz": beat,
                "left_hz": self.left_hz,
                "right_hz": self.right_hz,
                "is_ramp": False
            }
