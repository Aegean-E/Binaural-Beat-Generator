"""Test presets module."""

import unittest
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import presets


class TestPresets(unittest.TestCase):
    """Test preset data structures."""
    
    def test_monaural_presets_structure(self):
        """Test monaural presets have required fields."""
        for p in presets.MONAURAL_PRESETS:
            self.assertIn("label", p)
            self.assertIn("left_hz", p)
            self.assertIn("right_hz", p)
            self.assertIsInstance(p["label"], str)
            self.assertIsInstance(p["left_hz"], (int, float))
            self.assertIsInstance(p["right_hz"], (int, float))
    
    def test_binaural_presets_structure(self):
        """Test binaural presets have required fields."""
        for p in presets.BINAURAL_PRESETS:
            self.assertIn("label", p)
            self.assertIn("left_hz", p)
            self.assertIn("right_hz", p)
            self.assertIsInstance(p["label"], str)
            self.assertIsInstance(p["left_hz"], (int, float))
            self.assertIsInstance(p["right_hz"], (int, float))
    
    def test_isochronic_presets_structure(self):
        """Test isochronic presets have required fields."""
        for p in presets.ISOCHRONIC_PRESETS:
            self.assertIn("label", p)
            self.assertIn("carrier_hz", p)
            self.assertIn("pulse_hz", p)
            self.assertIsInstance(p["label"], str)
            self.assertIsInstance(p["carrier_hz"], (int, float))
            self.assertIsInstance(p["pulse_hz"], (int, float))
    
    def test_brainwave_ranges(self):
        """Test brainwave ranges are defined."""
        self.assertIn("Delta (0.5 - 4 Hz)", presets.BRAINWAVE_RANGES)
        self.assertIn("Theta (4 - 8 Hz)", presets.BRAINWAVE_RANGES)
        self.assertIn("Alpha (8 - 12 Hz)", presets.BRAINWAVE_RANGES)
        self.assertIn("Beta (12 - 30 Hz)", presets.BRAINWAVE_RANGES)
        self.assertIn("Gamma (30 - 80 Hz)", presets.BRAINWAVE_RANGES)
    
    def test_frequency_ranges_valid(self):
        """Test brainwave frequency ranges are valid."""
        for name, (low, high) in presets.BRAINWAVE_RANGES.items():
            self.assertLess(low, high, f"{name} has invalid range")
            self.assertGreater(low, 0, f"{name} has invalid low frequency")
    
    def test_presets_not_empty(self):
        """Test all preset lists are populated."""
        self.assertGreater(len(presets.MONAURAL_PRESETS), 0)
        self.assertGreater(len(presets.BINAURAL_PRESETS), 0)
        self.assertGreater(len(presets.ISOCHRONIC_PRESETS), 0)


if __name__ == '__main__':
    unittest.main()
