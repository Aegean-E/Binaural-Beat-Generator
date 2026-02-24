"""Test the AudioEngine class from SourceCode.py."""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import time

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mock heavy dependencies before importing SourceCode to allow testing
# the AudioEngine's logic without requiring numpy, scipy, or sounddevice.
mock_scipy = MagicMock()
mock_scipy.io = MagicMock()
mock_scipy.signal = MagicMock()

MOCK_MODULES = {
    'sounddevice': MagicMock(),
    'tkinter': MagicMock(),
    'tkinter.ttk': MagicMock(),
    'ttkbootstrap': MagicMock(),
}

for mod_name, mock_obj in MOCK_MODULES.items():
    if mod_name not in sys.modules:
        sys.modules[mod_name] = mock_obj

import SourceCode


class TestAudioEngine(unittest.TestCase):
    """Test the AudioEngine class."""

    @patch('SourceCode.sd', MOCK_MODULES['sounddevice'])
    @patch('SourceCode.BinauralGenerator')
    def test_start_binaural(self, mock_binaural_gen, mock_sd):
        """Test starting the audio engine for binaural beats."""
        engine = SourceCode.AudioEngine()
        cfg = MagicMock(beat_type='binaural', sample_rate=44100)

        engine.start(cfg)

        mock_binaural_gen.assert_called_once_with(cfg)
        self.assertTrue(engine.is_playing)
        self.assertIsNotNone(engine.generator)
        mock_sd.OutputStream.assert_called_once()
        engine._stream.start.assert_called_once()

        # Cleanup
        engine.stop()

    @patch('SourceCode.sd', MOCK_MODULES['sounddevice'])
    @patch('SourceCode.IsochronicGenerator')
    def test_start_isochronic(self, mock_isochronic_gen, mock_sd):
        """Test starting the audio engine for isochronic tones."""
        engine = SourceCode.AudioEngine()
        cfg = MagicMock(beat_type='isochronic', sample_rate=44100)

        engine.start(cfg)

        mock_isochronic_gen.assert_called_once_with(cfg)
        self.assertTrue(engine.is_playing)
        self.assertIsNotNone(engine.generator)
        mock_sd.OutputStream.assert_called_once()
        engine._stream.start.assert_called_once()

        # Cleanup
        engine.stop()

    @patch('SourceCode.sd', MOCK_MODULES['sounddevice'])
    @patch('SourceCode.BinauralGenerator')
    def test_stop(self, mock_binaural_gen, mock_sd):
        """Test stopping the audio engine."""
        engine = SourceCode.AudioEngine()
        cfg = MagicMock(beat_type='binaural', sample_rate=44100)

        # Mock the generator instance
        mock_gen_instance = mock_binaural_gen.return_value
        mock_gen_instance.is_finished = False

        engine.start(cfg)
        self.assertTrue(engine.is_playing)

        engine.stop()

        mock_gen_instance.request_stop.assert_called_once()
        engine._stream.stop.assert_called_once()
        engine._stream.close.assert_called_once()
        self.assertFalse(engine.is_playing)
        self.assertIsNone(engine.generator)
        self.assertIsNone(engine.last_block)

    @patch('SourceCode.sd', MOCK_MODULES['sounddevice'])
    def test_stop_when_not_playing(self, mock_sd):
        """Test that stop() does nothing if not playing."""
        engine = SourceCode.AudioEngine()
        self.assertFalse(engine.is_playing)

        engine.stop()

        mock_sd.OutputStream.assert_not_called()

    @patch('SourceCode.sd', MOCK_MODULES['sounddevice'])
    @patch('SourceCode.logger')
    def test_start_exception(self, mock_logger, mock_sd):
        """Test exception handling during start."""
        mock_sd.OutputStream.side_effect = Exception("Device error")

        engine = SourceCode.AudioEngine()
        cfg = MagicMock(beat_type='binaural', sample_rate=44100)

        with self.assertRaises(Exception):
            engine.start(cfg)

        self.assertFalse(engine.is_playing)
        mock_logger.error.assert_called_with("Failed to start audio", exc_info=True)

    def test_get_elapsed_time(self):
        """Test elapsed time calculation."""
        engine = SourceCode.AudioEngine()
        self.assertEqual(engine.get_elapsed_time(), 0.0)

        engine.is_playing = True
        engine.start_time = time.time() - 5.0

        self.assertAlmostEqual(engine.get_elapsed_time(), 5.0, delta=0.1)


if __name__ == '__main__':
    unittest.main()