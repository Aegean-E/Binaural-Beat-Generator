import unittest
import sys
import os
import importlib.machinery
import importlib.util
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.simpledialog'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()
sys.modules['scipy.io'] = MagicMock()
sys.modules['scipy.io.wavfile'] = MagicMock()

# Mock numpy
mock_np = MagicMock()
sys.modules['numpy'] = mock_np

# Setup numpy mocks to return usable objects
mock_np.float32 = float
mock_np.pi = 3.14159
mock_np.arange.return_value = MagicMock() # Represents array
mock_np.sin.return_value = MagicMock()
mock_np.tanh.return_value = MagicMock()
mock_np.clip.return_value = MagicMock()
mock_np.column_stack.return_value = MagicMock() # Represents stereo array
mock_np.concatenate.return_value = MagicMock()

# Load SourceCode
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Force reload to pick up mocks
if 'SourceCode' in sys.modules:
    del sys.modules['SourceCode']

try:
    loader = importlib.machinery.SourceFileLoader('SourceCode', 'SourceCode')
    spec = importlib.util.spec_from_loader(loader.name, loader)
    sc = importlib.util.module_from_spec(spec)
    loader.exec_module(sc)
except Exception as e:
    print(f"Error importing SourceCode: {e}")
    sys.exit(1)

class TestBinauralGenerator(unittest.TestCase):
    def setUp(self):
        self.cfg = sc.AudioConfig(
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
            ramp_minutes=0.0
        )
        # Reset mocks
        mock_np.arange.reset_mock()
        mock_np.sin.reset_mock()
        mock_np.clip.reset_mock()

    def test_initialization(self):
        gen = sc.BinauralGenerator(self.cfg)
        self.assertEqual(gen.samples_generated, 0)
        self.assertEqual(gen.phase_l, 0.0)
        self.assertEqual(gen.phase_r, 0.0)

    def test_generate_block_manual(self):
        gen = sc.BinauralGenerator(self.cfg)
        frames = 1024

        # Call generate
        output = gen.generate_block(frames)

        # Verify sample count incremented
        self.assertEqual(gen.samples_generated, frames)

        # Verify numpy calls
        mock_np.arange.assert_called_with(frames, dtype=float)

        # Verify phase update happened
        self.assertTrue(mock_np.sin.called)

        # Verify clip was called (stateless limiter)
        mock_np.clip.assert_called()

    def test_generate_block_ramp(self):
        self.cfg.use_ramp = True
        self.cfg.ramp_minutes = 1.0
        self.cfg.start_beat_hz = 10.0
        self.cfg.end_beat_hz = 5.0
        self.cfg.carrier_hz = 200.0

        gen = sc.BinauralGenerator(self.cfg)
        frames = 44100 # 1 second

        gen.generate_block(frames)

        # Check samples
        self.assertEqual(gen.samples_generated, 44100)

        # Call again
        gen.generate_block(frames)
        self.assertEqual(gen.samples_generated, 88200)

class TestExport(unittest.TestCase):
    def test_export_audio_file(self):
        # Setup global root mock
        sc.root = MagicMock()

        # Mock dependencies
        with patch.object(sc.filedialog, 'asksaveasfilename') as mock_asksaveas, \
             patch.object(sc.simpledialog, 'askstring') as mock_askstring, \
             patch.object(sc.wavfile, 'write') as mock_write, \
             patch.object(sc.root, 'update') as mock_update, \
             patch.object(sc, 'BinauralGenerator') as MockGen:

            # Setup inputs
            sc.left_volume_entry = MagicMock()
            sc.left_volume_entry.get.return_value = "50"
            sc.right_volume_entry = MagicMock()
            sc.right_volume_entry.get.return_value = "50"

            sc.left_frequency_entry = MagicMock()
            sc.left_frequency_entry.get.return_value = "440"
            sc.right_frequency_entry = MagicMock()
            sc.right_frequency_entry.get.return_value = "444"

            sc.ramp_enabled_var = MagicMock()
            sc.ramp_enabled_var.get.return_value = False

            sc.left_waveform_var = MagicMock()
            sc.left_waveform_var.get.return_value = "Sine"
            sc.right_waveform_var = MagicMock()
            sc.right_waveform_var.get.return_value = "Sine"

            # Mock dialogs
            mock_askstring.return_value = "1" # 1 second duration
            mock_asksaveas.return_value = "test_output.wav"

            mock_gen_instance = MockGen.return_value
            mock_gen_instance.generate_block.return_value = MagicMock() # Audio block

            sc.export_audio_file()

            # Verify generator was initialized
            MockGen.assert_called()

            # Verify generate_block was called
            self.assertTrue(mock_gen_instance.generate_block.called)

            # Verify write was called
            mock_write.assert_called()
            args, _ = mock_write.call_args
            self.assertEqual(args[0], "test_output.wav")
            self.assertEqual(args[1], 44100)

class TestValidation(unittest.TestCase):
    def test_validate_audio_params(self):
        # Valid
        self.assertIsNone(sc.validate_audio_params(440, 444, 50, 50))

        # Invalid Freq
        self.assertIsNotNone(sc.validate_audio_params(0, 444, 50, 50))
        self.assertIsNotNone(sc.validate_audio_params(2000, 444, 50, 50))

        # Invalid Volume
        self.assertIsNotNone(sc.validate_audio_params(440, 444, -10, 50))
        self.assertIsNotNone(sc.validate_audio_params(440, 444, 50, 110))

        # Invalid Duration
        self.assertIsNotNone(sc.validate_audio_params(440, 444, 50, 50, duration=0))
        self.assertIsNotNone(sc.validate_audio_params(440, 444, 50, 50, duration=-5))

if __name__ == '__main__':
    unittest.main()
