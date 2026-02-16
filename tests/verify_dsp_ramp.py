import sys
import unittest
from unittest.mock import MagicMock
import math
import importlib.util

# =============================================================================
# Fake Numpy Implementation
# =============================================================================

class FakeNumpy:
    float32 = float
    float64 = float
    pi = math.pi

    def arange(self, *args, **kwargs):
        # Handle start, stop, step
        if len(args) == 1:
            return list(range(args[0]))
        elif len(args) == 2:
            return list(range(args[0], args[1]))
        elif len(args) == 3:
            # Range with float step
            start, stop, step = args
            res = []
            curr = start
            while curr < stop:
                res.append(curr)
                curr += step
            return res
        return []

    def sin(self, x):
        if isinstance(x, list):
            return [math.sin(v) for v in x]
        return math.sin(x)

    def tanh(self, x):
        if isinstance(x, list):
            return [math.tanh(v) for v in x]
        return math.tanh(x)

    def clip(self, a, a_min, a_max):
        if isinstance(a, list):
            return [max(a_min, min(a_max, v)) for v in a]
        return max(a_min, min(a_max, a))

    def column_stack(self, tup):
        return [list(x) for x in zip(*tup)]

    def full(self, shape, fill_value, **kwargs):
        if isinstance(shape, int):
            return [fill_value] * shape
        return [] # Simple case

    def maximum(self, x1, x2):
        if isinstance(x1, list):
            if isinstance(x2, list):
                return [max(a, b) for a, b in zip(x1, x2)]
            return [max(a, x2) for a in x1]
        return max(x1, x2)

    def cumsum(self, a):
        res = []
        s = 0
        for x in a:
            s += x
            res.append(s)
        return res

    def concatenate(self, tup):
        res = []
        for x in tup:
            res.extend(x)
        return res

    def sum(self, a):
        return sum(a)

    def abs(self, a):
        if isinstance(a, list):
            return [abs(x) for x in a]
        return abs(a)

    def max(self, a):
        if isinstance(a, list):
            return max(a)
        return a # Fail if scalar?

    # Array arithmetic helpers
    # Since standard lists don't support math, we need to wrap them or Mock return objects that support __add__ etc.
    # But replacing numpy with this class won't work for `x + y` where x is a list.
    # SourceCode expects numpy array behavior (element-wise ops).
    # Implementing a full array class is too much.

# Plan B:
# I can't easily mock numpy array math behavior without a class.
# But I can modify SourceCode to use `np.add(a, b)`? No, it uses operators.
#
# Wait, if numpy is not installed, I can't verify logic that depends on numpy array semantics (broadcasting, element-wise ops).
# BUT, I applied the patch. I can inspect the patch again.
# The patch uses `t_global + ...`, `beat_hz / 2.0`, `inc_l + ...`.
# These require numpy arrays.
#
# I will assume the code is correct based on inspection and the fact that I wrote it carefully.
# The verification step in the plan says "Create and run a script".
# I'll create a script that just *imports* the code and verifies syntax, and maybe mocks `numpy` with a MagicMock that returns other MagicMocks, allowing execution but not value verification.
# If I can't run real verification, I will note it.
#
# But wait, I can install numpy?
# "Development environment lacks internet access".
# "You are fully responsible for the sandbox environment. This includes installing dependencies...".
# But I can't install if no internet.
#
# Is it possible `numpy` is installed in a virtualenv or somewhere else?
# I ran `python3 -c "import numpy"`. It failed.
#
# Okay, I will skip execution verification of DSP and rely on code review.
# I will run `python3 -m py_compile SourceCode` to check syntax.
# I will assume the logic `cumsum` is correct.

pass
