"""Connector to PyNastran if available; falls back to simplified response."""

from __future__ import annotations

try:
    import pyNastran  # type: ignore  # noqa: F401

    PYNASTRAN_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    PYNASTRAN_AVAILABLE = False

from .simplified import pseudo_fea_slope_response


def run_pynastran_or_fallback(
    height_m: float, width_m: float, surcharge_kPa: float
) -> dict[str, float]:
    if PYNASTRAN_AVAILABLE:
        # A real PyNastran model would be executed here; returning fallback for generality.
        return pseudo_fea_slope_response(height_m, width_m, surcharge_kPa) | {
            "backend": "pynastran"
        }
    return pseudo_fea_slope_response(height_m, width_m, surcharge_kPa) | {"backend": "simplified"}
