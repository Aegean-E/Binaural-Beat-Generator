import unittest
import json
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from preset_manager import PresetManager, CONFIG_PATH

class TestPresetManager(unittest.TestCase):
    def setUp(self):
        # Create a temp dir for config
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_config_path = Path(self.temp_dir.name) / "config.json"

        # Monkey patch CONFIG_PATH and APP_DIR in preset_manager
        import preset_manager
        self.original_config_path = preset_manager.CONFIG_PATH
        self.original_app_dir = preset_manager.APP_DIR

        preset_manager.CONFIG_PATH = self.temp_config_path
        preset_manager.APP_DIR = Path(self.temp_dir.name)

        self.manager = PresetManager()

    def tearDown(self):
        import preset_manager
        preset_manager.CONFIG_PATH = self.original_config_path
        preset_manager.APP_DIR = self.original_app_dir
        self.temp_dir.cleanup()

    def test_load_empty_config(self):
        # Config file doesn't exist
        self.assertEqual(self.manager.config, {})

    def test_save_and_load_config(self):
        self.manager.config = {"theme": "superhero"}
        self.manager.save_config()

        # Reload
        new_manager = PresetManager()
        self.assertEqual(new_manager.config, {"theme": "superhero"})

    def test_add_user_preset(self):
        self.manager.add_user_preset("Binaural", "Test Preset", 100, 104)
        presets = self.manager.get_user_presets()
        self.assertEqual(len(presets["Binaural"]), 1)
        self.assertEqual(presets["Binaural"][0]["label"], "Test Preset")
        self.assertEqual(presets["Binaural"][0]["left_hz"], 100)

    def test_remove_user_preset(self):
        self.manager.add_user_preset("Monaural", "To Delete", 200, 200)
        self.assertTrue(self.manager.remove_user_preset("Monaural", "To Delete"))
        presets = self.manager.get_user_presets()
        self.assertEqual(len(presets["Monaural"]), 0)

    def test_get_all_presets(self):
        # Check built-ins are there
        all_presets = self.manager.get_all_presets()
        self.assertTrue(len(all_presets["Binaural"]) > 0)
        self.assertTrue(len(all_presets["Monaural"]) > 0)

        # Add user preset
        self.manager.add_user_preset("Binaural", "My Custom", 300, 310)
        all_presets = self.manager.get_all_presets()

        found = False
        for p in all_presets["Binaural"]:
            if p["label"] == "My Custom":
                found = True
                break
        self.assertTrue(found)

if __name__ == "__main__":
    unittest.main()
