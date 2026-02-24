"""
Test the DSP generator classes (BinauralGenerator, IsochronicGenerator).
These tests require numpy and scipy to be installed.
"""

import unittest
import numpy as np
from unittest.mock import MagicMock

# We need to import the real numpy and scipy for these tests,
# but we still need to mock the UI and sounddevice parts of SourceCode.
import sys
from unittest.mock import patch

MOCK_MODULES = {
    'tkinter': MagicMock(),
    'tkinter.ttk': MagicMock(),
    'ttkbootstrap': MagicMock(),
    'sounddevice': MagicMock(),
    'matplotlib': MagicMock(),
    'matplotlib.figure': MagicMock(),
    'matplotlib.backends': MagicMock(),
    'matplotlib.backends.backend_tkagg': MagicMock(),
}
for mod_name, mock_obj in MOCK_MODULES.items():
    sys.modules[mod_name] = mock_obj

import SourceCode


class TestBinauralGenerator(unittest.TestCase):
    """Tests for the BinauralGenerator class."""

    def setUp(self):
        """Set up a default AudioConfig for tests."""
        self.cfg = SourceCode.AudioConfig(
            sample_rate=44100,
            left_volume=0.8,
            right_volume=0.8,
            left_waveform="Sine",
            right_waveform="Sine",
            noise_type="None",
            noise_volume=0.0,
            use_ramp=False,
            left_frequency=432.0,
            right_frequency=442.0,
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0,
            beat_type="binaural"
        )

    def test_block_generation(self):
        """Test that a block of audio is generated with the correct shape and type."""
        gen = SourceCode.BinauralGenerator(self.cfg)
        block = gen.generate_block(1024)
        self.assertIsInstance(block, np.ndarray)
        self.assertEqual(block.shape, (1024, 2))
        self.assertEqual(block.dtype, np.float32)
        # Check that it's not all zeros
        self.assertTrue(np.any(block))

    def test_fade_in(self):
        """Test that the signal fades in at the beginning."""
        gen = SourceCode.BinauralGenerator(self.cfg)
        block = gen.generate_block(1024)
        # The first sample should be close to zero
        self.assertAlmostEqual(block[0, 0], 0.0, places=5)
        # The amplitude should increase over the fade-in period
        fade_in_len = int(0.02 * self.cfg.sample_rate)  # 882 samples
        self.assertTrue(np.mean(np.abs(block[:100])) < np.mean(np.abs(block[fade_in_len:fade_in_len + 100])))

    def test_fade_out(self):
        """Test that the signal fades out and finishes when stop is requested."""
        gen = SourceCode.BinauralGenerator(self.cfg)
        # Generate some initial blocks to get past the fade-in
        _ = gen.generate_block(4096)

        gen.request_stop()
        self.assertFalse(gen.is_finished)

        # Generate blocks until fade-out is complete
        fade_out_len = int(0.02 * self.cfg.sample_rate)  # 882 samples
        num_blocks_to_fade = (fade_out_len // 1024) + 2

        all_blocks = []
        for _ in range(num_blocks_to_fade):
            block = gen.generate_block(1024)
            all_blocks.append(block)
            if gen.is_finished:
                break

        self.assertTrue(gen.is_finished)

        # The last part of the last block should be all zeros
        last_block = all_blocks[-1]
        self.assertTrue(np.all(last_block[-512:] == 0))

    def test_noise_mixing(self):
        """Test that noise is correctly added to the signal."""
        self.cfg.noise_type = "White"
        self.cfg.noise_volume = 0.5

        gen_with_noise = SourceCode.BinauralGenerator(self.cfg)
        block_with_noise = gen_with_noise.generate_block(1024)

        self.cfg.noise_type = "None"
        gen_without_noise = SourceCode.BinauralGenerator(self.cfg)
        block_without_noise = gen_without_noise.generate_block(1024)

        # The block with noise should be different from the one without
        self.assertFalse(np.allclose(block_with_noise, block_without_noise))
        # The RMS value should be higher (in general)
        rms_with_noise = np.sqrt(np.mean(block_with_noise ** 2))
        rms_without_noise = np.sqrt(np.mean(block_without_noise ** 2))
        self.assertTrue(rms_with_noise > rms_without_noise)

    def test_ramp_mode(self):
        """Test that ramp mode runs without error and produces output."""
        self.cfg.use_ramp = True
        self.cfg.carrier_hz = 432.0
        self.cfg.start_beat_hz = 20.0
        self.cfg.end_beat_hz = 10.0
        self.cfg.ramp_duration_s = 2.0

        gen = SourceCode.BinauralGenerator(self.cfg)
        block1 = gen.generate_block(1024)
        self.assertEqual(block1.shape, (1024, 2))
        self.assertTrue(np.any(block1))

        # Generate another block to ensure phase continuity logic works
        block2 = gen.generate_block(1024)
        self.assertEqual(block2.shape, (1024, 2))
        self.assertTrue(np.any(block2))
        self.assertFalse(np.allclose(block1, block2))


class TestIsochronicGenerator(unittest.TestCase):
    """Tests for the IsochronicGenerator class."""

    def setUp(self):
        """Set up a default AudioConfig for tests."""
        self.cfg = SourceCode.AudioConfig(
            sample_rate=44100,
            left_volume=0.8,
            right_volume=0.8,  # Not used by isochronic, but part of dataclass
            left_waveform="Sine",
            right_waveform="Sine",  # Not used
            noise_type="None",
            noise_volume=0.0,
            use_ramp=False,
            left_frequency=10.0,  # Pulse Hz
            right_frequency=200.0,  # Carrier Hz
            carrier_hz=200.0,  # Also set here for consistency
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0,
            beat_type="isochronic"
        )

    def test_block_generation(self):
        """Test that a block of isochronic tones is generated correctly."""
        gen = SourceCode.IsochronicGenerator(self.cfg)
        block = gen.generate_block(4410)  # 100ms, should contain one full pulse cycle

        self.assertEqual(block.shape, (4410, 2))
        self.assertEqual(block.dtype, np.float32)

        # Left and right channels should be identical
        self.assertTrue(np.allclose(block[:, 0], block[:, 1]))

        # The block should contain both sound and silence due to pulsing
        self.assertTrue(np.any(block))
        self.assertTrue(np.any(block == 0))

        # With a 10Hz pulse, the first half should have sound, second half should be silent
        half_point = len(block) // 2
        self.assertTrue(np.any(block[:half_point]))
        self.assertTrue(np.all(np.abs(block[half_point + 100: -100]) < 1e-6))  # Check middle of silent part


if __name__ == '__main__':
    unittest.main()