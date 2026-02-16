import sys
import unittest
from unittest.mock import MagicMock
from dataclasses import dataclass
import importlib.machinery
import importlib.util
import os

# Add project root to sys.path to find presets.py
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock dependencies before importing SourceCode
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['scipy.signal'] = MagicMock()
sys.modules['scipy.io'] = MagicMock()
sys.modules['scipy.io.wavfile'] = MagicMock()

# Setup mocks for numpy and scipy.signal
mock_np = MagicMock()
mock_np.sin = MagicMock()
mock_np.pi = 3.141592653589793
mock_np.float32 = float
mock_np.arange = MagicMock(return_value=[0.0, 1.0])
mock_np.column_stack = MagicMock(return_value=[[0.0, 0.0]])
mock_np.tanh = MagicMock(return_value=0.5)
mock_np.max = MagicMock(return_value=1.0)
mock_np.abs = MagicMock(return_value=0.5)
sys.modules['numpy'] = mock_np

# Import SourceCode
try:
    # Adjust path if running from tests/
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    source_path = os.path.join(project_root, 'SourceCode')
    if not os.path.exists(source_path):
        source_path = 'SourceCode' # Fallback if running from root

    loader = importlib.machinery.SourceFileLoader('SourceCode', source_path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    sc = importlib.util.module_from_spec(spec)
    loader.exec_module(sc)
except Exception as e:
    print(f"Error importing SourceCode: {e}")
    sys.exit(1)

class TestAudioConfig(unittest.TestCase):
    def test_start_stream_with_config(self):
        # Reset mocks
        sc.sd.OutputStream.reset_mock()

        cfg = sc.AudioConfig(
            sample_rate=44100,
            left_volume=0.5,
            right_volume=0.5,
            left_waveform="Sine",
            right_waveform="Sine",
            use_ramp=False,
            left_frequency=432.0,
            right_frequency=436.0,
            carrier_hz=0.0,
            start_beat_hz=0.0,
            end_beat_hz=0.0,
            ramp_minutes=0.0
        )

        sc._start_stream(cfg)

        # Verify OutputStream was created with correct sample rate
        sc.sd.OutputStream.assert_called_once()
        call_args = sc.sd.OutputStream.call_args
        self.assertEqual(call_args.kwargs['samplerate'], 44100)

        # Verify stream started
        sc.stream.start.assert_called_once()

if __name__ == '__main__':
    unittest.main()
