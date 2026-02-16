import unittest
from unittest.mock import MagicMock
import sys
import os
import importlib.machinery
import importlib.util

# Mock dependencies before import
sys.path.append(os.getcwd())
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.simpledialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()
sys.modules['scipy.io'] = MagicMock()
sys.modules['scipy.io.wavfile'] = MagicMock()
sys.modules['numpy'] = MagicMock()

# Load SourceCode
try:
    loader = importlib.machinery.SourceFileLoader('SourceCode', 'SourceCode.py')
    spec = importlib.util.spec_from_loader(loader.name, loader)
    source_code = importlib.util.module_from_spec(spec)
    sys.modules["SourceCode"] = source_code
    loader.exec_module(source_code)
except Exception as e:
    print(f"Error loading SourceCode: {e}")
    sys.exit(1)

class TestValidation(unittest.TestCase):
    def test_freq_range(self):
        # 19Hz
        msg = source_code.validate_audio_params(19, 100, 50, 50)
        self.assertIn("Frequency must be between 20 Hz and 20000 Hz", msg)

        # 20001Hz
        msg = source_code.validate_audio_params(20001, 100, 50, 50)
        self.assertIn("Frequency must be between 20 Hz and 20000 Hz", msg)

        # Valid
        msg = source_code.validate_audio_params(20, 20000, 50, 50)
        self.assertIsNone(msg)

    def test_volume_range(self):
        msg = source_code.validate_audio_params(100, 100, -1, 50)
        self.assertIn("Volume", msg)

        msg = source_code.validate_audio_params(100, 100, 101, 50)
        self.assertIn("Volume", msg)

    def test_duration(self):
        msg = source_code.validate_audio_params(100, 100, 50, 50, duration=0)
        self.assertIn("Duration", msg)

        msg = source_code.validate_audio_params(100, 100, 50, 50, duration=-5)
        self.assertIn("Duration", msg)

        msg = source_code.validate_audio_params(100, 100, 50, 50, duration=10)
        self.assertIsNone(msg)

if __name__ == '__main__':
    unittest.main()
