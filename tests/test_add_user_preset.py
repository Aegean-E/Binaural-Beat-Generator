import unittest
import sys
import os
import json
import importlib.machinery
import importlib.util
from unittest.mock import MagicMock, patch

# Mock dependencies before import to avoid errors
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()

# Ensure local imports work (for presets.py)
sys.path.append(os.getcwd())

# Helper to load the extensionless SourceCode module
def load_source_code():
    module_name = 'SourceCode'
    # Try current directory first
    if os.path.exists(module_name):
        file_path = os.path.abspath(module_name)
    elif os.path.exists(os.path.join('..', module_name)):
        file_path = os.path.abspath(os.path.join('..', module_name))
    else:
        # Fallback to absolute path search or assume it's in current dir
        file_path = os.path.abspath(module_name)

    loader = importlib.machinery.SourceFileLoader(module_name, file_path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    # Register in sys.modules so patch can find it
    sys.modules[module_name] = module
    loader.exec_module(module)
    return module

try:
    source_code = load_source_code()
except Exception as e:
    print(f"Error loading SourceCode: {e}")
    sys.exit(1)

class TestAddUserPreset(unittest.TestCase):
    def setUp(self):
        # Save original config to restore later
        self.original_config = source_code.config

        # Create a fresh test config structure
        self.test_config = {
            "user_presets": {
                "Monaural": [],
                "Binaural": []
            }
        }
        # Inject the test config into the module
        source_code.config = self.test_config

    def tearDown(self):
        # Restore original config
        source_code.config = self.original_config

    @patch('SourceCode.save_config')
    def test_add_user_preset_success_binaural(self, mock_save_config):
        """Test adding a valid Binaural preset."""
        source_code.add_user_preset("Binaural", "My Preset", 100.0, 110.0)

        self.assertEqual(len(self.test_config["user_presets"]["Binaural"]), 1)
        preset = self.test_config["user_presets"]["Binaural"][0]
        self.assertEqual(preset["label"], "My Preset")
        self.assertEqual(preset["left_hz"], 100.0)
        self.assertEqual(preset["right_hz"], 110.0)

        mock_save_config.assert_called_once_with(self.test_config)

    @patch('SourceCode.save_config')
    def test_add_user_preset_success_monaural(self, mock_save_config):
        """Test adding a valid Monaural preset."""
        source_code.add_user_preset("Monaural", "Mono Preset", 432.0, 432.0)

        self.assertEqual(len(self.test_config["user_presets"]["Monaural"]), 1)
        preset = self.test_config["user_presets"]["Monaural"][0]
        self.assertEqual(preset["label"], "Mono Preset")
        self.assertEqual(preset["left_hz"], 432.0)
        self.assertEqual(preset["right_hz"], 432.0)

        mock_save_config.assert_called_once_with(self.test_config)

    @patch('SourceCode.save_config')
    def test_add_user_preset_category_normalization(self, mock_save_config):
        """Test that category string is normalized (case insensitive, stripped)."""
        # " binaural " -> "Binaural"
        source_code.add_user_preset(" binaural ", "Preset 1", 100, 110)
        self.assertEqual(len(self.test_config["user_presets"]["Binaural"]), 1)

        # "MONAURAL" -> "Monaural"
        source_code.add_user_preset("MONAURAL", "Preset 2", 200, 200)
        self.assertEqual(len(self.test_config["user_presets"]["Monaural"]), 1)

    @patch('SourceCode.save_config')
    def test_add_user_preset_label_strip(self, mock_save_config):
        """Test that label is stripped of leading/trailing whitespace."""
        source_code.add_user_preset("Binaural", "  Spaced Label  ", 100, 110)

        preset = self.test_config["user_presets"]["Binaural"][0]
        self.assertEqual(preset["label"], "Spaced Label")

    @patch('SourceCode.save_config')
    def test_add_user_preset_string_frequency(self, mock_save_config):
        """Test that string frequencies are converted to float."""
        source_code.add_user_preset("Binaural", "String Freq", "100.5", "110.5")

        preset = self.test_config["user_presets"]["Binaural"][0]
        self.assertIsInstance(preset["left_hz"], float)
        self.assertIsInstance(preset["right_hz"], float)
        self.assertEqual(preset["left_hz"], 100.5)
        self.assertEqual(preset["right_hz"], 110.5)

    def test_add_user_preset_invalid_category(self):
        """Test that invalid category raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            source_code.add_user_preset("Invalid", "Label", 100, 110)
        self.assertIn("Category must be 'Monaural' or 'Binaural'", str(cm.exception))

    def test_add_user_preset_empty_label(self):
        """Test that empty label raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            source_code.add_user_preset("Binaural", "   ", 100, 110)
        self.assertIn("Preset Name Cannot be Empty", str(cm.exception))

    def test_add_user_preset_invalid_frequency(self):
        """Test that invalid numeric values for frequency raise ValueError."""
        with self.assertRaises(ValueError) as cm:
            source_code.add_user_preset("Binaural", "Label", "abc", 110)
        self.assertIn("Invalid numeric value for frequencies", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
