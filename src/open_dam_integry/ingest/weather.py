"""Weather data ingestion using Open-Meteo API (no API key required)."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

import pandas as pd
import requests


def fetch_precipitation_series(
    latitude: float,
    longitude: float,
    start: datetime,
    end: datetime,
) -> pd.DataFrame:
    """Fetch hourly precipitation from Open-Meteo archive API as a DataFrame.

    Returns a DataFrame with columns: time (UTC), precipitation
    """
    base = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "hourly": "precipitation",
        "timezone": "UTC",
    }
    resp = requests.get(base, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    times: Iterable[str] = data.get("hourly", {}).get("time", [])
    prec: Iterable[float] = data.get("hourly", {}).get("precipitation", [])
    df = pd.DataFrame({"time": pd.to_datetime(list(times), utc=True), "precipitation": list(prec)})
    return df

