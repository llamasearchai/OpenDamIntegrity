"""Simplified elastic response estimates and connectors for FEA backends."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ElasticParams:
    E_kPa: float  # Young's modulus in kPa
    nu: float  # Poisson's ratio
    plane_strain: bool = True


def plane_strain_stiffness_matrix(E_kPa: float, nu: float) -> np.ndarray:
    coef = E_kPa / ((1 + nu) * (1 - 2 * nu))
    C = coef * np.array(
        [
            [1 - nu, nu, 0],
            [nu, 1 - nu, 0],
            [0, 0, (1 - 2 * nu) / 2],
        ]
    )
    return C


def estimate_strain_from_stress(stress_vec: np.ndarray, params: ElasticParams) -> np.ndarray:
    """Given [σxx, σyy, τxy] (kPa), estimate [εxx, εyy, γxy]."""
    C = plane_strain_stiffness_matrix(params.E_kPa, params.nu)
    strain = np.linalg.solve(C, stress_vec)
    return strain


def pseudo_fea_slope_response(
    height_m: float, width_m: float, surcharge_kPa: float
) -> dict[str, float]:
    """Toy response: estimate near-surface stress increase and a proxy displacement.

    This is a fast closed-form approximation used when a full FEA backend is unavailable.
    """
    # area not required for this simplified proxy; keep computation minimal
    avg_stress = surcharge_kPa  # simplistic: uniform surcharge
    E_kPa = 5e5  # nominal stiffness (kPa)
    nu = 0.3
    params = ElasticParams(E_kPa=E_kPa, nu=nu)
    stress = np.array([avg_stress, avg_stress / 2, 0.0])
    strain = estimate_strain_from_stress(stress, params)
    # Proxy vertical displacement scale
    disp_mm = float(strain[1] * height_m * 1000.0)
    return {
        "avg_stress_kpa": float(avg_stress),
        "proxy_vertical_disp_mm": disp_mm,
    }
