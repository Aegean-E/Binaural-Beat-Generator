import unittest
import sys
import os
import importlib.machinery
import importlib.util
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.simpledialog'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()
sys.modules['scipy.io'] = MagicMock()
sys.modules['scipy.io.wavfile'] = MagicMock()

# Mock numpy
mock_np = MagicMock()
sys.modules['numpy'] = mock_np

# Setup numpy mocks to return usable objects
mock_np.float32 = float
mock_np.float64 = float
mock_np.pi = 3.14159
mock_np.arange.return_value = MagicMock() # Represents array
mock_np.sin.return_value = MagicMock()
mock_np.tanh.return_value = MagicMock()
mock_np.clip.return_value = MagicMock()
mock_np.column_stack.return_value = MagicMock() # Represents stereo array
mock_np.concatenate.return_value = MagicMock()
mock_np.maximum.return_value = MagicMock()
mock_np.cumsum.return_value = MagicMock()
mock_np.full.return_value = MagicMock()
mock_np.sum.return_value = 0.0

# Load SourceCode
# Use importlib.util to load extensionless file
try:
    loader = importlib.machinery.SourceFileLoader('SourceCode', 'SourceCode')
    spec = importlib.util.spec_from_loader(loader.name, loader)
    sc = importlib.util.module_from_spec(spec)
    sys.modules["SourceCode"] = sc
    loader.exec_module(sc)
except Exception as e:
    print(f"Error importing SourceCode: {e}")
    sys.exit(1)

class TestBinauralGenerator(unittest.TestCase):
    def setUp(self):
        # Patch waveforms
        sc.waveforms = {"Sine": MagicMock(return_value=MagicMock())}

        self.cfg = sc.AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            use_ramp=False,
            left_frequency=440.0,
            right_frequency=444.0,
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0
        )
        # Reset mocks
        mock_np.arange.reset_mock()
        mock_np.sin.reset_mock()
        mock_np.clip.reset_mock()
        mock_np.cumsum.reset_mock()
        mock_np.full.reset_mock()

    def test_initialization(self):
        gen = sc.BinauralGenerator(self.cfg)
        self.assertEqual(gen.samples_generated, 0)
        self.assertEqual(gen.phase_l, 0.0)
        self.assertEqual(gen.phase_r, 0.0)

    def test_generate_block_manual(self):
        gen = sc.BinauralGenerator(self.cfg)
        frames = 1024

        # Call generate
        output = gen.generate_block(frames)

        # Verify sample count incremented
        self.assertEqual(gen.samples_generated, frames)

        # Verify optimization: cumsum should NOT be called
        mock_np.cumsum.assert_not_called()

        # Verify arange was called (for t_vec)
        self.assertTrue(mock_np.arange.called)

        # Verify clip was called (stateless limiter + fades)
        mock_np.clip.assert_called()

    def test_generate_block_ramp(self):
        self.cfg.use_ramp = True
        self.cfg.ramp_duration_s = 60.0
        self.cfg.start_beat_hz = 10.0
        self.cfg.end_beat_hz = 5.0
        self.cfg.carrier_hz = 200.0

        gen = sc.BinauralGenerator(self.cfg)
        frames = 44100 # 1 second

        mock_cumsum_ret = MagicMock()
        mock_np.cumsum.return_value = mock_cumsum_ret
        mock_cumsum_ret.__getitem__.return_value = MagicMock()

        gen.generate_block(frames)

        # Check samples
        self.assertEqual(gen.samples_generated, 44100)

        # Verify cumsum WAS called (ramp logic uses it)
        self.assertTrue(mock_np.cumsum.called)

        # Call again
        gen.generate_block(frames)
        self.assertEqual(gen.samples_generated, 88200)

if __name__ == '__main__':
    unittest.main()
