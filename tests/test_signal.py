import numpy as np

from open_dam_integry.signal_processing.filters import butter_lowpass_filter


def test_butter_lowpass_reduces_noise():
    fs_hz = 50.0
    t = np.arange(0, 2, 1 / fs_hz)
    clean = np.sin(2 * np.pi * 1.0 * t)
    noise = 0.5 * np.random.RandomState(0).normal(size=t.size)
    x = clean + noise
    y = butter_lowpass_filter(x, cutoff_hz=5.0, fs_hz=fs_hz, order=4)
    # Filtered signal should have lower std than noisy signal
    assert y.std() < x.std()
