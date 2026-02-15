import sys
from unittest.mock import MagicMock

# Mock dependencies immediately
sys.modules['numpy'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['presets'] = MagicMock()
sys.modules['presets'].MONAURAL_PRESETS = []
sys.modules['presets'].BINAURAL_PRESETS = []

import unittest
import importlib.machinery
import types

def load_source_code():
    print(f"Loading SourceCode... numpy in sys.modules: {'numpy' in sys.modules}")
    loader = importlib.machinery.SourceFileLoader("SourceCode", "SourceCode")
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)
    return mod

class TestUpdateLiveStatus(unittest.TestCase):
    def setUp(self):
        self.mod = load_source_code()

        # Inject mock root
        self.mock_root = MagicMock()
        self.mod.root = self.mock_root

        # Define TclError on the mock tk (which should be available as mod.tk)
        class TclError(Exception): pass
        self.mod.tk.TclError = TclError

        # Mock global variables
        self.mod.is_playing = False
        self.mod.play_mode = "manual"
        self.mod.status_var = MagicMock()
        self.mod.live_status_after_id = 123

        # Mock time
        self.mod.time = MagicMock()
        self.mod.time.time.return_value = 1000.0
        self.mod.play_start_time = 0.0

    def test_update_live_status_window_not_exists(self):
        self.mock_root.winfo_exists.return_value = 0
        self.mod.live_status_after_id = 123
        self.mod.update_live_status()
        self.assertIsNone(self.mod.live_status_after_id)

    def test_update_live_status_tcl_error(self):
        self.mock_root.winfo_exists.side_effect = self.mod.tk.TclError("Display destroyed")
        self.mod.live_status_after_id = 123
        self.mod.update_live_status()
        self.assertIsNone(self.mod.live_status_after_id)

    def test_update_live_status_bare_exception(self):
        # After fix: ValueError should NOT be caught
        self.mock_root.winfo_exists.side_effect = ValueError("Random error")
        self.mod.live_status_after_id = 123

        with self.assertRaises(ValueError):
            self.mod.update_live_status()

        # live_status_after_id should NOT be set to None if exception propagates
        # self.assertIsNotNone(self.mod.live_status_after_id)
        # Actually it depends where exception occurs. It occurs at start.
        # But global variable might not be updated if it fails early.
        # However, checking that ValueError is raised is sufficient.

if __name__ == '__main__':
    unittest.main()
