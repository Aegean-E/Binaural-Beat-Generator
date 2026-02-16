import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch, mock_open

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

import importlib.machinery
import importlib.util

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

class TestSourceCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the module once
        cls.module = load_source_code()

    def test_normalize_category(self):
        # _normalize_category(category)
        self.assertEqual(self.module._normalize_category("binaural"), "Binaural")
        self.assertEqual(self.module._normalize_category("Binaural"), "Binaural")
        self.assertEqual(self.module._normalize_category(" monaural "), "Monaural")
        self.assertEqual(self.module._normalize_category("MONAURAL"), "Monaural")

        with self.assertRaises(ValueError):
            self.module._normalize_category("invalid")

    def test_compute_ramped_beat_hz(self):
        # _compute_ramped_beat_hz(elapsed_s, start_beat_hz, end_beat_hz, ramp_s)
        start = 10.0
        end = 5.0
        ramp_s = 100.0

        # At t=0, should be start
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(0, start, end, ramp_s), start)
        # At t=ramp_s, should be end
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(ramp_s, start, end, ramp_s), end)
        # At t=ramp_s/2, should be mid (linear interpolation)
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(ramp_s/2, start, end, ramp_s), 7.5)
        # At t>ramp_s, should be end (clamped)
        self.assertAlmostEqual(self.module._compute_ramped_beat_hz(ramp_s*2, start, end, ramp_s), end)

        # Test 0 duration
        self.assertEqual(self.module._compute_ramped_beat_hz(10, start, end, 0), end)

        # Test negative duration (should behave like 0 duration based on code logic 'if ramp_s <= 0: return end_beat_hz')
        self.assertEqual(self.module._compute_ramped_beat_hz(10, start, end, -10), end)

    def test_add_user_preset(self):
        # Setup initial config
        # We need to make sure we don't modify the global config permanently across tests
        # We'll save the original config and restore it after
        original_config = self.module.config

        test_config = {
            "user_presets": {
                "Monaural": [],
                "Binaural": []
            }
        }

        try:
            self.module.config = test_config

            with patch.object(self.module, 'save_config') as mock_save:
                # Add a preset
                self.module.add_user_preset("Binaural", "Test Preset", 100, 110)

                # Verify it was added to the in-memory config
                self.assertEqual(len(test_config["user_presets"]["Binaural"]), 1)
                self.assertEqual(test_config["user_presets"]["Binaural"][0]["label"], "Test Preset")
                self.assertEqual(test_config["user_presets"]["Binaural"][0]["left_hz"], 100.0)
                self.assertEqual(test_config["user_presets"]["Binaural"][0]["right_hz"], 110.0)

                # Verify save_config was called
                mock_save.assert_called_once()

                # Add invalid preset (empty label)
                with self.assertRaises(ValueError):
                    self.module.add_user_preset("Binaural", "", 100, 110)

                # Add invalid preset (bad number)
                with self.assertRaises(ValueError):
                    # Python's float("abc") raises ValueError, which is caught and re-raised as ValueError("Invalid numeric value for frequencies.")
                    self.module.add_user_preset("Binaural", "Bad", "abc", 110)

        finally:
            self.module.config = original_config

    def test_remove_user_preset(self):
        original_config = self.module.config

        test_config = {
            "user_presets": {
                "Monaural": [],
                "Binaural": [
                    {"label": "To Remove", "left_hz": 100, "right_hz": 110},
                    {"label": "Keep Me", "left_hz": 200, "right_hz": 210}
                ]
            }
        }

        try:
            self.module.config = test_config

            with patch.object(self.module, 'save_config') as mock_save:
                # Remove the preset
                result = self.module.remove_user_preset("Binaural", "To Remove")

                self.assertTrue(result)
                self.assertEqual(len(test_config["user_presets"]["Binaural"]), 1)
                self.assertEqual(test_config["user_presets"]["Binaural"][0]["label"], "Keep Me")
                mock_save.assert_called_once()

                # Try removing non-existent
                result = self.module.remove_user_preset("Binaural", "Non Existent")
                self.assertFalse(result)

                # Try removing from wrong category
                result = self.module.remove_user_preset("Monaural", "Keep Me")
                self.assertFalse(result)

        finally:
            self.module.config = original_config

    def test_get_all_presets(self):
        original_config = self.module.config
        test_config = {
            "user_presets": {
                "Monaural": [{"label": "User Mono", "left_hz": 1, "right_hz": 1}],
                "Binaural": [{"label": "User Bi", "left_hz": 2, "right_hz": 3}]
            }
        }

        try:
            self.module.config = test_config

            presets = self.module.get_all_presets()

            # Check Monaural
            # presets.MONAURAL_PRESETS has 2 items by default (based on file read earlier)
            # plus 1 user preset
            self.assertTrue(len(presets["Monaural"]) >= 3)
            user_mono = [p for p in presets["Monaural"] if p["label"] == "User Mono"]
            self.assertEqual(len(user_mono), 1)

            # Check Binaural
            # presets.BINAURAL_PRESETS has 6 items by default
            # plus 1 user preset
            self.assertTrue(len(presets["Binaural"]) >= 7)
            user_bi = [p for p in presets["Binaural"] if p["label"] == "User Bi"]
            self.assertEqual(len(user_bi), 1)

        finally:
            self.module.config = original_config

if __name__ == '__main__':
    unittest.main()
