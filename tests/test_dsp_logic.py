import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os
import importlib.machinery
import importlib.util

# Mock dependencies before import
sys.path.append(os.getcwd())
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.simpledialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()
sys.modules['scipy.io'] = MagicMock()
sys.modules['scipy.io.wavfile'] = MagicMock()

# Mock numpy
mock_np = MagicMock()
sys.modules['numpy'] = mock_np

# Mock waveforms to return a mock
mock_waveform = MagicMock()
# We need to set this after import or use patch.
# But SourceCode accesses waveforms dict at module level (class uses it).
# The class BinauralGenerator uses `waveforms.get`.
# So we can patch `SourceCode.waveforms` later.

# Load SourceCode
try:
    loader = importlib.machinery.SourceFileLoader('SourceCode', 'SourceCode')
    spec = importlib.util.spec_from_loader(loader.name, loader)
    source_code = importlib.util.module_from_spec(spec)
    sys.modules["SourceCode"] = source_code
    loader.exec_module(source_code)
except Exception as e:
    print(f"Error loading SourceCode: {e}")
    sys.exit(1)

class TestDSPLogic(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        mock_np.reset_mock()
        # Patch waveforms
        source_code.waveforms = {"Sine": MagicMock(return_value=MagicMock())}

    def test_fade_in_invoked(self):
        # Configure minimal config
        cfg = source_code.AudioConfig(
            sample_rate=44100,
            left_volume=1.0, right_volume=1.0,
            left_waveform="Sine", right_waveform="Sine",
            use_ramp=False,
            left_frequency=100, right_frequency=100,
            carrier_hz=0, start_beat_hz=0, end_beat_hz=0, ramp_duration_s=0
        )
        gen = source_code.BinauralGenerator(cfg)

        # Mock what np.clip returns so we can check if it was multiplied
        # generate_block -> stereo = np.clip(...)
        mock_stereo = MagicMock()
        mock_np.clip.return_value = mock_stereo

        # Also mock astype
        mock_stereo.astype.return_value = mock_stereo

        # Call generate
        gen.generate_block(100)

        # Check if inplace multiplication was called on mock_stereo
        # This confirms that "stereo *= ramp" was executed
        # Note: Depending on implementation, it might be __imul__ or __mul__
        calls = mock_stereo.mock_calls
        # Look for __imul__ or __mul__
        has_mul = any(name in ('__imul__', '__mul__') for name, args, kwargs in calls)
        self.assertTrue(has_mul, "Fade logic should multiply stereo array")

    def test_fade_out_invoked(self):
        cfg = source_code.AudioConfig(
            sample_rate=44100,
            left_volume=1.0, right_volume=1.0,
            left_waveform="Sine", right_waveform="Sine",
            use_ramp=False,
            left_frequency=100, right_frequency=100,
            carrier_hz=0, start_beat_hz=0, end_beat_hz=0, ramp_duration_s=0
        )
        gen = source_code.BinauralGenerator(cfg)

        # Advance past fade in
        gen.samples_generated = 2000 # > 882

        # No fade in should happen now.
        mock_stereo = MagicMock()
        mock_np.clip.return_value = mock_stereo
        mock_stereo.astype.return_value = mock_stereo

        gen.generate_block(100)
        # Verify NO mul (since fade in done and not stopping)
        calls = mock_stereo.mock_calls
        has_mul = any(name in ('__imul__', '__mul__') for name, args, kwargs in calls)
        self.assertFalse(has_mul, "No fade should happen in steady state")

        # Request stop
        gen.request_stop()

        # Reset mocks
        mock_stereo.reset_mock()

        gen.generate_block(100)

        # Verify mul (fade out)
        calls = mock_stereo.mock_calls
        has_mul = any(name in ('__imul__', '__mul__') for name, args, kwargs in calls)
        self.assertTrue(has_mul, "Fade out logic should multiply stereo array when stopping")

if __name__ == '__main__':
    unittest.main()
