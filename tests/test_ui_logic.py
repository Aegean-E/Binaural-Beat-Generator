"""Test UI logic functions from SourceCode.py that don't require a live UI."""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mock heavy dependencies before importing SourceCode
# Create a mock for scipy that can handle nested attribute access
mock_scipy = MagicMock()
mock_scipy.io = MagicMock()
mock_scipy.signal = MagicMock()

MOCK_MODULES = {
    'numpy': MagicMock(),
    'scipy': mock_scipy,
    'scipy.io': mock_scipy.io,
    'scipy.signal': mock_scipy.signal,
    'sounddevice': MagicMock(),
    'tkinter': MagicMock(),
    'tkinter.ttk': MagicMock(),
    'ttkbootstrap': MagicMock(),
    'matplotlib': MagicMock(),
    'matplotlib.figure': MagicMock(),
    'matplotlib.backends': MagicMock(),
    'matplotlib.backends.backend_tkagg': MagicMock(),
}
for mod_name, mock_obj in MOCK_MODULES.items():
    if mod_name not in sys.modules:
        sys.modules[mod_name] = mock_obj

import SourceCode


# This is a decorator to patch all UI globals for a test function
def patch_ui_globals(func):
    @patch('SourceCode.left_frequency_entry', MagicMock())
    @patch('SourceCode.right_frequency_entry', MagicMock())
    @patch('SourceCode.left_volume_entry', MagicMock())
    @patch('SourceCode.right_volume_entry', MagicMock())
    @patch('SourceCode.noise_volume_entry', MagicMock())
    @patch('SourceCode.left_waveform_var', MagicMock())
    @patch('SourceCode.right_waveform_var', MagicMock())
    @patch('SourceCode.noise_type_var', MagicMock())
    @patch('SourceCode.ramp_enabled_var', MagicMock())
    @patch('SourceCode.beat_type_var', MagicMock())
    @patch('SourceCode.carrier_entry', MagicMock())
    @patch('SourceCode.start_beat_entry', MagicMock())
    @patch('SourceCode.end_beat_entry', MagicMock())
    @patch('SourceCode.ramp_minutes_entry', MagicMock())
    def wrapper(*args, **kwargs):
        # The mock objects are passed as arguments by @patch
        return func(*args, **kwargs)

    return wrapper


