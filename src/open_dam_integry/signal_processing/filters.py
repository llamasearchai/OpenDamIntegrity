"""Signal processing functions: filtering and denoising."""
from __future__ import annotations

from typing import Iterable

import numpy as np
from scipy import signal

try:
    import pywt  # type: ignore
except Exception:  # pragma: no cover - optional
    pywt = None  # type: ignore


def butter_lowpass_filter(x: Iterable[float], cutoff_hz: float, fs_hz: float, order: int = 4) -> np.ndarray:
    """Zero-phase Butterworth low-pass filter using filtfilt."""
    x_arr = np.asarray(list(x), dtype=float)
    nyq = 0.5 * fs_hz
    normal_cutoff = cutoff_hz / nyq
    b, a = signal.butter(order, normal_cutoff, btype="low", analog=False)
    y = signal.filtfilt(b, a, x_arr)
    return y


def wavelet_denoise(x: Iterable[float], wavelet: str = "db4", level: int = 1) -> np.ndarray:
    """Wavelet denoising with soft threshold. Falls back to Savitzky-Golay if PyWavelets is unavailable."""
    arr = np.asarray(list(x), dtype=float)
    if pywt is None:
        # Savitzky-Golay fallback
        window = min(len(arr) - (1 - len(arr) % 2), 11)
        if window < 5:
            return arr
        return signal.savgol_filter(arr, window_length=window, polyorder=2)
    coeffs = pywt.wavedec(arr, wavelet, mode="periodization")
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745 if len(coeffs[-1]) else 0.0
    uthresh = sigma * np.sqrt(2 * np.log(len(arr))) if len(arr) else 0.0
    denoised = [coeffs[0]]
    for c in coeffs[1:]:
        denoised.append(pywt.threshold(c, value=uthresh, mode="soft"))
    return pywt.waverec(denoised, wavelet, mode="periodization")

