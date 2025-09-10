"""Sensor ingestion helpers for OpenDamIntegry."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _read_csv(path: str | Path, parse_dates: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in parse_dates:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True)
    return df


def read_inclinometers(path: str | Path) -> pd.DataFrame:
    """Read inclinometer CSV with columns: timestamp, depth_m, displacement_mm"""
    return _read_csv(path, ["timestamp"])


def read_piezometers(path: str | Path) -> pd.DataFrame:
    """Read piezometer CSV with columns: timestamp, pressure_kpa"""
    return _read_csv(path, ["timestamp"])


def read_settlement(path: str | Path) -> pd.DataFrame:
    """Read settlement plates CSV with columns: timestamp, settlement_mm"""
    return _read_csv(path, ["timestamp"])
