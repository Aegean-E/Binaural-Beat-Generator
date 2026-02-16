import sys
import unittest
from unittest.mock import MagicMock, patch
import importlib.machinery
import types
import os

# Add root directory to sys.path to allow importing presets
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Mock modules that are not available or need to be mocked
sys.modules['numpy'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()

# Load the source code
# Adjust path to find SourceCode in the parent directory
source_code_path = os.path.join(os.path.dirname(__file__), '..', 'SourceCode')
if not os.path.exists(source_code_path):
    # Fallback if running from root and file is in root
    source_code_path = 'SourceCode'

loader = importlib.machinery.SourceFileLoader('SourceCode', source_code_path)
mod = types.ModuleType(loader.name)
loader.exec_module(mod)

class TestPlayAudio(unittest.TestCase):
    def setUp(self):
        # Reset globals
        mod.is_playing = False
        mod.stream = None
        mod.live_status_after_id = None

        # Mock UI elements
        self.left_volume_entry = MagicMock()
        self.right_volume_entry = MagicMock()
        self.left_waveform_var = MagicMock()
        self.right_waveform_var = MagicMock()
        self.ramp_enabled_var = MagicMock()
        self.carrier_entry = MagicMock()
        self.start_beat_entry = MagicMock()
        self.end_beat_entry = MagicMock()
        self.ramp_minutes_entry = MagicMock()
        self.left_frequency_entry = MagicMock()
        self.right_frequency_entry = MagicMock()

        # Set default return values
        self.left_volume_entry.get.return_value = "50"
        self.right_volume_entry.get.return_value = "50"
        self.left_waveform_var.get.return_value = "Sine"
        self.right_waveform_var.get.return_value = "Sine"
        self.ramp_enabled_var.get.return_value = False

        self.carrier_entry.get.return_value = "432"
        self.start_beat_entry.get.return_value = "20"
        self.end_beat_entry.get.return_value = "3"
        self.ramp_minutes_entry.get.return_value = "30"

        self.left_frequency_entry.get.return_value = "432"
        self.right_frequency_entry.get.return_value = "436"

        # Inject mocks into module
        mod.left_volume_entry = self.left_volume_entry
        mod.right_volume_entry = self.right_volume_entry
        mod.left_waveform_var = self.left_waveform_var
        mod.right_waveform_var = self.right_waveform_var
        mod.ramp_enabled_var = self.ramp_enabled_var
        mod.carrier_entry = self.carrier_entry
        mod.start_beat_entry = self.start_beat_entry
        mod.end_beat_entry = self.end_beat_entry
        mod.ramp_minutes_entry = self.ramp_minutes_entry
        mod.left_frequency_entry = self.left_frequency_entry
        mod.right_frequency_entry = self.right_frequency_entry

        # Mock other dependencies
        mod.stop_audio = MagicMock()
        mod._start_stream = MagicMock()
        mod.update_live_status = MagicMock()
        mod.messagebox = MagicMock()

    def test_play_audio_manual(self):
        mod.play_audio()

        mod._start_stream.assert_called_once()
        args, kwargs = mod._start_stream.call_args

        self.assertEqual(kwargs['use_ramp'], False)
        self.assertEqual(kwargs['left_frequency'], 432.0)
        self.assertEqual(kwargs['right_frequency'], 436.0)
        self.assertEqual(kwargs['left_volume'], 0.5)
        self.assertEqual(kwargs['right_volume'], 0.5)
        self.assertEqual(kwargs['left_waveform'], "Sine")
        self.assertEqual(kwargs['right_waveform'], "Sine")

        self.assertTrue(mod.is_playing)
        mod.update_live_status.assert_called_once()

    def test_play_audio_ramp(self):
        self.ramp_enabled_var.get.return_value = True

        mod.play_audio()

        mod._start_stream.assert_called_once()
        args, kwargs = mod._start_stream.call_args

        self.assertEqual(kwargs['use_ramp'], True)
        self.assertEqual(kwargs['carrier_hz'], 432.0)
        self.assertEqual(kwargs['start_beat_hz'], 20.0)
        self.assertEqual(kwargs['end_beat_hz'], 3.0)
        self.assertEqual(kwargs['ramp_minutes'], 30.0)

        # Check if UI was updated
        self.left_frequency_entry.delete.assert_called()
        self.right_frequency_entry.delete.assert_called()
        self.left_frequency_entry.insert.assert_called()
        self.right_frequency_entry.insert.assert_called()

        # Verify inserted values (carrier +/- start_beat/2)
        # 432 - 10 = 422
        # 432 + 10 = 442
        calls = self.left_frequency_entry.insert.call_args_list
        self.assertEqual(calls[-1][0][1], str(422.0))

        calls = self.right_frequency_entry.insert.call_args_list
        self.assertEqual(calls[-1][0][1], str(442.0))

if __name__ == '__main__':
    unittest.main()
