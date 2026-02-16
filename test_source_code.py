import unittest
import sys
from unittest.mock import MagicMock
import importlib.machinery
import importlib.util
import types
import os

# Create a dummy module for dependencies that are not installed
def mock_module(module_name):
    m = types.ModuleType(module_name)
    sys.modules[module_name] = m
    return m

# Mock dependencies
mock_tk = MagicMock()
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()

# Mock numpy with necessary attributes for SourceCode import
mock_numpy = MagicMock()
sys.modules['numpy'] = mock_numpy
mock_numpy.sin = MagicMock()
mock_numpy.float32 = float # Use built-in float for simple tests if needed

# Load the SourceCode module
# Since SourceCode is in the current directory and has no extension
source_code_path = os.path.abspath('SourceCode')

# We need to load it properly
loader = importlib.machinery.SourceFileLoader('SourceCode', source_code_path)
spec = importlib.util.spec_from_loader(loader.name, loader)
SourceCode = importlib.util.module_from_spec(spec)

# Mock presets module if needed, but it seems to exist.
# However, let's just let it import naturally if possible,
# or mock it if it has dependencies we don't have.
# content of presets.py is simple list of dicts, no imports. So it should be fine.

# Execute module
try:
    loader.exec_module(SourceCode)
except Exception as e:
    print(f"Error importing SourceCode: {e}")
    sys.exit(1)

class TestGetUserPresets(unittest.TestCase):

    def setUp(self):
        # Reset config before each test to ensure isolation
        # We manipulate the module-level config variable directly
        self.original_config = SourceCode.config.copy()
        SourceCode.config = {}

    def tearDown(self):
        # Restore original config
        SourceCode.config = self.original_config

    def test_get_user_presets_empty_config(self):
        """Test that empty config returns empty lists for both categories."""
        SourceCode.config = {}
        result = SourceCode.get_user_presets()
        expected = {
            "Monaural": [],
            "Binaural": [],
        }
        self.assertEqual(result, expected)

    def test_get_user_presets_populated_config(self):
        """Test that populated config returns the correct presets."""
        user_presets_data = {
            "Monaural": [
                {"label": "Test Mono", "left_hz": 100, "right_hz": 100}
            ],
            "Binaural": [
                {"label": "Test Binaural", "left_hz": 200, "right_hz": 210}
            ]
        }
        SourceCode.config = {"user_presets": user_presets_data}

        result = SourceCode.get_user_presets()

        self.assertEqual(len(result["Monaural"]), 1)
        self.assertEqual(result["Monaural"][0]["label"], "Test Mono")
        self.assertEqual(result["Monaural"][0]["left_hz"], 100)

        self.assertEqual(len(result["Binaural"]), 1)
        self.assertEqual(result["Binaural"][0]["label"], "Test Binaural")
        self.assertEqual(result["Binaural"][0]["left_hz"], 200)

    def test_get_user_presets_partial_config_monaural_only(self):
        """Test when only Monaural presets are defined."""
        user_presets_data = {
            "Monaural": [
                {"label": "Test Mono Only", "left_hz": 100, "right_hz": 100}
            ]
        }
        SourceCode.config = {"user_presets": user_presets_data}

        result = SourceCode.get_user_presets()

        self.assertEqual(len(result["Monaural"]), 1)
        self.assertEqual(result["Monaural"][0]["label"], "Test Mono Only")
        self.assertEqual(result["Binaural"], [])

    def test_get_user_presets_partial_config_binaural_only(self):
        """Test when only Binaural presets are defined."""
        user_presets_data = {
            "Binaural": [
                {"label": "Test Binaural Only", "left_hz": 200, "right_hz": 210}
            ]
        }
        SourceCode.config = {"user_presets": user_presets_data}

        result = SourceCode.get_user_presets()

        self.assertEqual(result["Monaural"], [])
        self.assertEqual(len(result["Binaural"]), 1)
        self.assertEqual(result["Binaural"][0]["label"], "Test Binaural Only")

    def test_get_user_presets_with_extra_keys(self):
        """Test that extra keys in user_presets are ignored."""
        user_presets_data = {
            "Monaural": [],
            "Binaural": [],
            "ExtraCategory": [{"label": "Should be ignored"}]
        }
        SourceCode.config = {"user_presets": user_presets_data}

        result = SourceCode.get_user_presets()

        self.assertIn("Monaural", result)
        self.assertIn("Binaural", result)
        self.assertNotIn("ExtraCategory", result)

if __name__ == '__main__':
    unittest.main()
