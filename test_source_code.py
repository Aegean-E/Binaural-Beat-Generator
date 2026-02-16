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
sys.modules['scipy.io'] = MagicMock()
sys.modules['scipy.io.wavfile'] = MagicMock()

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

if __name__ == '__main__':
    unittest.main()
