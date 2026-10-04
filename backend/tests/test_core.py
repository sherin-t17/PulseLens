import numpy as np
from app.processing.heart_rate import estimate_heart_rate


def make_fake_ppg(bpm, fs=30, seconds=25, noise=0.3):
    """A sine wave at the heart-rate frequency + random noise + slow drift."""
    t = np.arange(0, seconds, 1 / fs)
    pulse = np.sin(2 * np.pi * (bpm / 60) * t)
    drift = 0.5 * t / seconds
    return pulse + drift + noise * np.random.randn(len(t))


def test_recovers_known_bpm():
    for true_bpm in (55, 72, 95, 130):
        result = estimate_heart_rate(make_fake_ppg(true_bpm), fs=30)
        assert abs(result["bpm"] - true_bpm) < 3


def test_pure_noise_is_poor():
    noise = np.random.randn(30 * 25)
    assert estimate_heart_rate(noise, fs=30)["quality_label"] in ("POOR", "MEDIUM")