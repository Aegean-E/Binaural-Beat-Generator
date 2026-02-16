import unittest
import sys
import os
import json
import importlib.machinery
import importlib.util
from unittest.mock import MagicMock, patch

# Mock dependencies before import
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()

# Ensure local imports work
sys.path.append(os.getcwd())

# Load SourceCode module
try:
    loader = importlib.machinery.SourceFileLoader('SourceCode', 'SourceCode')
    spec = importlib.util.spec_from_loader(loader.name, loader)
    source_code = importlib.util.module_from_spec(spec)
    loader.exec_module(source_code)
except Exception as e:
    print(f"Error loading SourceCode: {e}")
    sys.exit(1)

class TestSaveConfig(unittest.TestCase):
    def setUp(self):
        self.test_config = {"theme": "darkly", "user_presets": {}}
        # Save original values
        self.original_app_dir = source_code.APP_DIR
        self.original_config_path = source_code.CONFIG_PATH

    def tearDown(self):
        # Restore original values
        source_code.APP_DIR = self.original_app_dir
        source_code.CONFIG_PATH = self.original_config_path

    def test_save_config_success(self):
        # Setup mocks
        mock_app_dir = MagicMock()
        mock_config_path = MagicMock()
        source_code.APP_DIR = mock_app_dir
        source_code.CONFIG_PATH = mock_config_path

        # Execute
        source_code.save_config(self.test_config)

        # Verify
        mock_app_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        expected_json = json.dumps(self.test_config, indent=2)
        mock_config_path.write_text.assert_called_once_with(expected_json, encoding="utf-8")

    def test_save_config_mkdir_exception(self):
        # Setup mocks
        mock_app_dir = MagicMock()
        mock_app_dir.mkdir.side_effect = PermissionError("Access denied")
        mock_config_path = MagicMock()
        source_code.APP_DIR = mock_app_dir
        source_code.CONFIG_PATH = mock_config_path

        # Execute (should not raise exception)
        source_code.save_config(self.test_config)

        # Verify mkdir was called
        mock_app_dir.mkdir.assert_called_once()
        # Verify write_text was NOT called
        mock_config_path.write_text.assert_not_called()

    def test_save_config_write_text_exception(self):
        # Setup mocks
        mock_app_dir = MagicMock()
        mock_config_path = MagicMock()
        mock_config_path.write_text.side_effect = IOError("Disk full")
        source_code.APP_DIR = mock_app_dir
        source_code.CONFIG_PATH = mock_config_path

        # Execute (should not raise exception)
        source_code.save_config(self.test_config)

        # Verify calls
        mock_app_dir.mkdir.assert_called_once()
        mock_config_path.write_text.assert_called_once()

class TestPresetManagement(unittest.TestCase):
    def setUp(self):
        # Save original config reference
        self.original_config = source_code.config
        # Create a fresh config for testing
        source_code.config = {
            "theme": "darkly",
            "user_presets": {
                "Monaural": [],
                "Binaural": [
                    {"label": "Test Preset 1", "left_hz": 100.0, "right_hz": 110.0},
                    {"label": "Test Preset 2", "left_hz": 200.0, "right_hz": 210.0},
                ]
            }
        }

    def tearDown(self):
        # Restore original config
        source_code.config = self.original_config

    @patch.object(source_code, 'save_config')
    def test_remove_user_preset(self, mock_save_config):
        # Test removing an existing preset
        result = source_code.remove_user_preset("Binaural", "Test Preset 1")
        self.assertTrue(result)

        # Verify preset was removed from config
        binaural_presets = source_code.config["user_presets"]["Binaural"]
        self.assertEqual(len(binaural_presets), 1)
        self.assertEqual(binaural_presets[0]["label"], "Test Preset 2")

        # Verify save_config was called with the updated config
        mock_save_config.assert_called_once()
        args, _ = mock_save_config.call_args
        self.assertEqual(args[0], source_code.config)

        # Reset mock for next steps
        mock_save_config.reset_mock()

        # Test removing non-existent preset
        result = source_code.remove_user_preset("Binaural", "Non Existent")
        self.assertFalse(result)
        # Verify no change
        self.assertEqual(len(source_code.config["user_presets"]["Binaural"]), 1)
        mock_save_config.assert_not_called()

        # Test removing from wrong category
        result = source_code.remove_user_preset("Monaural", "Test Preset 2")
        self.assertFalse(result)
        mock_save_config.assert_not_called()

        # Test case insensitivity for category
        result = source_code.remove_user_preset("binaural", "Test Preset 2")
        self.assertTrue(result)
        self.assertEqual(len(source_code.config["user_presets"]["Binaural"]), 0)
        mock_save_config.assert_called_once()

if __name__ == '__main__':
    unittest.main()
