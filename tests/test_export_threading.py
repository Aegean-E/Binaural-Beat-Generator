import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import importlib.util
import importlib.machinery

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

class TestExportThreading(unittest.TestCase):
    def test_export_starts_thread(self):
        # Mock root
        source_code.root = MagicMock()

        # Setup global UI vars
        # We need to mock entries that are module-level variables in SourceCode?
        # SourceCode assigns them at the end.
        # So we can assign them on source_code module object.

        # Mock entries
        mock_entry = MagicMock()
        mock_entry.get.return_value = "50"
        source_code.left_volume_entry = mock_entry
        source_code.right_volume_entry = mock_entry

        mock_var = MagicMock()
        mock_var.get.return_value = "Sine"
        source_code.left_waveform_var = mock_var
        source_code.right_waveform_var = mock_var

        mock_bool_var = MagicMock()
        mock_bool_var.get.return_value = False
        source_code.ramp_enabled_var = mock_bool_var

        mock_freq_entry = MagicMock()
        mock_freq_entry.get.return_value = "100"
        source_code.left_frequency_entry = mock_freq_entry
        source_code.right_frequency_entry = mock_freq_entry

        # Mock dialogs on source_code.simpledialog, not sys.modules['tkinter.simpledialog']?
        # SourceCode imports simpledialog.
        source_code.simpledialog.askstring.return_value = "10"
        source_code.filedialog.asksaveasfilename.return_value = "test.wav"

        # Mock stop_audio
        source_code.stop_audio = MagicMock()

        # Mock threading
        with patch('SourceCode.threading.Thread') as mock_thread:
            source_code.export_audio_file()

            mock_thread.assert_called_once()
            mock_thread.return_value.start.assert_called_once()

            # Verify target is _run_export_thread
            args, kwargs = mock_thread.call_args
            # kwargs might not be used if args passed directly
            # Thread(target=..., args=...)
            if 'target' in kwargs:
                self.assertEqual(kwargs['target'], source_code._run_export_thread)
            else:
                # args[0] might be target? No, Thread(group=None, target=None, ...)
                pass

if __name__ == '__main__':
    unittest.main()
