import unittest
import sys
import os
import importlib.machinery
import importlib.util
from unittest.mock import MagicMock

# 1. Mock external dependencies that might be missing or problematic
# We must do this BEFORE importing SourceCode

# Create a dummy numpy module
mock_numpy = MagicMock()
mock_numpy.pi = 3.14159
mock_numpy.float32 = float
sys.modules["numpy"] = mock_numpy

# Create dummy scipy
mock_scipy = MagicMock()
sys.modules["scipy"] = mock_scipy
sys.modules["scipy.signal"] = MagicMock()
sys.modules["scipy.io"] = MagicMock()
sys.modules["scipy.io.wavfile"] = MagicMock()

# Create dummy sounddevice
sys.modules["sounddevice"] = MagicMock()

# Create dummy ttkbootstrap
sys.modules["ttkbootstrap"] = MagicMock()

# Create dummy tkinter
# We always mock tkinter to prevent GUI windows from opening during tests
mock_tk = MagicMock()
# Explicitly set TclError so code catching it works
mock_tk.TclError = Exception
sys.modules["tkinter"] = mock_tk
sys.modules["tkinter.ttk"] = MagicMock()
sys.modules["tkinter.messagebox"] = MagicMock()
sys.modules["tkinter.filedialog"] = MagicMock()

def load_source_code():
    # Load the extensionless SourceCode file
    # Use path relative to this test file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    file_path = os.path.join(project_root, "SourceCode.py")

    # Ensure presets.py can be imported from project root
    if project_root not in sys.path:
        sys.path.append(project_root)

    loader = importlib.machinery.SourceFileLoader("SourceCode", file_path)
    spec = importlib.util.spec_from_loader("SourceCode", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

class TestBeatCalculation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the module once
        cls.module = load_source_code()

    def test_ramp_up(self):
        """Test increasing frequency ramp."""
        start = 5.0
        end = 10.0
        ramp_s = 100.0
        elapsed = 50.0  # Halfway
        expected = 7.5
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(elapsed, start, end, ramp_s), expected)

    def test_ramp_down(self):
        """Test decreasing frequency ramp."""
        start = 10.0
        end = 5.0
        ramp_s = 100.0
        elapsed = 50.0  # Halfway
        expected = 7.5
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(elapsed, start, end, ramp_s), expected)

    def test_constant_beat(self):
        """Test constant frequency (no change)."""
        start = 10.0
        end = 10.0
        ramp_s = 100.0
        elapsed = 50.0
        expected = 10.0
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(elapsed, start, end, ramp_s), expected)

    def test_elapsed_zero(self):
        """Test at t=0."""
        start = 5.0
        end = 10.0
        ramp_s = 100.0
        elapsed = 0.0
        expected = 5.0
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(elapsed, start, end, ramp_s), expected)

    def test_elapsed_negative(self):
        """Test at t<0 (should be clamped to start)."""
        start = 5.0
        end = 10.0
        ramp_s = 100.0
        elapsed = -10.0
        expected = 5.0
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(elapsed, start, end, ramp_s), expected)

    def test_elapsed_equals_duration(self):
        """Test at t=duration."""
        start = 5.0
        end = 10.0
        ramp_s = 100.0
        elapsed = 100.0
        expected = 10.0
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(elapsed, start, end, ramp_s), expected)

    def test_elapsed_exceeds_duration(self):
        """Test at t>duration (should be clamped to end)."""
        start = 5.0
        end = 10.0
        ramp_s = 100.0
        elapsed = 150.0
        expected = 10.0
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(elapsed, start, end, ramp_s), expected)

    def test_zero_ramp_duration(self):
        """Test ramp duration = 0 (immediate jump to end)."""
        start = 5.0
        end = 10.0
        ramp_s = 0.0
        elapsed = 50.0
        expected = 10.0
        self.assertEqual(self.module._compute_ramped_beat_hz(elapsed, start, end, ramp_s), expected)

    def test_negative_ramp_duration(self):
        """Test negative ramp duration (immediate jump to end)."""
        start = 5.0
        end = 10.0
        ramp_s = -10.0
        elapsed = 50.0
        expected = 10.0
        self.assertEqual(self.module._compute_ramped_beat_hz(elapsed, start, end, ramp_s), expected)

    def test_midpoint_linearity(self):
        """Test multiple points along the ramp for linearity."""
        start = 0.0
        end = 100.0
        ramp_s = 100.0

        for t in [10, 25, 50, 75, 90]:
            expected = float(t)
            self.assertAlmostEqual(self.module._compute_ramped_beat_hz(t, start, end, ramp_s), expected)

if __name__ == '__main__':
    unittest.main()
