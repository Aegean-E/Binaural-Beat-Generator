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
    file_path = os.path.join(project_root, "SourceCode")

    # Ensure presets.py can be imported from project root
    if project_root not in sys.path:
        sys.path.append(project_root)

    loader = importlib.machinery.SourceFileLoader("SourceCode", file_path)
    spec = importlib.util.spec_from_loader("SourceCode", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

class TestClamp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the module once
        cls.module = load_source_code()

    def clamp(self, *args):
        return self.module.clamp(*args)

    def test_basic_usage(self):
        """Test clamp works for normal ranges."""
        self.assertEqual(self.clamp(5, 0, 10), 5)
        self.assertEqual(self.clamp(5, 0, 10), 5)

    def test_lower_bound(self):
        """Test clamp handles values below lower bound."""
        self.assertEqual(self.clamp(-1, 0, 10), 0)
        self.assertEqual(self.clamp(-100, 0, 10), 0)

    def test_upper_bound(self):
        """Test clamp handles values above upper bound."""
        self.assertEqual(self.clamp(11, 0, 10), 10)
        self.assertEqual(self.clamp(100, 0, 10), 10)

    def test_boundary_conditions(self):
        """Test clamp exactly at the boundaries."""
        self.assertEqual(self.clamp(0, 0, 10), 0)
        self.assertEqual(self.clamp(10, 0, 10), 10)

    def test_floating_point(self):
        """Test clamp works with floats."""
        self.assertEqual(self.clamp(5.5, 0.0, 10.0), 5.5)
        self.assertEqual(self.clamp(-0.1, 0.0, 1.0), 0.0)
        self.assertEqual(self.clamp(1.1, 0.0, 1.0), 1.0)
        # Verify precision (basic)
        self.assertAlmostEqual(self.clamp(1.0/3.0, 0.0, 1.0), 0.3333333333333333)

    def test_negative_ranges(self):
        """Test clamp works with negative ranges."""
        self.assertEqual(self.clamp(-5, -10, -1), -5)
        self.assertEqual(self.clamp(-11, -10, -1), -10)
        self.assertEqual(self.clamp(0, -10, -1), -1)

    def test_lo_equals_hi(self):
        """Test clamp when lo == hi."""
        self.assertEqual(self.clamp(5, 10, 10), 10)
        self.assertEqual(self.clamp(10, 10, 10), 10)
        self.assertEqual(self.clamp(15, 10, 10), 10)

    def test_lo_greater_than_hi(self):
        """Test edge case where lo > hi.
        Current implementation returns lo because max(lo, min(hi, val)) returns lo if lo > hi.
        """
        # If lo > hi, current implementation always returns lo.
        # This behavior is documented here.
        lo = 10
        hi = 0
        self.assertEqual(self.clamp(5, lo, hi), lo)   # min(0, 5)=0, max(10, 0)=10
        self.assertEqual(self.clamp(-5, lo, hi), lo)  # min(0, -5)=-5, max(10, -5)=10
        self.assertEqual(self.clamp(15, lo, hi), lo)  # min(0, 15)=0, max(10, 0)=10

if __name__ == '__main__':
    unittest.main()
