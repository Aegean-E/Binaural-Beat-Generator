import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch
import importlib.machinery
import importlib.util

class TestPresetsLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create mocks for dependencies
        mock_numpy = MagicMock()
        mock_numpy.pi = 3.14159
        mock_numpy.float32 = float

        mock_scipy = MagicMock()

        mock_tk = MagicMock()
        mock_tk.TclError = Exception

        # Prepare dict for patch
        modules_to_patch = {
            'numpy': mock_numpy,
            'scipy': mock_scipy,
            'scipy.signal': MagicMock(),
            'scipy.io': MagicMock(),
            'scipy.io.wavfile': MagicMock(),
            'sounddevice': MagicMock(),
            'ttkbootstrap': MagicMock(),
            'tkinter': mock_tk,
            'tkinter.ttk': MagicMock(),
            'tkinter.messagebox': MagicMock(),
            'tkinter.filedialog': MagicMock(),
        }

        # Start patching sys.modules
        cls.modules_patcher = patch.dict(sys.modules, modules_to_patch)
        cls.modules_patcher.start()

        # Load the module
        cls.module = cls.load_source_code()

    @classmethod
    def tearDownClass(cls):
        cls.modules_patcher.stop()

    @staticmethod
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

    def setUp(self):
        # Save original config
        self.original_config = self.module.config.copy() if isinstance(self.module.config, dict) else {}

        # Define mock presets data
        self.mock_monaural_presets = [
            {"label": "Mock Mono 1", "left_hz": 10.0, "right_hz": 10.0},
            {"label": "Mock Mono 2", "left_hz": 20.0, "right_hz": 20.0},
        ]
        self.mock_binaural_presets = [
            {"label": "Mock Bi 1", "left_hz": 100.0, "right_hz": 105.0},
            {"label": "Mock Bi 2", "left_hz": 200.0, "right_hz": 210.0},
        ]

        # Patch the presets module inside SourceCode
        # Note: SourceCode imports presets, so it's available as cls.module.presets
        self.patcher_mono = patch.object(self.module.presets, 'MONAURAL_PRESETS', self.mock_monaural_presets)
        self.patcher_bi = patch.object(self.module.presets, 'BINAURAL_PRESETS', self.mock_binaural_presets)
        self.patcher_mono.start()
        self.patcher_bi.start()

    def tearDown(self):
        # Restore config
        self.module.config = self.original_config

        # Stop patches
        self.patcher_mono.stop()
        self.patcher_bi.stop()

    def test_merge_standard(self):
        """Test merging default presets with user presets."""
        user_presets = {
            "Monaural": [{"label": "User Mono", "left_hz": 30.0, "right_hz": 30.0}],
            "Binaural": [{"label": "User Bi", "left_hz": 300.0, "right_hz": 315.0}]
        }
        self.module.config = {"user_presets": user_presets}

        result = self.module.get_all_presets()

        # Verify Monaural
        expected_mono = self.mock_monaural_presets + user_presets["Monaural"]
        self.assertEqual(result["Monaural"], expected_mono)
        self.assertEqual(len(result["Monaural"]), 3)

        # Verify Binaural
        expected_bi = self.mock_binaural_presets + user_presets["Binaural"]
        self.assertEqual(result["Binaural"], expected_bi)
        self.assertEqual(len(result["Binaural"]), 3)

    def test_merge_empty_user_presets(self):
        """Test merging when user presets are empty."""
        user_presets = {
            "Monaural": [],
            "Binaural": []
        }
        self.module.config = {"user_presets": user_presets}

        result = self.module.get_all_presets()

        self.assertEqual(result["Monaural"], self.mock_monaural_presets)
        self.assertEqual(result["Binaural"], self.mock_binaural_presets)

    def test_merge_empty_defaults(self):
        """Test merging when default presets are empty."""
        # Override patches with empty lists
        with patch.object(self.module.presets, 'MONAURAL_PRESETS', []), \
             patch.object(self.module.presets, 'BINAURAL_PRESETS', []):

            user_presets = {
                "Monaural": [{"label": "User Mono", "left_hz": 30.0, "right_hz": 30.0}],
                "Binaural": [{"label": "User Bi", "left_hz": 300.0, "right_hz": 315.0}]
            }
            self.module.config = {"user_presets": user_presets}

            result = self.module.get_all_presets()

            self.assertEqual(result["Monaural"], user_presets["Monaural"])
            self.assertEqual(result["Binaural"], user_presets["Binaural"])

    def test_merge_both_empty(self):
        """Test merging when both default and user presets are empty."""
        with patch.object(self.module.presets, 'MONAURAL_PRESETS', []), \
             patch.object(self.module.presets, 'BINAURAL_PRESETS', []):

            self.module.config = {"user_presets": {"Monaural": [], "Binaural": []}}

            result = self.module.get_all_presets()

            self.assertEqual(result["Monaural"], [])
            self.assertEqual(result["Binaural"], [])

    def test_structure(self):
        """Verify the output dictionary keys."""
        result = self.module.get_all_presets()
        self.assertIn("Monaural", result)
        self.assertIn("Binaural", result)
        self.assertIsInstance(result["Monaural"], list)
        self.assertIsInstance(result["Binaural"], list)

if __name__ == '__main__':
    unittest.main()
