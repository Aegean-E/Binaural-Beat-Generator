import numpy as np
import logging
from scipy.io import wavfile
import tempfile
import os

logger = logging.getLogger(__name__)

def validate_signal(audio_data, sample_rate, expected_left_hz, expected_right_hz, duration_s, tolerance_hz=0.1):
    """
    Validates the generated audio signal for scientific accuracy.

    Args:
        audio_data: Numpy array of shape (samples, 2)
        sample_rate: Sampling rate in Hz
        expected_left_hz: Expected frequency for left channel
        expected_right_hz: Expected frequency for right channel
        duration_s: Duration in seconds
        tolerance_hz: Allowed deviation in Hz (default 0.1)

    Returns:
        List of error strings. Empty if valid.
    """
    errors = []

    # 1. Duration Precision
    expected_samples = int(duration_s * sample_rate)
    # Allow off-by-one due to float math rounding in caller
    if abs(len(audio_data) - expected_samples) > 1:
        errors.append(f"Duration mismatch: Expected {expected_samples} samples, got {len(audio_data)}")

    # 2. Amplitude Safety
    max_amp = np.max(np.abs(audio_data))
    if max_amp > 1.0 + 1e-6: # Slight float tolerance
        errors.append(f"Clipping detected: Max amplitude {max_amp} > 1.0")

    if np.isnan(audio_data).any():
        errors.append("NaN values detected in audio signal")

    rms_left = np.sqrt(np.mean(audio_data[:, 0]**2))
    rms_right = np.sqrt(np.mean(audio_data[:, 1]**2))

    if rms_left < 1e-9 or rms_right < 1e-9:
        # Warning only, as silence might be intended? But usually not for a generator.
        errors.append(f"Signal is silent or near silent (RMS L={rms_left}, R={rms_right})")

    # 3. DC Offset Check
    dc_offset = np.mean(audio_data, axis=0)
    if np.any(np.abs(dc_offset) > 0.01):
        errors.append(f"DC Offset detected: {dc_offset}")

    # 4. Stereo Separation
    left = audio_data[:, 0]
    right = audio_data[:, 1]

    # Calculate correlation
    # If left and right are identical (mono), corr is 1.0.
    # If they are different (binaural), corr < 1.0.
    # If beat freq is 0, we expect 1.0.
    expected_beat = abs(expected_right_hz - expected_left_hz)

    if len(left) > 1 and len(right) > 1:
        if np.std(left) > 1e-9 and np.std(right) > 1e-9:
            correlation = np.corrcoef(left, right)[0, 1]
            if expected_beat > 0.5 and correlation > 0.999:
                 errors.append(f"Poor stereo separation for beat {expected_beat}Hz: Correlation {correlation}")
        else:
             # Already caught by silent check
             pass

    # 5. FFT Frequency Accuracy
    # Zero-pad for higher resolution
    n_samples = len(audio_data)
    n_fft = max(n_samples * 10, sample_rate) # At least 1Hz resolution if short, or 10x interp

    window = np.hanning(n_samples)

    # Analyze Left
    left_spectrum = np.fft.rfft(left * window, n=n_fft)
    freqs = np.fft.rfftfreq(n_fft, 1/sample_rate)
    left_peak_idx = np.argmax(np.abs(left_spectrum))
    left_peak_freq = freqs[left_peak_idx]

    if abs(left_peak_freq - expected_left_hz) > tolerance_hz:
        errors.append(f"Left Frequency Mismatch: Expected {expected_left_hz}Hz, Got {left_peak_freq:.4f}Hz")

    # Analyze Right
    right_spectrum = np.fft.rfft(right * window, n=n_fft)
    right_peak_idx = np.argmax(np.abs(right_spectrum))
    right_peak_freq = freqs[right_peak_idx]

    if abs(right_peak_freq - expected_right_hz) > tolerance_hz:
        errors.append(f"Right Frequency Mismatch: Expected {expected_right_hz}Hz, Got {right_peak_freq:.4f}Hz")

    # Beat Difference Check
    measured_beat = abs(right_peak_freq - left_peak_freq)
    if abs(measured_beat - expected_beat) > tolerance_hz:
        errors.append(f"Beat Frequency Mismatch: Expected {expected_beat}Hz, Measured {measured_beat:.4f}Hz")

    return errors

def validate_export(generator_class, config, duration_s):
    """
    Validates that the exported WAV file matches the in-memory generation.
    """
    errors = []
    tmp_path = None

    try:
        # 1. Generate in memory
        sample_rate = config.sample_rate
        total_samples = int(duration_s * sample_rate)

        generator = generator_class(config)
        block_size = 4096
        frames_generated = 0
        audio_blocks = []

        while frames_generated < total_samples:
            chunk = min(block_size, total_samples - frames_generated)
            block = generator.generate_block(chunk)
            audio_blocks.append(block)
            frames_generated += chunk

        memory_audio = np.concatenate(audio_blocks)

        # Apply fade out if the generator does it?
        # The app applies fade out manually in export_audio_file BEFORE writing.
        # But wait, export_audio_file logic:
        #   full_audio[-fade_len:] *= ramp
        #   wavfile.write(...)
        # The generator itself has internal fade in/out logic but 'request_stop' triggers fade out.
        # In export_audio_file, it uses generate_block loop until done, then applies manual fade out.
        # We must replicate exactly what export_audio_file does to match.

        fade_len = int(0.02 * sample_rate)
        if len(memory_audio) > fade_len:
            ramp = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
            memory_audio[-fade_len:] *= ramp[:, np.newaxis]

        # 2. Export to WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        wavfile.write(tmp_path, sample_rate, memory_audio)

        # 3. Read back
        read_rate, read_audio = wavfile.read(tmp_path)

        # 4. Compare
        if read_rate != sample_rate:
            errors.append(f"Export Sample Rate Mismatch: Expected {sample_rate}, Got {read_rate}")

        if read_audio.shape != memory_audio.shape:
             errors.append(f"Export Shape Mismatch: Expected {memory_audio.shape}, Got {read_audio.shape}")

        # Normalize read audio to -1.0 to 1.0 if it's int
        # wavfile.read returns float32 if written as float32.
        # But let's check dtype.

        if np.allclose(memory_audio, read_audio, atol=1e-4):
             pass
        else:
             max_diff = np.max(np.abs(memory_audio - read_audio))
             errors.append(f"Export Content Mismatch: Max diff {max_diff}")

    except Exception as e:
        errors.append(f"Export Exception: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return errors
