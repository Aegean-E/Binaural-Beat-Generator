import sys
import unittest
from unittest.mock import MagicMock
import types
import os

# Add parent directory to sys.path to find 'presets' and 'SourceCode'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create dummy modules
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()

# Mock numpy if needed
try:
    import numpy
except ImportError:
    sys.modules['numpy'] = MagicMock()

# Load SourceCode module
source_code = types.ModuleType("SourceCode")
file_path = os.path.abspath("SourceCode")

with open(file_path, "r") as f:
    code_content = f.read()

source_code.__file__ = file_path

try:
    exec(code_content, source_code.__dict__)
except Exception as e:
    print(f"Error loading module: {e}")
    # We don't exit here, we let the tests run, they might fail if module is broken
    pass

sys.modules["SourceCode"] = source_code

class TestUIRefactor(unittest.TestCase):

    def setUp(self):
        # Reset mocks before each test if needed
        # Ensure ttk.Entry returns new mocks each time
        source_code.ttk.Entry.side_effect = lambda *args, **kwargs: MagicMock()
        source_code.ttk.Combobox.side_effect = lambda *args, **kwargs: MagicMock()

    def test_create_frequency_control_frame(self):
        """Test the create_frequency_control_frame helper function."""
        if not hasattr(source_code, 'create_frequency_control_frame'):
            self.fail("create_frequency_control_frame not implemented")

        # Mock parent widget
        parent = MagicMock()
        title = "Test Frequency Frame"
        col_idx = 0
        default_freq = "123"
        default_vol = "45"
        default_waveform = "Square"
        waveform_options = ["Sine", "Square"]

        # Call the function
        freq_entry, vol_entry, waveform_var, waveform_combobox = source_code.create_frequency_control_frame(
            parent, title, col_idx, waveform_options, default_freq, default_vol, default_waveform
        )

        # Verify the returned objects are mocks
        self.assertIsInstance(freq_entry, MagicMock)
        self.assertIsInstance(vol_entry, MagicMock)
        self.assertIsInstance(waveform_combobox, MagicMock)

        # Verify calls on the mocks
        freq_entry.insert.assert_called_with(0, default_freq)
        vol_entry.insert.assert_called_with(0, default_vol)
        waveform_combobox.set.assert_called_with(default_waveform)

        # Check grid calls
        freq_entry.grid.assert_called()
        vol_entry.grid.assert_called()
        waveform_combobox.grid.assert_called()

if __name__ == '__main__':
    unittest.main()
