import unittest
from unittest.mock import MagicMock, patch
import sys
import importlib.machinery
import importlib.util

class TestSourceCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock dependencies
        cls.mock_numpy = MagicMock()
        cls.mock_sounddevice = MagicMock()
        cls.mock_scipy = MagicMock()
        cls.mock_ttkbootstrap = MagicMock()
        cls.mock_tkinter = MagicMock()

        # Apply mocks
        cls.modules_patcher = patch.dict(sys.modules, {
            'numpy': cls.mock_numpy,
            'sounddevice': cls.mock_sounddevice,
            'scipy': cls.mock_scipy,
            'scipy.signal': cls.mock_scipy.signal,
            'ttkbootstrap': cls.mock_ttkbootstrap,
            'tkinter': cls.mock_tkinter,
            'tkinter.ttk': cls.mock_tkinter.ttk,
            'tkinter.messagebox': cls.mock_tkinter.messagebox,
            'tkinter.filedialog': cls.mock_tkinter.filedialog
        })
        cls.modules_patcher.start()

        # Import SourceCode
        # We need to use SourceFileLoader because the file has no extension
        loader = importlib.machinery.SourceFileLoader('SourceCode', 'SourceCode')
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        sys.modules['SourceCode'] = mod
        loader.exec_module(mod)
        cls.SourceCode = mod

    @classmethod
    def tearDownClass(cls):
        cls.modules_patcher.stop()

    def setUp(self):
        # Reset mocks before each test
        self.mock_numpy.reset_mock()

    def test_soft_limiter_defaults(self):
        """Test that soft_limiter uses the correct default drive."""
        import inspect
        sig = inspect.signature(self.SourceCode.soft_limiter)
        drive_param = sig.parameters['drive']
        self.assertEqual(drive_param.default, self.SourceCode.LIMITER_DRIVE)
        self.assertEqual(self.SourceCode.LIMITER_DRIVE, 2.5)

    def test_soft_limiter_calls_numpy(self):
        """Test soft_limiter logic calls numpy functions."""
        stereo_audio = MagicMock()
        drive = 2.5

        # Setup mocks
        mock_tanh_res = MagicMock()
        self.mock_numpy.tanh.return_value = mock_tanh_res

        self.mock_numpy.max.return_value = 0.5 # peak <= 1.0

        result = self.SourceCode.soft_limiter(stereo_audio, drive)

        # Verify calls
        # Check that tanh was called with drive (for the divisor)
        self.mock_numpy.tanh.assert_any_call(drive)

        # Check that max and abs were called for peak detection
        self.mock_numpy.abs.assert_called()
        self.mock_numpy.max.assert_called()

if __name__ == '__main__':
    unittest.main()
