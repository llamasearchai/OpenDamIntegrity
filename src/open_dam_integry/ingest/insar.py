"""InSAR (non-raster) ingestion helpers for OpenDamIntegry.

This module expects CSV with columns: timestamp, lat, lon, los_displacement_mm
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd


def read_insar_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["timestamp"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True)
    return df