class TestUiLogic(unittest.TestCase):
    """Test UI-related logic functions."""

    @patch_ui_globals
    def test_get_audio_config_manual_mode(self, *mocks):
        """Test get_audio_config_from_ui in manual mode."""
        # The mocks are passed in reverse order of decoration
        (
            ramp_minutes_entry, end_beat_entry, start_beat_entry, carrier_entry,
            beat_type_var, ramp_enabled_var, noise_type_var, right_waveform_var,
            left_waveform_var, noise_volume_entry, right_volume_entry, left_volume_entry,
            right_frequency_entry, left_frequency_entry
        ) = mocks

        ramp_enabled_var.get.return_value = False
        left_frequency_entry.get.return_value = "432.0"
        right_frequency_entry.get.return_value = "442.0"
        left_volume_entry.get.return_value = "50"
        right_volume_entry.get.return_value = "50"
        noise_volume_entry.get.return_value = "10"
        left_waveform_var.get.return_value = "Sine"
        right_waveform_var.get.return_value = "Square"
        noise_type_var.get.return_value = "Pink"
        beat_type_var.get.return_value = "binaural"

        cfg = SourceCode.get_audio_config_from_ui()

        self.assertFalse(cfg.use_ramp)
        self.assertEqual(cfg.left_frequency, 432.0)
        self.assertEqual(cfg.right_frequency, 442.0)
        self.assertAlmostEqual(cfg.left_volume, 0.5)
        self.assertEqual(cfg.left_waveform, "Sine")
        self.assertEqual(cfg.right_waveform, "Square")
        self.assertEqual(cfg.noise_type, "Pink")
        self.assertAlmostEqual(cfg.noise_volume, 0.1)
        self.assertEqual(cfg.beat_type, "binaural")

    @patch_ui_globals
    def test_get_audio_config_ramp_mode(self, *mocks):
        """Test get_audio_config_from_ui in ramp mode."""
        (
            ramp_minutes_entry, end_beat_entry, start_beat_entry, carrier_entry,
            beat_type_var, ramp_enabled_var, noise_type_var, right_waveform_var,
            left_waveform_var, noise_volume_entry, right_volume_entry, left_volume_entry,
            right_frequency_entry, left_frequency_entry
        ) = mocks

        ramp_enabled_var.get.return_value = True
        carrier_entry.get.return_value = "528"
        start_beat_entry.get.return_value = "20"
        end_beat_entry.get.return_value = "8"
        ramp_minutes_entry.get.return_value = "15"
        left_volume_entry.get.return_value = "60"
        right_volume_entry.get.return_value = "60"
        noise_volume_entry.get.return_value = "0"
        left_waveform_var.get.return_value = "Sine"
        right_waveform_var.get.return_value = "Sine"
        noise_type_var.get.return_value = "None"
        beat_type_var.get.return_value = "binaural"

        cfg = SourceCode.get_audio_config_from_ui()

        self.assertTrue(cfg.use_ramp)
        self.assertEqual(cfg.carrier_hz, 528.0)
        self.assertEqual(cfg.start_beat_hz, 20.0)
        self.assertEqual(cfg.end_beat_hz, 8.0)
        self.assertEqual(cfg.ramp_duration_s, 15 * 60.0)
        self.assertAlmostEqual(cfg.left_volume, 0.6)

    @patch_ui_globals
    def test_get_audio_config_invalid_input(self, *mocks):
        """Test get_audio_config_from_ui with invalid text input."""
        (
            ramp_minutes_entry, end_beat_entry, start_beat_entry, carrier_entry,
            beat_type_var, ramp_enabled_var, noise_type_var, right_waveform_var,
            left_waveform_var, noise_volume_entry, right_volume_entry, left_volume_entry,
            right_frequency_entry, left_frequency_entry
        ) = mocks

        ramp_enabled_var.get.return_value = False
        left_frequency_entry.get.return_value = "not-a-number"
        right_frequency_entry.get.return_value = "442.0"
        left_volume_entry.get.return_value = "50"
        right_volume_entry.get.return_value = "50"
        noise_volume_entry.get.return_value = "10"

        with self.assertRaisesRegex(ValueError, "Please enter valid numeric values for frequencies."):
            SourceCode.get_audio_config_from_ui()

    @patch_ui_globals
    def test_get_audio_config_out_of_range(self, *mocks):
        """Test get_audio_config_from_ui with out-of-range frequency."""
        (
            ramp_minutes_entry, end_beat_entry, start_beat_entry, carrier_entry,
            beat_type_var, ramp_enabled_var, noise_type_var, right_waveform_var,
            left_waveform_var, noise_volume_entry, right_volume_entry, left_volume_entry,
            right_frequency_entry, left_frequency_entry
        ) = mocks

        ramp_enabled_var.get.return_value = False
        left_frequency_entry.get.return_value = "10.0"  # Below 20Hz
        right_frequency_entry.get.return_value = "442.0"
        left_volume_entry.get.return_value = "50"
        right_volume_entry.get.return_value = "50"
        noise_volume_entry.get.return_value = "10"
        beat_type_var.get.return_value = "binaural"

        with self.assertRaisesRegex(ValueError, "Frequency must be between 20 Hz and 20000 Hz."):
            SourceCode.get_audio_config_from_ui()

    @patch('SourceCode.apply_preset')
    def test_build_preset_buttons(self, mock_apply_preset):
        """Test that preset buttons are created with the correct commands."""
        mock_binaural_frame = MagicMock()
        mock_isochronic_frame = MagicMock()

        with patch('SourceCode.binaural_monaural_frame', mock_binaural_frame), \
                patch('SourceCode.isochronic_beats_frame', mock_isochronic_frame), \
                patch('SourceCode.get_all_presets') as mock_get_presets:
            mock_get_presets.return_value = {
                "Monaural": [],
                "Binaural": [{"label": "Test Binaural", "left_hz": 400, "right_hz": 410}],
                "Isochronic": [{"label": "Test Iso", "carrier_hz": 200, "pulse_hz": 10}],
            }

            with patch('SourceCode.ttk.Button') as mock_button:
                SourceCode.build_preset_buttons()

                self.assertGreaterEqual(len(mock_button.call_args_list), 2)

                binaural_call_args = mock_button.call_args_list[0]
                binaural_command = binaural_call_args[1]['command']
                binaural_command()
                mock_apply_preset.assert_called_with(400, 410, "Binaural")

                isochronic_call_args = mock_button.call_args_list[1]
                isochronic_command = isochronic_call_args[1]['command']
                isochronic_command()
                mock_apply_preset.assert_called_with(0, 0, "Isochronic", carrier_hz=200, pulse_hz=10)

    def test_apply_preset(self):
        """Test that apply_preset correctly updates the UI entries."""
        mock_left_entry = MagicMock()
        mock_right_entry = MagicMock()
        mock_beat_type_var = MagicMock()
        mock_carrier_entry = MagicMock()

        with patch('SourceCode.left_frequency_entry', mock_left_entry), \
                patch('SourceCode.right_frequency_entry', mock_right_entry), \
                patch('SourceCode.beat_type_var', mock_beat_type_var), \
                patch('SourceCode.carrier_entry', mock_carrier_entry):
            SourceCode.apply_preset(left_hz=432.0, right_hz=440.0, category="Binaural")
            mock_left_entry.delete.assert_called_with(0, 'end')
            mock_left_entry.insert.assert_called_with(0, '432.0')
            mock_right_entry.delete.assert_called_with(0, 'end')
            mock_right_entry.insert.assert_called_with(0, '440.0')
            mock_beat_type_var.set.assert_called_with("binaural")

            SourceCode.apply_preset(category="Isochronic", pulse_hz=10.0, carrier_hz=200.0)
            mock_left_entry.insert.assert_called_with(0, '10.0')
            mock_right_entry.insert.assert_called_with(0, '200.0')
            mock_carrier_entry.insert.assert_called_with(0, '200.0')
            mock_beat_type_var.set.assert_called_with("isochronic")


if __name__ == '__main__':
    unittest.main()