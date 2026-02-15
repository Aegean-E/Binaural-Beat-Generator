import pytest
import sys
from unittest.mock import MagicMock

# Mock dependencies before importing the module under test
# This allows the module to be imported even if these packages are not installed.
mock_modules = [
    "numpy",
    "sounddevice",
    "scipy",
    "scipy.signal",
    "ttkbootstrap",
    "tkinter",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.filedialog",
]

for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# Now import the function from SourceCode.py
from SourceCode import _normalize_category

def test_normalize_category_valid_binaural():
    """Test that 'Binaural' in various forms is correctly normalized."""
    assert _normalize_category("Binaural") == "Binaural"
    assert _normalize_category("binaural") == "Binaural"
    assert _normalize_category("  BINAURAL  ") == "Binaural"

def test_normalize_category_valid_monaural():
    """Test that 'Monaural' in various forms is correctly normalized."""
    assert _normalize_category("Monaural") == "Monaural"
    assert _normalize_category("monaural") == "Monaural"
    assert _normalize_category("  MONAURAL  ") == "Monaural"

def test_normalize_category_invalid():
    """Test that invalid category strings raise a ValueError with the expected message."""
    expected_msg = "Category must be 'Monaural' or 'Binaural'"

    with pytest.raises(ValueError, match=expected_msg):
        _normalize_category("Invalid")

    with pytest.raises(ValueError, match=expected_msg):
        _normalize_category("Stereo")

    with pytest.raises(ValueError, match=expected_msg):
        _normalize_category("")

    with pytest.raises(ValueError, match=expected_msg):
        _normalize_category(None)
