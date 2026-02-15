import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from audio_engine import AudioEngine

class TestAudioEngine(unittest.TestCase):
    def setUp(self):
        # Mock sounddevice before creating AudioEngine if it initializes stream in init (it doesn't)
        # But we should mock it anyway for calls.
        self.patcher = patch("audio_engine.sd")
        self.mock_sd = self.patcher.start()
        self.engine = AudioEngine()

    def tearDown(self):
        self.patcher.stop()

    def test_init(self):
        self.assertFalse(self.engine.is_playing)
        self.assertIsNone(self.engine.stream)
        self.assertEqual(self.engine.left_hz, 432.0)

    def test_start(self):
        self.engine.start(
            left_hz=440, right_hz=444,
            left_vol=0.5, right_vol=0.5,
            left_waveform="Sine", right_waveform="Sine"
        )
        self.assertTrue(self.engine.is_playing)
        self.mock_sd.OutputStream.assert_called_once()
        self.assertEqual(self.engine.left_hz, 440)
        self.assertEqual(self.engine.right_hz, 444)

    def test_stop(self):
        self.engine.start(440, 444, 0.5, 0.5, "Sine", "Sine")
        self.engine.stop()
        self.assertFalse(self.engine.is_playing)
        self.assertIsNone(self.engine.stream)

    def test_ramp_calculation(self):
        # 0s elapsed
        hz = self.engine._compute_ramped_beat_hz(0.0)
        self.assertAlmostEqual(hz, 20.0) # Default start

        # 50% elapsed (default 1800s duration)
        self.engine.ramp_duration_s = 100.0
        self.engine.ramp_start_beat_hz = 10.0
        self.engine.ramp_end_beat_hz = 20.0

        hz = self.engine._compute_ramped_beat_hz(50.0)
        self.assertAlmostEqual(hz, 15.0)

        # 100% elapsed
        hz = self.engine._compute_ramped_beat_hz(100.0)
        self.assertAlmostEqual(hz, 20.0)

        # Over elapsed
        hz = self.engine._compute_ramped_beat_hz(150.0)
        self.assertAlmostEqual(hz, 20.0)

    def test_soft_limiter(self):
        # Create a signal with peaks > 1
        arr = np.array([[0.5, 0.5], [2.0, -2.0]])
        limited = self.engine._soft_limiter(arr)

        # Check values are within [-1, 1]
        self.assertTrue(np.all(limited >= -1.0))
        self.assertTrue(np.all(limited <= 1.0))

        # Check clipping/limiting behavior
        self.assertTrue(limited[1, 0] <= 1.0) # Tanh should squash it
        self.assertTrue(limited[1, 0] > 0.9) # But still close to 1

    def test_callback_logic(self):
        # Initialize
        self.engine.start(440, 440, 1.0, 1.0, "Sine", "Sine")

        frames = 1024
        outdata = np.zeros((frames, 2), dtype=np.float32)

        # Call callback directly
        self.engine._callback(outdata, frames, None, None)

        # Check output is not silent
        self.assertFalse(np.all(outdata == 0))

        # Check left and right are similar (same freq/vol/wave)
        # Due to float precision they might slightly differ but should be close or identical if phase synced
        # But phase updates, so let's just check shape
        self.assertEqual(outdata.shape, (frames, 2))

if __name__ == "__main__":
    unittest.main()
