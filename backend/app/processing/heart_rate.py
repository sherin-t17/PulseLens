"""
The full pipeline in one place. This is the file to explain in your viva:

video -> green signal -> detrend -> band-pass -> FFT -> dominant frequency -> BPM
"""

import numpy as np

from app.processing.video_processing import extract_green_signal
from app.processing.signal_processing import (
    detrend_signal, bandpass_filter, compute_spectrum,
    find_dominant_frequency, signal_quality, LOW_HZ, HIGH_HZ,
)
from app.utils.errors import PulseLensError

MIN_SECONDS = 10       # shorter videos give too coarse a frequency resolution
SKIP_SECONDS = 2
# camera auto-exposure is unstable at the start
POOR_MESSAGE = "Unable to obtain a reliable estimate. Please record again with your finger steady."


def interpret(bpm, quality_label):
    """Informational text only. This is NOT a diagnosis."""
    if quality_label == "POOR" or bpm is None:
        return ("The signal quality is too low for a reliable estimate. "
                "Please keep your finger steady and try again.")
    if bpm < 60:
        return ("Your estimated heart rate is below the typical resting range. "
                "Consider resting and measuring again.")
    if bpm > 100:
        return ("Your estimated heart rate is above the typical resting range. "
                "Consider resting and measuring again.")
    return "Your estimated heart rate is within the expected resting range."


def estimate_heart_rate(fs_signal, fs, low=LOW_HZ, high=HIGH_HZ):
    """
    Core math on an already-extracted signal (no video needed).
    Separate from video reading so it is easy to test and reuse
    (e.g. by a future real-time mobile version).
    """
    x = detrend_signal(fs_signal)
    filtered = bandpass_filter(x, fs, low, high)
    freqs, power = compute_spectrum(filtered, fs)
    dominant_hz = find_dominant_frequency(freqs, power, low, high)
    score, label = signal_quality(freqs, power, dominant_hz, low, high)
    bpm = dominant_hz * 60.0  # <-- the conversion: Hz -> beats per minute
    return {
        "bpm": round(bpm, 1),
        "dominant_frequency_hz": round(dominant_hz, 4),
        "quality_score": round(score, 3),
        "quality_label": label,
        "filtered_signal": filtered,
        "freqs": freqs,
        "power": power,
    }


def analyze_video(video_path, channel="green"):
    """Full analysis of a video file. Returns a dict ready for the API."""
    signal, fps, mean_bgr = extract_green_signal(video_path, channel=channel)

    # Was a finger really covering the lens? With flash on, the frame should be
    # bright and red-dominant.
    b, g, r = mean_bgr
    if not (r > g and r > b and r > 60):
        raise PulseLensError(
            "A fingertip covering the camera was not detected. "
            "Cover the lens fully with the flash on and record again."
        )

    # Drop the unstable first seconds
    signal = signal[int(SKIP_SECONDS * fps):]
    duration = len(signal) / fps
    if duration < MIN_SECONDS:
        raise PulseLensError(
            f"The video is too short ({duration:.0f}s usable). Record at least "
            f"{MIN_SECONDS + SKIP_SECONDS} seconds, ideally 20-30."
        )

    result = estimate_heart_rate(signal, fps)
    result["duration_seconds"] = round(duration + SKIP_SECONDS, 1)
    result["fps"] = round(fps, 2)
    result["time_axis"] = np.arange(len(result["filtered_signal"])) / fps

    if result["quality_label"] == "POOR":
        result["bpm"] = None  # don't return a misleading number
        result["message"] = POOR_MESSAGE
    else:
        result["message"] = None
    result["interpretation"] = interpret(result["bpm"], result["quality_label"])
    return result