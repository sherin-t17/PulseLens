"""
Signal-processing building blocks. Each function does ONE job.

Vocabulary:
- Sampling rate (fs): how many values per second we have. Video at 30 FPS -> 30 Hz.
- Frequency (Hz): repeats per second. A heart beating 72 times per minute
  beats 72 / 60 = 1.2 times per second = 1.2 Hz.
- BPM = frequency (Hz) * 60.
"""

import numpy as np
from scipy.signal import butter, filtfilt, detrend

from app.utils.errors import PulseLensError

LOW_HZ = 0.7    # 0.7 * 60 =  42 BPM
HIGH_HZ = 4.0   # 4.0 * 60 = 240 BPM


def detrend_signal(signal):
    """
    Remove slow drift (e.g. brightness slowly changing as your finger presses
    harder). We subtract the best straight line, then normalize so the signal
    has mean 0 and standard deviation 1.
    """
    x = detrend(np.asarray(signal, dtype=float), type="linear")
    std = x.std()
    if std < 1e-9:
        raise PulseLensError(
            "No variation was found in the video. Make sure your finger fully covers the camera."
        )
    return (x - x.mean()) / std


def bandpass_filter(signal, fs, low=LOW_HZ, high=HIGH_HZ, order=4):
    """
    Keep only frequencies between `low` and `high` Hz (plausible heart rates),
    remove everything else (slow drift, fast noise).

    Butterworth = a filter with a smooth, flat response inside the band.
    filtfilt    = runs the filter forwards and backwards so the signal is not
                  shifted in time (zero phase distortion).
    """
    nyquist = fs / 2.0  # highest frequency we can represent at this sampling rate
    if high >= nyquist:
        raise PulseLensError("The video frame rate is too low to analyze heart rate.")

    try:
        b, a = butter(order, [low / nyquist, high / nyquist], btype="band")
        # filtfilt needs the signal to be longer than its "padding" length
        if len(signal) <= 3 * max(len(a), len(b)):
            raise PulseLensError("The video is too short to filter.")
        return filtfilt(b, a, signal)
    except PulseLensError:
        raise
    except Exception:
        raise PulseLensError("Filtering failed. Please try another video.")


def compute_spectrum(signal, fs, zero_pad_factor=8):
    """
    FFT (Fast Fourier Transform): splits a signal into the frequencies it is
    made of, and tells us how strong each frequency is.

    A pulse repeating ~1.2 times per second shows up as a tall peak at 1.2 Hz.

    We multiply by a Hann window first (reduces "leakage" at the edges) and
    zero-pad (add zeros at the end) so the spectrum has finer frequency steps,
    which makes the peak easier to locate.

    Returns: frequencies (Hz), power (magnitude squared)
    """
    n = len(signal)
    n_fft = int(2 ** np.ceil(np.log2(n * zero_pad_factor)))
    windowed = signal * np.hanning(n)
    try:
        spectrum = np.fft.rfft(windowed, n=n_fft)
    except Exception:
        raise PulseLensError("Frequency analysis (FFT) failed.")
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / fs)
    power = np.abs(spectrum) ** 2
    return freqs, power


def find_dominant_frequency(freqs, power, low=LOW_HZ, high=HIGH_HZ):
    """Strongest frequency inside the heart-rate band only."""
    band = (freqs >= low) & (freqs <= high)
    if not band.any():
        raise PulseLensError("No valid frequency range found.")
    band_freqs, band_power = freqs[band], power[band]
    peak_index = int(np.argmax(band_power))
    return float(band_freqs[peak_index])


def signal_quality(freqs, power, dominant_hz, low=LOW_HZ, high=HIGH_HZ, half_width=0.15):
    """
    Simple, NOT clinically validated, quality score between 0 and 1.

    Idea: a clean pulse puts most of its energy in ONE narrow peak.
    A noisy signal spreads energy across many frequencies.

        score = energy near the peak (+/- 0.15 Hz) / total energy in the band

    Rough labels (tunable numbers; these are starting guesses, tune them
    with your own recordings):
        >= 0.35 GOOD,  >= 0.20 MEDIUM,  otherwise POOR
    """
    band = (freqs >= low) & (freqs <= high)
    near_peak = (freqs >= dominant_hz - half_width) & (freqs <= dominant_hz + half_width)
    total = power[band].sum()
    if total <= 0:
        return 0.0, "POOR"
    score = float(power[near_peak & band].sum() / total)

    if score >= 0.35:
        label = "GOOD"
    elif score >= 0.20:
        label = "MEDIUM"
    else:
        label = "POOR"
    return score, label