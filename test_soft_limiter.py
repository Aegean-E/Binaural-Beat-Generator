import sys
import unittest
from unittest.mock import MagicMock
import types
import math
import importlib.machinery
import importlib.util

# --- Mock Setup ---

# Always mock sounddevice, scipy, ttkbootstrap as per instructions/environment constraints
sys.modules["sounddevice"] = MagicMock()
mock_scipy = MagicMock()
mock_signal = MagicMock()
mock_signal.square = MagicMock(return_value=0.0)
mock_signal.sawtooth = MagicMock(return_value=0.0)
mock_scipy.signal = mock_signal
sys.modules["scipy"] = mock_scipy
sys.modules["scipy.signal"] = mock_signal
sys.modules["ttkbootstrap"] = MagicMock()

# --- Numpy Handling ---

USE_FAKE_NUMPY = False
try:
    import numpy as np
except ImportError:
    USE_FAKE_NUMPY = True

if USE_FAKE_NUMPY:
    # Define FakeNumpy Implementation
    class FakeArray:
        def __init__(self, data):
            if not isinstance(data, list):
                raise ValueError("FakeArray data must be a list")
            self.data = data
            if len(data) > 0 and isinstance(data[0], list):
                self.shape = (len(data), len(data[0]))
            else:
                self.shape = (len(data),)

        def __repr__(self):
            return f"FakeArray({self.data})"

        def _apply_op(self, other, op):
            if isinstance(other, (int, float)):
                if len(self.shape) == 2:
                    new_data = [[op(x, other) for x in row] for row in self.data]
                else:
                    new_data = [op(x, other) for x in self.data]
                return FakeArray(new_data)
            elif isinstance(other, FakeArray):
                if self.shape != other.shape:
                    raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
                if len(self.shape) == 2:
                    new_data = [[op(self.data[i][j], other.data[i][j]) for j in range(self.shape[1])] for i in range(self.shape[0])]
                else:
                    new_data = [op(self.data[i], other.data[i]) for i in range(self.shape[0])]
                return FakeArray(new_data)
            else:
                return NotImplemented

        def __mul__(self, other):
            return self._apply_op(other, lambda a, b: a * b)

        def __rmul__(self, other):
            return self._apply_op(other, lambda a, b: b * a)

        def __truediv__(self, other):
            return self._apply_op(other, lambda a, b: a / b)

        def __rtruediv__(self, other):
            return self._apply_op(other, lambda a, b: b / a)

        def astype(self, dtype, copy=True):
            return self

    class FakeNumpy:
        def __init__(self):
            self.float32 = float
            self.pi = math.pi
            self.float64 = float
            self.ndarray = FakeArray

        def array(self, data, dtype=None):
            return FakeArray(data)

        def sin(self, x):
            if isinstance(x, FakeArray):
                if len(x.shape) == 2:
                    new_data = [[math.sin(val) for val in row] for row in x.data]
                else:
                    new_data = [math.sin(val) for val in x.data]
                return FakeArray(new_data)
            return math.sin(x)

        def tanh(self, x):
            if isinstance(x, FakeArray):
                if len(x.shape) == 2:
                    new_data = [[math.tanh(val) for val in row] for row in x.data]
                else:
                    new_data = [math.tanh(val) for val in x.data]
                return FakeArray(new_data)
            return math.tanh(x)

        def max(self, x):
            if isinstance(x, FakeArray):
                if len(x.shape) == 2:
                    flat = [val for row in x.data for val in row]
                else:
                    flat = x.data
                return max(flat) if flat else 0.0
            return x

        def abs(self, x):
            if isinstance(x, FakeArray):
                if len(x.shape) == 2:
                    new_data = [[abs(val) for val in row] for row in x.data]
                else:
                    new_data = [abs(val) for val in x.data]
                return FakeArray(new_data)
            return abs(x)

        def arange(self, *args, **kwargs):
            return FakeArray([])

        def column_stack(self, tup):
            return FakeArray([])

    fake_np = FakeNumpy()
    sys.modules["numpy"] = fake_np
    np = fake_np # use fake_np as np locally

# --- Import SourceCode ---

loader = importlib.machinery.SourceFileLoader("SourceCode", "SourceCode")
spec = importlib.util.spec_from_loader(loader.name, loader)
source_code_module = importlib.util.module_from_spec(spec)
# If real numpy was imported, SourceCode will use it.
# If fake numpy was patched, SourceCode will use it.
sys.modules["SourceCode"] = source_code_module
loader.exec_module(source_code_module)

soft_limiter = source_code_module.soft_limiter

# --- Tests ---

class TestSoftLimiter(unittest.TestCase):

    def create_array(self, data):
        if USE_FAKE_NUMPY:
            return FakeArray(data)
        else:
            return np.array(data, dtype=float)

    def test_soft_limiter_basic(self):
        input_data = [[0.1, -0.1], [0.2, -0.2]]
        arr = self.create_array(input_data)
        drive = 1.0

        output = soft_limiter(arr, drive=drive)

        # Validation
        if USE_FAKE_NUMPY:
            self.assertIsInstance(output, FakeArray)
            val00 = output.data[0][0]
            val01 = output.data[0][1]
        else:
            self.assertIsInstance(output, np.ndarray)
            val00 = output[0][0]
            val01 = output[0][1]

        expected00 = math.tanh(0.1) / math.tanh(1.0)
        self.assertAlmostEqual(val00, expected00, places=5)

        expected01 = math.tanh(-0.1) / math.tanh(1.0)
        self.assertAlmostEqual(val01, expected01, places=5)

    def test_soft_limiter_clipping(self):
        input_data = [[10.0, -10.0]]
        arr = self.create_array(input_data)

        output = soft_limiter(arr, drive=2.5)

        if USE_FAKE_NUMPY:
            peak = np.max(np.abs(output))
            val00 = abs(output.data[0][0])
        else:
            peak = np.max(np.abs(output))
            val00 = abs(output[0][0])

        self.assertAlmostEqual(peak, 1.0, places=5)
        self.assertAlmostEqual(val00, 1.0, places=5)

    def test_soft_limiter_zero(self):
        input_data = [[0.0, 0.0]]
        arr = self.create_array(input_data)

        output = soft_limiter(arr, drive=2.5)

        if USE_FAKE_NUMPY:
            val00 = output.data[0][0]
            val01 = output.data[0][1]
        else:
            val00 = output[0][0]
            val01 = output[0][1]

        self.assertEqual(val00, 0.0)
        self.assertEqual(val01, 0.0)

if __name__ == '__main__':
    unittest.main()
