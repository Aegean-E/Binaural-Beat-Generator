"""Test utility functions from SourceCode.py."""

import unittest
import os
import sys
from unittest.mock import MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mock heavy dependencies before importing SourceCode
mock_scipy = MagicMock()
mock_scipy.io = MagicMock()
mock_scipy.signal = MagicMock()

MOCK_MODULES = {
    'numpy': MagicMock(),
    'scipy': mock_scipy,
    'sounddevice': MagicMock(),
    'tkinter': MagicMock(),
    'tkinter.ttk': MagicMock(),
    'ttkbootstrap': MagicMock(),
    'matplotlib': MagicMock(),
    'matplotlib.figure': MagicMock(),
    'matplotlib.backends': MagicMock(),
    'matplotlib.backends.backend_tkagg': MagicMock(),
}
for mod_name, mock_obj in MOCK_MODULES.items():
    if mod_name not in sys.modules:
        sys.modules[mod_name] = mock_obj

# Now we can import SourceCode
import SourceCode


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_clamp(self):
        """Test the clamp function."""
        self.assertEqual(SourceCode.clamp(5, 0, 10), 5)
        self.assertEqual(SourceCode.clamp(-5, 0, 10), 0)
        self.assertEqual(SourceCode.clamp(15, 0, 10), 10)
        self.assertEqual(SourceCode.clamp(0, 0, 10), 0)
        self.assertEqual(SourceCode.clamp(10, 0, 10), 10)

    def test_validate_audio_params_valid(self):
        """Test validate_audio_params with valid inputs."""
        self.assertIsNone(SourceCode.validate_audio_params(440.0, 450.0, 50.0, 50.0, 10.0))
        # Test edge cases
        self.assertIsNone(SourceCode.validate_audio_params(20.0, 20000.0, 0.0, 100.0, 0.1))

    def test_validate_audio_params_invalid_freq(self):
        """Test validate_audio_params with invalid frequencies."""
        self.assertIn("Frequency", SourceCode.validate_audio_params(19.9, 440.0, 50, 50))
        self.assertIn("Frequency", SourceCode.validate_audio_params(20000.1, 440.0, 50, 50))
        self.assertIn("Frequency", SourceCode.validate_audio_params(440.0, 19.9, 50, 50))
        self.assertIn("Frequency", SourceCode.validate_audio_params(440.0, 20000.1, 50, 50))

    def test_validate_audio_params_invalid_vol(self):
        """Test validate_audio_params with invalid volumes."""
        self.assertIn("Volume", SourceCode.validate_audio_params(440.0, 450.0, -0.1, 50))
        self.assertIn("Volume", SourceCode.validate_audio_params(440.0, 450.0, 100.1, 50))
        self.assertIn("Volume", SourceCode.validate_audio_params(440.0, 450.0, 50, -0.1))
        self.assertIn("Volume", SourceCode.validate_audio_params(440.0, 450.0, 50, 100.1))

    def test_validate_audio_params_invalid_duration(self):
        """Test validate_audio_params with invalid duration."""
        self.assertIn("Duration", SourceCode.validate_audio_params(440.0, 450.0, 50, 50, 0))
        self.assertIn("Duration", SourceCode.validate_audio_params(440.0, 450.0, 50, 50, -10.0))

    def test_compute_ramped_beat_hz(self):
        """Test _compute_ramped_beat_hz calculation."""
        # Test start of ramp
        self.assertAlmostEqual(
            SourceCode._compute_ramped_beat_hz(0.0, 20.0, 10.0, 60.0),
            20.0
        )
        # Test end of ramp
        self.assertAlmostEqual(
            SourceCode._compute_ramped_beat_hz(60.0, 20.0, 10.0, 60.0),
            10.0
        )
        # Test halfway through ramp
        self.assertAlmostEqual(
            SourceCode._compute_ramped_beat_hz(30.0, 20.0, 10.0, 60.0),
            15.0
        )
        # Test overshooting ramp duration (should clamp to end)
        self.assertAlmostEqual(
            SourceCode._compute_ramped_beat_hz(100.0, 20.0, 10.0, 60.0),
            10.0
        )
        # Test zero duration ramp (should return end_beat_hz)
        self.assertAlmostEqual(
            SourceCode._compute_ramped_beat_hz(10.0, 20.0, 10.0, 0.0),
            10.0
        )
        # Test ramp up
        self.assertAlmostEqual(
            SourceCode._compute_ramped_beat_hz(30.0, 10.0, 20.0, 60.0),
            15.0
        )


if __name__ == '__main__':
    unittest.main()