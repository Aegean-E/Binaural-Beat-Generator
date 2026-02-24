"""Test generator classes."""

import unittest
import sys
import os
import math
from unittest.mock import MagicMock, patch, call

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def create_numpy_mock():
    """Create a more complete numpy mock."""
    import numpy as np
    return np


class TestBinauralGenerator(unittest.TestCase):
    """Test BinauralGenerator class."""
    
    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.np = np
        
        # Import SourceCode
        import SourceCode as sc
        cls.sc = sc
        
        # Create config
        cls.cfg = sc.AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            noise_type="None",
            noise_volume=0.0,
            use_ramp=False,
            left_frequency=432.0,
            right_frequency=440.0,
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0,
            beat_type="binaural"
        )
    
    def test_generator_initialization(self):
        """Test BinauralGenerator initializes correctly."""
        gen = self.sc.BinauralGenerator(self.cfg)
        
        self.assertEqual(gen.samples_generated, 0)
        self.assertEqual(gen.phase_l, 0.0)
        self.assertEqual(gen.phase_r, 0.0)
    
    def test_generator_creates_output(self):
        """Test BinauralGenerator creates audio output."""
        gen = self.sc.BinauralGenerator(self.cfg)
        frames = 1024
        
        output = gen.generate_block(frames)
        
        # Should generate stereo output
        self.assertEqual(output.shape[0], frames)
        self.assertEqual(output.shape[1], 2)  # stereo
        self.assertEqual(gen.samples_generated, frames)
    
    def test_generator_fade_in(self):
        """Test fade-in at start."""
        gen = self.sc.BinauralGenerator(self.cfg)
        frames = 1024
        
        output = gen.generate_block(frames)
        
        # First few samples should be ramping up (less than max)
        # and last few should be at full amplitude
        self.assertLess(output[0, 0], output[frames//2, 0])
    
    def test_request_stop(self):
        """Test request_stop sets stopping flag."""
        gen = self.sc.BinauralGenerator(self.cfg)
        gen.request_stop()
        
        self.assertTrue(gen.stopping)


class TestMonauralGenerator(unittest.TestCase):
    """Test MonauralGenerator class."""
    
    @classmethod
    def setUpClass(cls):
        import SourceCode as sc
        cls.sc = sc
        
        cls.cfg = sc.AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            noise_type="None",
            noise_volume=0.0,
            use_ramp=False,
            left_frequency=528.0,
            right_frequency=528.0,
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0,
            beat_type="monaural"
        )
    
    def test_generator_initialization(self):
        """Test MonauralGenerator initializes correctly."""
        gen = self.sc.MonauralGenerator(self.cfg)
        
        self.assertEqual(gen.samples_generated, 0)
    
    def test_generator_creates_output(self):
        """Test MonauralGenerator creates audio output."""
        gen = self.sc.MonauralGenerator(self.cfg)
        frames = 1024
        
        output = gen.generate_block(frames)
        
        self.assertEqual(output.shape[0], frames)
        self.assertEqual(output.shape[1], 2)


class TestIsochronicGenerator(unittest.TestCase):
    """Test IsochronicGenerator class."""
    
    @classmethod
    def setUpClass(cls):
        import SourceCode as sc
        cls.sc = sc
        
        cls.cfg = sc.AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            noise_type="None",
            noise_volume=0.0,
            use_ramp=False,
            left_frequency=10.0,
            right_frequency=432.0,
            carrier_hz=432.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0,
            beat_type="isochronic"
        )
    
    def test_generator_initialization(self):
        """Test IsochronicGenerator initializes correctly."""
        gen = self.sc.IsochronicGenerator(self.cfg)
        
        self.assertEqual(gen.samples_generated, 0)
        self.assertEqual(gen.phase, 0.0)
    
    def test_generator_creates_output(self):
        """Test IsochronicGenerator creates audio output."""
        gen = self.sc.IsochronicGenerator(self.cfg)
        frames = 1024
        
        output = gen.generate_block(frames)
        
        self.assertEqual(output.shape[0], frames)
        self.assertEqual(output.shape[1], 2)
    
    def test_generator_pulse_modulation(self):
        """Test IsochronicGenerator has pulsing."""
        gen = self.sc.IsochronicGenerator(self.cfg)
        frames = 44100  # 1 second
        
        output = gen.generate_block(frames)
        
        # Should have variation (pulsing)
        # Not all samples should be the same
        channel = output[:, 0]
        has_variation = False
        for i in range(1, len(channel)):
            if abs(channel[i] - channel[i-1]) > 0.01:
                has_variation = True
                break
        
        self.assertTrue(has_variation)
    
    def test_request_stop(self):
        """Test request_stop sets stopping flag."""
        gen = self.sc.IsochronicGenerator(self.cfg)
        gen.request_stop()
        
        self.assertTrue(gen.stopping)


class TestGeneratorWaveforms(unittest.TestCase):
    """Test generator with different waveforms."""
    
    @classmethod
    def setUpClass(cls):
        import SourceCode as sc
        cls.sc = sc
    
    def test_generator_with_sine(self):
        """Test generator with Sine waveform."""
        cfg = self.sc.AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            noise_type="None",
            noise_volume=0.0,
            use_ramp=False,
            left_frequency=440.0,
            right_frequency=444.0,
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_duration_s=0.0,
            beat_type="binaural"
        )
        
        gen = self.sc.BinauralGenerator(cfg)
        output = gen.generate_block(1024)
        
        self.assertEqual(output.shape, (1024, 2))
    
    def test_generator_with_ramp(self):
        """Test generator with ramp enabled."""
        cfg = self.sc.AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            noise_type="None",
            noise_volume=0.0,
            use_ramp=True,
            left_frequency=440.0,
            right_frequency=444.0,
            carrier_hz=200.0,
            start_beat_hz=10.0,
            end_beat_hz=20.0,
            ramp_duration_s=60.0,
            beat_type="binaural"
        )
        
        gen = self.sc.BinauralGenerator(cfg)
        
        # First block
        output1 = gen.generate_block(44100)
        self.assertEqual(output1.shape[0], 44100)
        
        # Second block  
        output2 = gen.generate_block(44100)
        self.assertEqual(output2.shape[0], 44100)


if __name__ == '__main__':
    unittest.main()
