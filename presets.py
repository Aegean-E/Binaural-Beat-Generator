# presets.py
# Data-only preset definitions for the app.

MONAURAL_PRESETS = [
    {"label": "528 Hz Monaural Beat", "left_hz": 528.0, "right_hz": 528.0},
    {"label": "432 Hz Monaural Beat", "left_hz": 432.0, "right_hz": 432.0},
]

BINAURAL_PRESETS = [
    {"label": "6 Hz Binaural Beat, 528 Hz Carrier Frequency", "left_hz": 525.0, "right_hz": 531.0},
    {"label": "6 Hz Binaural Beat, 432 Hz Carrier Frequency", "left_hz": 429.0, "right_hz": 435.0},
    {"label": "16 Hz Binaural Beat, 528 Hz Carrier Frequency", "left_hz": 520.0, "right_hz": 536.0},
    {"label": "16 Hz Binaural Beat, 432 Hz Carrier Frequency", "left_hz": 424.0, "right_hz": 440.0},
    {"label": "40 Hz Binaural Beat, 528 Hz Carrier Frequency", "left_hz": 508.0, "right_hz": 548.0},
    {"label": "40 Hz Binaural Beat, 438 Hz Carrier Frequency", "left_hz": 418.0, "right_hz": 458.0},
]

ISOCHRONIC_PRESETS = [
    {"label": "4 Hz Pulse, 432 Hz Carrier", "carrier_hz": 432.0, "pulse_hz": 4.0},
    {"label": "8 Hz Pulse, 432 Hz Carrier", "carrier_hz": 432.0, "pulse_hz": 8.0},
    {"label": "16 Hz Pulse, 432 Hz Carrier", "carrier_hz": 432.0, "pulse_hz": 16.0},
    {"label": "40 Hz Pulse, 432 Hz Carrier", "carrier_hz": 432.0, "pulse_hz": 40.0},
]

BRAINWAVE_RANGES = {
    "Delta (0.5 - 4 Hz)": (0.5, 4.0),
    "Theta (4 - 8 Hz)": (4.0, 8.0),
    "Alpha (8 - 12 Hz)": (8.0, 12.0),
    "Beta (12 - 30 Hz)": (12.0, 30.0),
    "Gamma (30 - 80 Hz)": (30.0, 80.0),
}
