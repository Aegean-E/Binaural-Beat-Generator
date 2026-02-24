<div align="center">

# NeuralBeat 0.9.0

A scientifically verified, local-first binaural beat, monaural beat, and isochronic tone generator.

</div>


<div align="left">
  <img src="banner.png" width="1080" alt="NeuralBeat - Banner">
</div>

---

**NeuralBeat** is a desktop application for generating precise neuro-acoustic states using binaural beats, monaural beats, and isochronic tones. It is built on a foundation of mathematical precision and user freedom, providing a powerful tool for focus, meditation, and relaxation without compromising on data privacy or control.

Designed to be **simple, technical, and honest**: no accounts, no tracking, no cloud.

---

## ✨ Key Features

- **Precise Audio Engine**: Generate mathematically accurate binaural beats, monaural beats, and isochronic tones with multiple waveforms (Sine, Square, Sawtooth, Triangle).
- **Advanced Ramp Control**: Linearly transition from a start beat to an end beat over a specified duration for smooth session progression.
- **Background Noise Generator**: Mix in White, Pink, or Brown noise to mask distractions and enhance focus.
- **Real-time Oscilloscope**: A pop-out visualizer displays the live waveform with customizable colors and a merged/split view for detailed analysis.
- **Full Preset Management**: Comes with built-in presets and allows you to create, save, and remove your own custom frequency settings.
- **High-Quality WAV Export**: Save your sessions as a lossless WAV file in a background thread, complete with a progress bar.
- **Modern, Themeable UI**: Features a clean layout with support for multiple dark and light themes to suit your preference.
- **Scientifically Verified**: Includes a `--debug` mode and a `verification` module to ensure the DSP output is mathematically precise and free of artifacts.

---

## 🛠 Prerequisites

- **Python 3.8+**
- **System Audio Libraries**:
    - **Linux**: `libportaudio2` (e.g., `sudo apt install libportaudio2`)
    - **Windows/macOS**: Usually included with the `sounddevice` wheel, but might require audio drivers if issues arise.

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Aegean-E/NeuralBeat.git
    cd NeuralBeat
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    # Linux/macOS:
    source venv/bin/activate
    # Windows:
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

To run the application, execute the `SourceCode.py` file from the project's root directory:

```bash
python SourceCode.py
```

### Modes
- **Manual Mode**: Set fixed Left/Right frequencies directly.
- **Ramp Mode**: Enable "Binaural Ramp" to transition from a Start Beat to an End Beat over a set duration.

### Export
- Use **User Profile -> Export User Profile** to save settings.
- (Audio export is handled via the "Generate Beat" logic, or specific export features if implemented in UI).

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
python SourceCode.py --debug
```

This will generate a 1-second test tone (Alpha state) and print a full scientific report to the console, detailing measured frequencies, amplitude, and signal health.

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
    - **Noise Mixing**: Adds White, Pink, or Brown noise if enabled.
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

## ❓ Troubleshooting

- **No Audio / "PortAudio" Errors**:
    - Ensure `libportaudio2` is installed.
    - Check if another application is using the audio device exclusively.
- **Tkinter Errors**:
    - On Linux, install `python3-tk` (`sudo apt install python3-tk`).
- **Permission Errors**:
    - Ensure you have write access to the directory for saving configs (`~/.neuralbeat`).

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

---

**Ægean - 2023-2026**