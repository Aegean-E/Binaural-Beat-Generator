<div align="center">

# Binaural Beat Generator 0.8.2

</div>


<div align="left">
  <img src="banner.png" width="1080" alt="Binaural Beat Generator - Banner">
  <br />
</div>

---

A scientifically verified **binaural and monaural beat generator** with a **standalone executable** for Windows.
This tool allows you to generate precise neuro-acoustic states using mathematically verified DSP algorithms.

Designed to be **simple, technical, and honest** : no accounts, no tracking, no cloud.

---

## 🔬 Scientific Signal Verification

This project implements a rigorous **Signal Verification Layer** to ensure that the audio output is mathematically precise and safe for neuro-acoustic usage.

### Verification Methodology
Every generated signal can be validated against the following criteria:

1.  **FFT Frequency Accuracy**:
    - The output is analyzed using Fast Fourier Transform (FFT) with zero-padding for high resolution.
    - We verify that the dominant peak in the Left channel matches `Carrier - (Beat / 2)`.
    - We verify that the dominant peak in the Right channel matches `Carrier + (Beat / 2)`.
    - Tolerance: ±0.1 Hz.

2.  **Amplitude Safety**:
    - **Clipping Check**: Ensures no sample exceeds 1.0 amplitude.
    - **RMS Stability**: Verifies the signal has consistent energy and is not silent.
    - **Soft Limiting**: A `tanh` soft limiter is applied to prevent harsh digital clipping while maximizing volume.

3.  **DC Offset**:
    - Checks that the mean amplitude is approximately 0.0 to prevent speaker damage or dynamic range loss.

4.  **Stereo Separation**:
    - Calculates the correlation coefficient between Left and Right channels.
    - For binaural beats, the correlation must be low (channels are distinct).
    - Ensures true stereo generation, not dual-mono.

5.  **Export Integrity**:
    - When exporting to WAV, the system generates the audio in memory, writes it to disk, reads it back, and compares the signals bit-by-bit (or within float tolerance) to ensure the file matches the live playback exactly.

### Debug & Verification Mode
You can run the application with the `--debug` flag to perform a self-test of the DSP engine upon startup:

```bash
python SourceCode --debug
```

This will generate a 1-second test tone (Alpha state) and print a full scientific report to the console, detailing measured frequencies, amplitude, and signal health.

---

## 🧠 Brainwave Presets

The generator includes standardized brainwave state presets. Selecting a preset automatically configures the beat frequency range for the **Ramp Mode**.

| State | Frequency Range | Associated Mental State |
| :--- | :--- | :--- |
| **Delta** | 0.5 – 4 Hz | Deep sleep, healing, detachment |
| **Theta** | 4 – 8 Hz | Meditation, intuition, memory |
| **Alpha** | 8 – 12 Hz | Relaxation, visualization, creativity |
| **Beta** | 12 – 30 Hz | Alertness, concentration, cognition |
| **Gamma** | 30 – 80 Hz | Peak focus, insight, high-level processing |

*Note: You can adjust the Carrier frequency (Base) independently. Lower carriers (e.g., 100-200Hz) are often preferred for Delta/Theta, while higher carriers (e.g., 400Hz+) are common for Alpha/Beta.*

---

## 🏗 Architecture Overview

### DSP Engine
The core audio generation is handled by the `BinauralGenerator` class.
- **Formula**: $A(t) = \sin(2\pi \cdot f \cdot t + \phi)$
- **Phase Accumulation**: We use cumulative phase summation (`numpy.cumsum`) rather than absolute time calculations (`t * f`) for the ramp mode. This ensures **phase continuity** when frequency changes dynamically, preventing clicks or artifacts.
- **Precision**: All internal DSP is done in **float64** (time accumulation) and **float32** (audio buffer) to balance precision and performance.

### Audio Pipeline
1.  **Configuration**: User inputs are validated and converted to an `AudioConfig` dataclass.
2.  **Generation**: `generate_block()` produces chunks of audio (e.g., 100ms).
3.  **Post-Processing**:
    - **Ramping**: Linearly interpolates beat frequency if enabled.
    - **Limiting**: `tanh` soft clipper.
    - **Fading**: 20ms Fade-In/Out applied to start/stop transitions.
4.  **Output**:
    - **Live**: Streamed via `sounddevice` (PortAudio).
    - **Export**: Written to WAV via `scipy.io.wavfile` in a background thread.

---

## 🧪 Testing & Validation

The project includes a comprehensive test suite to ensure stability and accuracy.

### Running Tests
To run the scientific verification tests (requires `numpy`, `scipy`, `sounddevice`):

```bash
python -m unittest tests/test_scientific_verification.py
```

### Test Coverage
- `test_frequency_accuracy`: Generates audio and verifies spectral peaks.
- `test_amplitude_bounds`: Ensures safety limits are respected.
- `test_stereo_separation`: Confirms channel independence.
- `test_export_integrity`: Validates file I/O against memory generation.

---

## Features

- **Precise Binaural & Monaural Beats**
- **Scientifically Verified Output**
- **Brainwave Presets (Delta, Theta, Alpha, Beta, Gamma)**
- **Ramp Mode** (Targeted frequency shifts)
- **High-Quality WAV Export**
- **Real-Time Status Display**
- **Theme Support** (Dark/Light modes)
- **No Installation Required** (Standalone EXE available)

---

## Privacy & Philosophy

- No Telemetry
- No Analytics
- No Internet Usage
- No Background Services

This is a **local tool**. Nothing leaves your machine.

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

- **Twitter**: [@Aegean_E](https://twitter.com/@Aegean_E)  
- **YouTube**: [Aegean_E](https://youtube.com/@Aegean_E)  
- **Patreon**: [Aegean_E](https://www.patreon.com/Aegean_E)  

---

**Ægean - 2023-2026**
