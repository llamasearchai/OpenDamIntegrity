"""Data models for sensor records and derived metrics."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class InclinometerRecord(BaseModel):
    timestamp: datetime
    depth_m: float
    displacement_mm: float


class PiezometerRecord(BaseModel):
    timestamp: datetime
    pressure_kpa: float


class SettlementRecord(BaseModel):
    timestamp: datetime
    settlement_mm: float


class InSARRecord(BaseModel):
    timestamp: datetime
    lat: float
    lon: float
    los_displacement_mm: float


class StabilityResult(BaseModel):
    method: str = Field("infinite_slope", description="Stability analysis method used")
    factor_of_safety: float
    risk_level: str
    details: dict | None = None
