"""Test AudioConfig dataclass and utility functions."""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mock dependencies before importing SourceCode
mock_numpy = MagicMock()
mock_numpy.pi = 3.14159
mock_numpy.float32 = float
mock_numpy.float64 = float
mock_numpy.sin = MagicMock()
mock_numpy.cos = MagicMock()
mock_numpy.tanh = MagicMock()
mock_numpy.clip = MagicMock()
mock_numpy.maximum = MagicMock()
mock_numpy.column_stack = MagicMock()
mock_numpy.concatenate = MagicMock()
mock_numpy.cumsum = MagicMock()
mock_numpy.full = MagicMock()
mock_numpy.sum = MagicMock()
mock_numpy.arange = MagicMock()
mock_numpy.abs = MagicMock()
mock_numpy.exp = MagicMock()
mock_numpy.mod = MagicMock()

mock_scipy = MagicMock()
mock_scipy.signal = MagicMock()
mock_scipy.io = MagicMock()
mock_scipy.io.wavfile = MagicMock()

mock_tk = MagicMock()
mock_tk.TclError = Exception

modules_to_patch = {
    'numpy': mock_numpy,
    'scipy': mock_scipy,
    'scipy.signal': MagicMock(),
    'scipy.io': MagicMock(),
    'scipy.io.wavfile': MagicMock(),
    'sounddevice': MagicMock(),
    'ttkbootstrap': MagicMock(),
    'tkinter': mock_tk,
    'tkinter.ttk': MagicMock(),
    'tkinter.messagebox': MagicMock(),
    'tkinter.filedialog': MagicMock(),
    'matplotlib': MagicMock(),
    'matplotlib.figure': MagicMock(),
    'matplotlib.backends': MagicMock(),
    'matplotlib.backends.backend_tkagg': MagicMock(),
}


class TestAudioConfig(unittest.TestCase):
    """Test AudioConfig dataclass."""
    
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch.dict(sys.modules, modules_to_patch)
        cls.patcher.start()
        import SourceCode as sc
        cls.sc = sc
    
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
    
    def test_audio_config_defaults(self):
        """Test AudioConfig default values."""
        cfg = self.sc.AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            noise_type="None",
            noise_volume=0.0,
            use_ramp=False,
            left_frequency=440.0,
            right_frequency=444.0,
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0
        )
        
        self.assertEqual(cfg.sample_rate, 44100)
        self.assertEqual(cfg.left_volume, 0.5)
        self.assertEqual(cfg.right_volume, 0.5)
        self.assertEqual(cfg.beat_type, "binaural")  # default
    
    def test_audio_config_isochronic(self):
        """Test AudioConfig with isochronic beat type."""
        cfg = self.sc.AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            noise_type="None",
            noise_volume=0.0,
            use_ramp=False,
            left_frequency=10.0,
            right_frequency=432.0,
            carrier_hz=432.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0,
            beat_type="isochronic"
        )
        
        self.assertEqual(cfg.beat_type, "isochronic")
        self.assertEqual(cfg.left_frequency, 10.0)  # pulse rate
        self.assertEqual(cfg.carrier_hz, 432.0)


class TestClampFunction(unittest.TestCase):
    """Test clamp utility function."""
    
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch.dict(sys.modules, modules_to_patch)
        cls.patcher.start()
        import SourceCode as sc
        cls.sc = sc
    
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
    
    def test_clamp_basic(self):
        """Test basic clamping."""
        self.assertEqual(self.sc.clamp(5, 0, 10), 5)
        self.assertEqual(self.sc.clamp(-5, 0, 10), 0)
        self.assertEqual(self.sc.clamp(15, 0, 10), 10)
    
    def test_clamp_edge_cases(self):
        """Test clamp edge cases."""
        self.assertEqual(self.sc.clamp(0, 0, 10), 0)
        self.assertEqual(self.sc.clamp(10, 0, 10), 10)
        self.assertEqual(self.sc.clamp(0, -10, -5), -5)


class TestRampCalculation(unittest.TestCase):
    """Test ramp computation function."""
    
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch.dict(sys.modules, modules_to_patch)
        cls.patcher.start()
        import SourceCode as sc
        cls.sc = sc
    
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
    
    def test_ramp_no_ramp(self):
        """Test ramp calculation when ramp is disabled (returns end_beat_hz)."""
        result = self.sc._compute_ramped_beat_hz(0, 10.0, 20.0, 0.0)
        self.assertEqual(result, 20.0)  # Returns end_beat_hz when ramp_s <= 0
    
    def test_ramp_linear(self):
        """Test linear ramp calculation."""
        # At halfway point, should be average
        result = self.sc._compute_ramped_beat_hz(30, 10.0, 20.0, 60.0)
        self.assertAlmostEqual(result, 15.0)
    
    def test_ramp_at_end(self):
        """Test ramp at end point."""
        result = self.sc._compute_ramped_beat_hz(60, 10.0, 20.0, 60.0)
        self.assertEqual(result, 20.0)
    
    def test_ramp_beyond_end(self):
        """Test ramp beyond duration."""
        result = self.sc._compute_ramped_beat_hz(100, 10.0, 20.0, 60.0)
        self.assertEqual(result, 20.0)


class TestValidation(unittest.TestCase):
    """Test validation functions."""
    
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch.dict(sys.modules, modules_to_patch)
        cls.patcher.start()
        import SourceCode as sc
        cls.sc = sc
    
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
    
    def test_validate_valid_params(self):
        """Test validation with valid parameters."""
        result = self.sc.validate_audio_params(440.0, 444.0, 50, 50)
        self.assertIsNone(result)
    
    def test_validate_invalid_left_freq(self):
        """Test validation with invalid left frequency."""
        result = self.sc.validate_audio_params(5.0, 444.0, 50, 50)
        self.assertIsNotNone(result)
    
    def test_validate_invalid_volume(self):
        """Test validation with invalid volume."""
        result = self.sc.validate_audio_params(440.0, 444.0, -10, 50)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
