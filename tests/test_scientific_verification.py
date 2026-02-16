import unittest
import sys
import os
import importlib.util
from unittest.mock import MagicMock

# Check for scientific dependencies
HAS_DEPS = False
try:
    import numpy as np
    import scipy
    import sounddevice
    # Check if they are mocks (test pollution from other tests)
    if isinstance(np, MagicMock) or hasattr(np, 'reset_mock'):
        HAS_DEPS = False
    else:
        HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

# Mock dependencies if missing to allow importing SourceCode and defining tests
if not HAS_DEPS:
    sys.modules['numpy'] = MagicMock()
    sys.modules['scipy'] = MagicMock()
    sys.modules['scipy.signal'] = MagicMock()
    sys.modules['scipy.io'] = MagicMock()
    sys.modules['scipy.io.wavfile'] = MagicMock()
    sys.modules['sounddevice'] = MagicMock()

# Always mock UI for headless testing
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.simpledialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()

# Import SourceCode dynamically
import importlib.machinery
try:
    loader = importlib.machinery.SourceFileLoader('SourceCode', 'SourceCode')
    spec = importlib.util.spec_from_loader(loader.name, loader)
    SourceCode = importlib.util.module_from_spec(spec)
    sys.modules["SourceCode"] = SourceCode
    loader.exec_module(SourceCode)
    BinauralGenerator = SourceCode.BinauralGenerator
    AudioConfig = SourceCode.AudioConfig
except Exception as e:
    # If we are in tests/ directory, we might need to look up one level
    try:
        loader = importlib.machinery.SourceFileLoader('SourceCode', '../SourceCode')
        spec = importlib.util.spec_from_loader(loader.name, loader)
        SourceCode = importlib.util.module_from_spec(spec)
        sys.modules["SourceCode"] = SourceCode
        loader.exec_module(SourceCode)
        BinauralGenerator = SourceCode.BinauralGenerator
        AudioConfig = SourceCode.AudioConfig
    except Exception as e2:
        print(f"Warning: Failed to import SourceCode: {e}, {e2}")
        SourceCode = None

import verification

class TestScientificVerification(unittest.TestCase):

    @unittest.skipIf(not HAS_DEPS, "Scientific dependencies (numpy/scipy) not installed")
    def test_frequency_accuracy(self):
        """Verify that generated frequencies match the configuration."""
        cfg = AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            use_ramp=False,
            left_frequency=440.0,
            right_frequency=450.0, # 10Hz beat
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0
        )
        gen = BinauralGenerator(cfg)
        audio = gen.generate_block(44100 * 1) # 1 second

        errors = verification.validate_signal(audio, 44100, 440.0, 450.0, 1.0)
        self.assertEqual(errors, [], "Signal validation failed: " + str(errors))

    @unittest.skipIf(not HAS_DEPS, "Scientific dependencies not installed")
    def test_amplitude_bounds(self):
        """Verify that amplitude does not exceed limits."""
        cfg = AudioConfig(
            sample_rate=44100,
            left_volume=1.0, # Max volume
            right_volume=1.0,
            left_waveform="Sine",
            right_waveform="Sine",
            use_ramp=False,
            left_frequency=100.0,
            right_frequency=100.0,
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0
        )
        gen = BinauralGenerator(cfg)
        audio = gen.generate_block(1000)

        self.assertTrue(np.max(np.abs(audio)) <= 1.0, "Amplitude exceeded 1.0")

    @unittest.skipIf(not HAS_DEPS, "Scientific dependencies not installed")
    def test_stereo_separation(self):
        """Verify stereo separation for binaural beats."""
        cfg = AudioConfig(
            sample_rate=44100,
            left_volume=0.8,
            right_volume=0.8,
            left_waveform="Sine",
            right_waveform="Sine",
            use_ramp=False,
            left_frequency=440.0,
            right_frequency=450.0, # 10Hz beat
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0
        )
        gen = BinauralGenerator(cfg)
        audio = gen.generate_block(44100)

        # Manually check correlation or use verification module
        left = audio[:, 0]
        right = audio[:, 1]
        corr = np.corrcoef(left, right)[0, 1]
        self.assertLess(corr, 0.99, "Stereo channels are too correlated for binaural beat")

    @unittest.skipIf(not HAS_DEPS, "Scientific dependencies not installed")
    def test_export_integrity(self):
        """Verify that exported audio matches generated audio."""
        cfg = AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            use_ramp=False,
            left_frequency=440.0,
            right_frequency=444.0,
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0
        )

        errors = verification.validate_export(BinauralGenerator, cfg, 0.5) # 0.5s duration
        self.assertEqual(errors, [], "Export validation failed: " + str(errors))

    @unittest.skipIf(not HAS_DEPS, "Scientific dependencies not installed")
    def test_long_duration_stability(self):
        """Simulate a long session to check for phase drift or float errors."""
        cfg = AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            use_ramp=True,
            left_frequency=0.0,
            right_frequency=0.0,
            carrier_hz=440.0,
            start_beat_hz=10.0,
            end_beat_hz=5.0,
            ramp_duration_s=30.0 * 60.0
        )
        gen = BinauralGenerator(cfg)

        # Simulate 20 minutes passed
        minutes_passed = 20
        samples_passed = int(minutes_passed * 60 * 44100)
        gen.samples_generated = samples_passed

        # Generate a block at this late time
        block = gen.generate_block(44100) # 1 second

        # Check for NaNs
        self.assertFalse(np.isnan(block).any(), "NaN values detected after long duration")

        # Check Amplitude
        self.assertTrue(np.max(np.abs(block)) <= 1.0, "Amplitude instability detected")

        # Check that frequency is roughly correct
        # At 20 mins of 30 mins ramp from 10 to 5 Hz:
        # Progress = 20/30 = 0.666
        # Beat = 10 + (5 - 10) * 0.666 = 10 - 3.33 = 6.66 Hz
        expected_beat = 10.0 + (5.0 - 10.0) * (20.0 / 30.0)

        # Analyze beat frequency of this block
        # (Simplified check: just beat frequency via zero crossings or similar? Or verification module)
        # Using verification module

        # Calculate expected L/R
        # L = Carrier - Beat/2
        # R = Carrier + Beat/2
        # Note: The generator uses instantaneous frequency. Over 1 second, it changes slightly.
        # But 6.66Hz beat is slow change.

        expected_l = 440.0 - (expected_beat / 2.0)
        expected_r = 440.0 + (expected_beat / 2.0)

        errors = verification.validate_signal(block, 44100, expected_l, expected_r, 1.0, tolerance_hz=0.5)
        self.assertEqual(errors, [], "Long duration signal validation failed: " + str(errors))

if __name__ == '__main__':
    unittest.main()
