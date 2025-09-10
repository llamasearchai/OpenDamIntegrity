"""Stability computations for slopes and embankments.

Implements an infinite slope factor-of-safety method suitable for real-time assessment.
Units: c in kPa, unit weight gamma in kN/m^3, height z in m, angles in degrees.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from ..config import Thresholds


@dataclass
class InfiniteSlopeParams:
    cohesion_kpa: float
    phi_deg: float
    beta_deg: float
    height_m: float
    unit_weight_kN_m3: float
    ru: float = 0.0  # pore pressure ratio (u / sigma_n)


def factor_of_safety_infinite_slope(p: InfiniteSlopeParams) -> float:
    """Compute factor of safety for an infinite slope with seepage parallel to slope.

    FS = (c' + (γ * z * cos^2β * (1 - ru)) * tanφ) / (γ * z * sinβ * cosβ)
    """
    phi = math.radians(p.phi_deg)
    beta = math.radians(p.beta_deg)
    gamma_z = p.unit_weight_kN_m3 * p.height_m  # kPa
    numerator = p.cohesion_kpa + (gamma_z * (math.cos(beta) ** 2) * (1.0 - p.ru)) * math.tan(phi)
    denominator = gamma_z * math.sin(beta) * math.cos(beta)
    if denominator == 0.0:
        return float("inf")
    return numerator / denominator


def risk_level_from_fs(fs: float, t: Thresholds) -> str:
    """Map factor-of-safety to a risk level using configured thresholds."""
    if fs >= t.normal_fs_min:
        return "NORMAL"
    if fs >= t.watch_fs_min:
        return "WATCH"
    if fs >= t.warning_fs_min:
        return "WARNING"
    if fs >= t.alert_fs_min:
        return "ALERT"
    return "EMERGENCY"

