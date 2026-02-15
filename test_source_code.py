import unittest
from unittest.mock import MagicMock, patch
import sys
import importlib.machinery
import types

# Mock dependencies before importing SourceCode
sys.modules['sounddevice'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()

# Define TclError for tkinter
sys.modules['tkinter'].TclError = Exception

# Load SourceCode module using SourceFileLoader for extensionless file
loader = importlib.machinery.SourceFileLoader("SourceCode", "./SourceCode")
SourceCode = types.ModuleType(loader.name)
# Register the module so it can import itself or be imported
sys.modules["SourceCode"] = SourceCode
loader.exec_module(SourceCode)

class TestSourceCode(unittest.TestCase):
    def test_play_audio_uses_sample_rate(self):
        # Mock UI elements used in play_audio
        SourceCode.left_volume_entry = MagicMock()
        SourceCode.left_volume_entry.get.return_value = "50"

        SourceCode.right_volume_entry = MagicMock()
        SourceCode.right_volume_entry.get.return_value = "50"

        SourceCode.left_waveform_var = MagicMock()
        SourceCode.left_waveform_var.get.return_value = "Sine"

        SourceCode.right_waveform_var = MagicMock()
        SourceCode.right_waveform_var.get.return_value = "Sine"

        SourceCode.ramp_enabled_var = MagicMock()
        SourceCode.ramp_enabled_var.get.return_value = False

        SourceCode.left_frequency_entry = MagicMock()
        SourceCode.left_frequency_entry.get.return_value = "432"

        SourceCode.right_frequency_entry = MagicMock()
        SourceCode.right_frequency_entry.get.return_value = "436"

        # Mock dependencies used in ramp mode as well, just in case
        SourceCode.carrier_entry = MagicMock()
        SourceCode.start_beat_entry = MagicMock()
        SourceCode.end_beat_entry = MagicMock()
        SourceCode.ramp_minutes_entry = MagicMock()

        # Mock _start_stream to verify calls
        original_start_stream = SourceCode._start_stream
        SourceCode._start_stream = MagicMock()

        try:
            # Call play_audio
            SourceCode.play_audio()

            # Verify _start_stream was called
            SourceCode._start_stream.assert_called_once()
            call_args = SourceCode._start_stream.call_args
            kwargs = call_args.kwargs

            # Check if sample_rate was passed as 44100
            self.assertEqual(kwargs.get('sample_rate'), 44100, "sample_rate should be 44100")

        finally:
            # Restore original function
            SourceCode._start_stream = original_start_stream

if __name__ == '__main__':
    unittest.main()
