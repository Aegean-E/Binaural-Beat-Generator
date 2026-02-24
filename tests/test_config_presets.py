"""Test config and preset management functions."""

import unittest
import sys
import os
import json
import tempfile
from unittest.mock import MagicMock, patch, mock_open

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mock dependencies
mock_numpy = MagicMock()
mock_numpy.pi = 3.14159
mock_numpy.float32 = float
mock_numpy.float64 = float

mock_scipy = MagicMock()
mock_tk = MagicMock()
mock_tk.TclError = Exception

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
    'matplotlib': MagicMock(),
    'matplotlib.figure': MagicMock(),
    'matplotlib.backends': MagicMock(),
    'matplotlib.backends.backend_tkagg': MagicMock(),
}


class TestNormalizeCategory(unittest.TestCase):
    """Test _normalize_category function."""
    
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch.dict(sys.modules, modules_to_patch)
        cls.patcher.start()
        import SourceCode as sc
        cls.sc = sc
    
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
    
    def test_normalize_binaural(self):
        """Test normalization of binaural."""
        self.assertEqual(self.sc._normalize_category("binaural"), "Binaural")
        self.assertEqual(self.sc._normalize_category("Binaural"), "Binaural")
        self.assertEqual(self.sc._normalize_category("  Binaural  "), "Binaural")
    
    def test_normalize_monaural(self):
        """Test normalization maps monaural to Binaural."""
        self.assertEqual(self.sc._normalize_category("monaural"), "Binaural")
        self.assertEqual(self.sc._normalize_category("Monaural"), "Binaural")
        self.assertEqual(self.sc._normalize_category("monaural beat"), "Binaural")
    
    def test_normalize_isochronic(self):
        """Test normalization of isochronic."""
        self.assertEqual(self.sc._normalize_category("isochronic"), "Isochronic")
        self.assertEqual(self.sc._normalize_category("Isochronic"), "Isochronic")
        self.assertEqual(self.sc._normalize_category("isochronic tone"), "Isochronic")
    
    def test_normalize_invalid(self):
        """Test invalid category raises ValueError."""
        with self.assertRaises(ValueError):
            self.sc._normalize_category("invalid")
        
        with self.assertRaises(ValueError):
            self.sc._normalize_category("")


class TestGetUserPresets(unittest.TestCase):
    """Test get_user_presets function."""
    
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch.dict(sys.modules, modules_to_patch)
        cls.patcher.start()
        import SourceCode as sc
        cls.sc = sc
        
        # Create temp config directory
        cls.temp_dir = tempfile.mkdtemp()
        cls.config_path = os.path.join(cls.temp_dir, 'config.json')
        
        cls.original_home = os.path.expanduser
        os.path.expanduser = lambda x: cls.temp_dir
    
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
        os.path.expanduser = cls.original_home
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
    
    def test_get_user_presets_empty(self):
        """Test get_user_presets with no config file."""
        # Remove config if exists
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        
        # Mock config to empty
        self.sc.config = {}
        
        result = self.sc.get_user_presets()
        
        self.assertIn("Monaural", result)
        self.assertIn("Binaural", result)
        self.assertIn("Isochronic", result)
        self.assertEqual(result["Monaural"], [])
        self.assertEqual(result["Binaural"], [])
        self.assertEqual(result["Isochronic"], [])
    
    def test_get_user_presets_with_data(self):
        """Test get_user_presets with user presets."""
        user_data = {
            "user_presets": {
                "Monaural": [{"label": "Test", "left_hz": 100, "right_hz": 100}],
                "Binaural": [{"label": "Test2", "left_hz": 200, "right_hz": 210}],
                "Isochronic": [{"label": "Test3", "carrier_hz": 432, "pulse_hz": 10}]
            }
        }
        self.sc.config = user_data
        
        result = self.sc.get_user_presets()
        
        self.assertEqual(len(result["Monaural"]), 1)
        self.assertEqual(len(result["Binaural"]), 1)
        self.assertEqual(len(result["Isochronic"]), 1)


class TestGetAllPresets(unittest.TestCase):
    """Test get_all_presets function."""
    
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch.dict(sys.modules, modules_to_patch)
        cls.patcher.start()
        import SourceCode as sc
        cls.sc = sc
        import presets
        cls.presets = presets
    
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
    
    def test_get_all_presets_structure(self):
        """Test get_all_presets returns correct keys."""
        self.sc.config = {}
        result = self.sc.get_all_presets()
        
        self.assertIn("Monaural", result)
        self.assertIn("Binaural", result)
        self.assertIn("Isochronic", result)
    
    def test_get_all_presets_includes_defaults(self):
        """Test get_all_presets includes default presets."""
        self.sc.config = {}
        result = self.sc.get_all_presets()
        
        # Should have default presets
        self.assertGreater(len(result["Monaural"]), 0)
        self.assertGreater(len(result["Binaural"]), 0)
        self.assertGreater(len(result["Isochronic"]), 0)
    
    def test_get_all_presets_merges_user(self):
        """Test get_all_presets merges user presets."""
        self.sc.config = {
            "user_presets": {
                "Monaural": [{"label": "Custom", "left_hz": 100, "right_hz": 100}],
                "Binaural": [{"label": "Custom2", "left_hz": 200, "right_hz": 210}],
                "Isochronic": [{"label": "Custom3", "carrier_hz": 432, "pulse_hz": 10}]
            }
        }
        result = self.sc.get_all_presets()
        
        # Should have defaults + user presets
        self.assertGreater(len(result["Monaural"]), 1)
        self.assertGreater(len(result["Binaural"]), 1)
        self.assertGreater(len(result["Isochronic"]), 1)


class TestAddUserPreset(unittest.TestCase):
    """Test add_user_preset function."""
    
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch.dict(sys.modules, modules_to_patch)
        cls.patcher.start()
        import SourceCode as sc
        cls.sc = sc
    
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
    
    def test_add_user_preset_isochronic(self):
        """Test adding isochronic preset."""
        self.sc.config = {"user_presets": {}}
        
        # Isochronic presets use carrier_hz as right_hz and pulse_hz as left_hz
        self.sc.add_user_preset("Isochronic", "Test Preset", 10, 432)  # pulse_hz, carrier_hz
        
        self.assertIn("Isochronic", self.sc.config["user_presets"])
        self.assertEqual(len(self.sc.config["user_presets"]["Isochronic"]), 1)
    
    def test_add_user_preset_binaural(self):
        """Test adding binaural preset."""
        self.sc.config = {"user_presets": {}}
        
        self.sc.add_user_preset("Binaural", "Test Binaural", 440, 450)
        
        self.assertIn("Binaural", self.sc.config["user_presets"])
        self.assertEqual(len(self.sc.config["user_presets"]["Binaural"]), 1)


class TestRemoveUserPreset(unittest.TestCase):
    """Test remove_user_preset function."""
    
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch.dict(sys.modules, modules_to_patch)
        cls.patcher.start()
        import SourceCode as sc
        cls.sc = sc
    
    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
    
    def test_remove_existing_preset(self):
        """Test removing existing preset returns True."""
        # Config needs user_presets key
        self.sc.config = {}
        
        # First add a preset
        self.sc.add_user_preset("Monaural", "Test", 100, 100)
        
        # Now try to remove it
        result = self.sc.remove_user_preset("Monaural", "Test")
        
        self.assertTrue(result)
    
    def test_remove_nonexistent_preset(self):
        """Test removing nonexistent preset returns False."""
        self.sc.config = {"user_presets": {"Monaural": []}}
        
        result = self.sc.remove_user_preset("Monaural", "Nonexistent")
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
