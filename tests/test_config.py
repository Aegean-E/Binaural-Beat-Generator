"""Test configuration management functions."""

import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mock heavy dependencies before importing SourceCode
mock_scipy = MagicMock()
mock_scipy.io = MagicMock()
mock_scipy.signal = MagicMock()

MOCK_MODULES = {
    'sounddevice': MagicMock(),
    'tkinter': MagicMock(),
    'tkinter.ttk': MagicMock(),
    'ttkbootstrap': MagicMock(),
}
for mod_name, mock_obj in MOCK_MODULES.items():
    if mod_name not in sys.modules:
        sys.modules[mod_name] = mock_obj

# Now we can import SourceCode
import SourceCode


class TestConfig(unittest.TestCase):
    """Test configuration management functions."""

    def setUp(self):
        """Patch the config object for each test."""
        # We patch 'SourceCode.config' to isolate tests from each other
        # and from the actual file system.
        self.config_patcher = patch('SourceCode.config', {})
        self.mock_config = self.config_patcher.start()

        # We also need to patch save_config to see what it writes
        self.save_config_patcher = patch('SourceCode.save_config')
        self.mock_save_config = self.save_config_patcher.start()

    def tearDown(self):
        self.config_patcher.stop()
        self.save_config_patcher.stop()

    def test_normalize_category(self):
        """Test _normalize_category function."""
        self.assertEqual(SourceCode._normalize_category("binaural"), "Binaural")
        self.assertEqual(SourceCode._normalize_category("Monaural Beat"), "Binaural")
        self.assertEqual(SourceCode._normalize_category(" isochronic "), "Isochronic")
        with self.assertRaises(ValueError):
            SourceCode._normalize_category("invalid")

    def test_get_user_presets_empty(self):
        """Test get_user_presets with an empty config."""
        self.mock_config.clear()
        presets = SourceCode.get_user_presets()
        self.assertEqual(presets, {"Monaural": [], "Binaural": [], "Isochronic": []})

    def test_get_user_presets_populated(self):
        """Test get_user_presets with a populated config."""
        self.mock_config['user_presets'] = {
            "Binaural": [{"label": "test", "left_hz": 100, "right_hz": 110}],
            "Monaural": [],
        }
        presets = SourceCode.get_user_presets()
        self.assertEqual(presets, {
            "Binaural": [{"label": "test", "left_hz": 100, "right_hz": 110}],
            "Monaural": [],
            "Isochronic": [],
        })

    def test_add_user_preset(self):
        """Test adding a new user preset."""
        self.mock_config.clear()

        SourceCode.add_user_preset(
            category="Binaural",
            label="My Preset",
            left_hz=432.0,
            right_hz=442.0
        )

        # The function should have updated the in-memory config and called save_config
        self.assertIn("user_presets", self.mock_config)
        self.assertIn("Binaural", self.mock_config["user_presets"])
        self.assertEqual(len(self.mock_config["user_presets"]["Binaural"]), 1)
        self.assertEqual(self.mock_config["user_presets"]["Binaural"][0], {
            "label": "My Preset",
            "left_hz": 432.0,
            "right_hz": 442.0,
        })
        self.mock_save_config.assert_called_once_with(self.mock_config)

    def test_add_user_preset_invalid_values(self):
        """Test adding a preset with invalid numeric values."""
        with self.assertRaisesRegex(ValueError, "Invalid numeric value for frequencies."):
            SourceCode.add_user_preset("Binaural", "Test", "not-a-float", 440.0)

    def test_add_user_preset_empty_label(self):
        """Test adding a preset with an empty label."""
        with self.assertRaisesRegex(ValueError, "Preset Name Cannot be Empty"):
            SourceCode.add_user_preset("Binaural", "  ", 432.0, 440.0)

    def test_remove_user_preset(self):
        """Test removing an existing user preset."""
        self.mock_config['user_presets'] = {
            "Binaural": [{"label": "To Remove", "left_hz": 100, "right_hz": 110}],
            "Monaural": [],
            "Isochronic": [],
        }

        result = SourceCode.remove_user_preset("Binaural", "To Remove")

        self.assertTrue(result)
        self.assertEqual(len(self.mock_config["user_presets"]["Binaural"]), 0)
        self.mock_save_config.assert_called_once_with(self.mock_config)

    def test_remove_user_preset_not_found(self):
        """Test removing a preset that does not exist."""
        self.mock_config['user_presets'] = {
            "Binaural": [{"label": "Some Preset", "left_hz": 100, "right_hz": 110}],
            "Monaural": [],
            "Isochronic": [],
        }

        result = SourceCode.remove_user_preset("Binaural", "Not Found")

        self.assertFalse(result)
        self.assertEqual(len(self.mock_config["user_presets"]["Binaural"]), 1)
        self.mock_save_config.assert_not_called()

    @patch('SourceCode.CONFIG_PATH')
    def test_save_config(self, mock_path):
        """Test the actual save_config function."""
        # We need to un-patch the save_config we patched in setUp
        self.save_config_patcher.stop()

        mock_file = mock_open()
        # Mock the path object behavior
        mock_path.write_text = mock_file
        mock_path.parent.mkdir = MagicMock()

        test_config_data = {"theme": "darkly", "value": 1}
        SourceCode.save_config(test_config_data)

        mock_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(json.dumps(test_config_data, indent=2), encoding="utf-8")

        # Restore patch for other tests
        self.save_config_patcher.start()

    @patch('SourceCode.CONFIG_PATH')
    def test_load_config_exists(self, mock_path):
        """Test loading an existing config file."""
        test_json = '{"theme": "superhero"}'
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = test_json

        config = SourceCode.load_config()

        self.assertEqual(config, {"theme": "superhero"})
        mock_path.read_text.assert_called_once_with(encoding="utf-8")

    @patch('SourceCode.CONFIG_PATH')
    def test_load_config_not_exists(self, mock_path):
        """Test loading when config file does not exist."""
        mock_path.exists.return_value = False

        config = SourceCode.load_config()

        self.assertEqual(config, {})

    @patch('SourceCode.CONFIG_PATH')
    @patch('SourceCode.logger')
    def test_load_config_error(self, mock_logger, mock_path):
        """Test loading a corrupt config file."""
        mock_path.exists.return_value = True
        mock_path.read_text.side_effect = json.JSONDecodeError("err", "doc", 0)

        config = SourceCode.load_config()

        self.assertEqual(config, {})
        mock_logger.error.assert_called_once()


if __name__ == '__main__':
    unittest.main()