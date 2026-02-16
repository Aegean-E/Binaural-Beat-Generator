import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os
import importlib.util
import importlib.machinery
import threading

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
    loader = importlib.machinery.SourceFileLoader('SourceCode', 'SourceCode')
    spec = importlib.util.spec_from_loader(loader.name, loader)
    source_code = importlib.util.module_from_spec(spec)
    sys.modules["SourceCode"] = source_code
    loader.exec_module(source_code)
except Exception as e:
    print(f"Error loading SourceCode: {e}")
    sys.exit(1)

class TestAudioEngine(unittest.TestCase):
    def setUp(self):
        # Create a fresh engine for each test
        self.engine = source_code.AudioEngine()
        # Reset sd mock
        source_code.sd.reset_mock()

    def test_start_creates_stream(self):
        cfg = MagicMock()
        cfg.sample_rate = 44100

        mock_stream_cls = source_code.sd.OutputStream
        mock_stream_instance = mock_stream_cls.return_value

        # Mock generator constructor
        # Use patch.object on the loaded module
        with patch.object(source_code, 'BinauralGenerator') as mock_gen_cls:
            self.engine.start(cfg)

            mock_gen_cls.assert_called_once_with(cfg)
            mock_stream_cls.assert_called_once()
            mock_stream_instance.start.assert_called_once()
            self.assertTrue(self.engine.is_playing)

    def test_stop_calls_request_stop(self):
        # Manually set state to simulate playing
        self.engine.is_playing = True
        mock_stream = MagicMock()
        self.engine._stream = mock_stream
        mock_gen = MagicMock()
        self.engine.generator = mock_gen

        # is_finished is truthy by default (MagicMock)

        with patch('time.sleep') as mock_sleep:
            self.engine.stop()

            mock_gen.request_stop.assert_called_once()
            mock_stream.stop.assert_called_once()
            mock_stream.close.assert_called_once()
            self.assertFalse(self.engine.is_playing)
            self.assertIsNone(self.engine.generator)
            self.assertIsNone(self.engine._stream)

if __name__ == '__main__':
    unittest.main()
