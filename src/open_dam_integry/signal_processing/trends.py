"""Trend analysis utilities."""
from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np
from scipy.stats import linregress


def linear_trend(x: Iterable[float]) -> Tuple[float, float]:
    """Return slope and p-value for a simple linear trend (index vs values)."""
    y = np.asarray(list(x), dtype=float)
    x_idx = np.arange(len(y))
    res = linregress(x_idx, y)
    return float(res.slope), float(res.pvalue)


def detect_threshold_crossings(x: Iterable[float], threshold: float, direction: str = "above") -> np.ndarray:
    """Return indices where series crosses a threshold in the given direction (above/below)."""
    y = np.asarray(list(x), dtype=float)
    if direction == "above":
        return np.where((y[1:] >= threshold) & (y[:-1] < threshold))[0] + 1
    else:
        return np.where((y[1:] <= threshold) & (y[:-1] > threshold))[0] + 1
